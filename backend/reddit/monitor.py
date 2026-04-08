import sys
import time
import praw
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from config import settings
from main.claim_extractor import ClaimExtractor
from main.claim_discoverer import ClaimDiscoverer
from main.reasoning import ClaimReasoner
from main.headline import HeadlineGenerator
from main.summarizer import Summarizer
from main.rewriter import ClaimRewriter
from database.supabase_client import SupabaseClient


class RedditMonitor:
    """
    IMPACT TRACE:
      Entry point: run.py (subprocess), api/main.py (startup thread)
      Depends on: settings.REDDIT_*, ClaimExtractor, ClaimDiscoverer,
                  ClaimReasoner, HeadlineGenerator, SupabaseClient
      If changed: affects auto-moderation of r/eyeoftruth and community_archives
    """

    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=settings.REDDIT_CLIENT_ID,
            client_secret=settings.REDDIT_CLIENT_SECRET,
            user_agent=settings.REDDIT_USER_AGENT,
            username=settings.REDDIT_USERNAME,
            password=settings.REDDIT_PASSWORD
        )
        self.subreddit_name = "eyeoftruth"
        # NOTE: db, extractor, reasoner etc are NOT stored as instance fields.
        # handle_post() creates fresh instances per call so concurrent threads
        # never share mutable LangChain / Supabase state.

    def process_posts(self):
        try:
            print(f"Successfully logged in as: {self.reddit.user.me()}")
        except Exception as e:
            print(f"Failed to get logged in user: {e}")

        print(f"Monitoring r/{self.subreddit_name}...")
        subreddit = self.reddit.subreddit(self.subreddit_name)

        # Track which post IDs are already in-flight so we never double-submit
        in_flight: set = set()

        def _safe_handle(post):
            try:
                self.handle_post(post)
            except Exception as e:
                print(f"Error processing post {post.id}: {e}")
            finally:
                in_flight.discard(post.id)

        # Up to 4 posts verified in parallel — keeps the pipeline saturated
        # without hammering the OpenAI / Tavily rate limits too hard.
        executor = ThreadPoolExecutor(max_workers=4)

        # Process last 5 posts first (to catch up)
        print("Checking last 5 posts...")
        try:
            catchup_posts = list(subreddit.new(limit=5))
            futures = []
            for post in catchup_posts:
                if post.id not in in_flight:
                    in_flight.add(post.id)
                    futures.append(executor.submit(_safe_handle, post))
            # Wait for catchup to finish before streaming
            for f in as_completed(futures):
                pass
        except Exception as e:
            print(f"Error fetching recent posts: {e}")

        print("Streaming new posts...")
        for post in subreddit.stream.submissions(skip_existing=True):
            if post.id not in in_flight:
                in_flight.add(post.id)
                executor.submit(_safe_handle, post)

    def handle_post(self, post):
        print(f"New post: {post.title}")

        # Fresh instances per call — thread-safe (no shared mutable state)
        db = SupabaseClient()
        extractor = ClaimExtractor(max_tokens_per_chunk=15000)
        discoverer = ClaimDiscoverer()
        reasoner = ClaimReasoner()
        headline_generator = HeadlineGenerator()
        summarizer = Summarizer()
        rewriter = ClaimRewriter()

        # Check if already processed
        if db.check_reddit_post_exists(post.id):
            print("Post already processed.")
            return

        # Determine content and input type
        # Priority: external link post > URL in body > plain text
        import re
        content_to_verify = f"{post.title}\n\n{post.selftext}"
        input_type = "text"

        if not post.is_self and post.url and not post.url.startswith("https://www.reddit.com"):
            # Link post pointing to an external URL
            content_to_verify = post.url
            input_type = "url"
            print(f"Processing link post URL: {post.url}")
        elif post.selftext:
            # Check if body contains a URL
            url_match = re.search(r'https?://[^\s\)\"\']+', post.selftext)
            if url_match:
                body_url = url_match.group(0)
                if not body_url.startswith("https://www.reddit.com"):
                    content_to_verify = body_url
                    input_type = "url"
                    print(f"Processing URL found in post body: {body_url}")

        # Verify
        print("Verifying content...")
        print(f"Content preview: {content_to_verify[:200]}...")
        
        # 1. Extract Claims (with retry)
        claims = []
        claims_data: dict = {}
        for attempt in range(3):
            try:
                if input_type == "url":
                    claims_data = extractor.extract_claims_from_url(content_to_verify, key_name="user")
                else:
                    claims_data = extractor.extract_claims(content_to_verify, key_name="user")

                claims = claims_data.get("user", [])
                if claims:
                    print(f"Successfully extracted {len(claims)} claims")
                    break
                else:
                    print(f"Attempt {attempt + 1}: No claims extracted, retrying...")
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < 2:
                    import time
                    time.sleep(2)
            
        if not claims:
            print("No claims found. Saving with empty claims...")
            # Still save to DB with empty claims
            db.save_reddit_post(
                reddit_id=post.id,
                title=post.title,
                body=post.selftext,
                url=post.url if not post.is_self else None,
                headline=None,
                verdict=False,
                reasoning="No claims could be extracted from this content.",
                claims=[],
                sources={},
                author=str(post.author),
                subreddit=self.subreddit_name
            )
            print("Post saved with no claims.")
            return

        # 2. Summarise + rewrite claims into search queries
        raw_text = claims_data.get("raw_text", content_to_verify)
        document_summary = summarizer.summarise(raw_text)
        rewritten = rewriter.rewrite_claims(document_summary, claims)

        # 3. Discover sources via rewritten queries
        sources = discoverer.discover_sources_from_queries(rewritten)

        # 4. Scrape sources and extract website claims
        all_urls = list(set(u for urls in sources.values() for u in urls))
        all_urls = all_urls[:settings.TAVILY_MAX_URLS]  # capped to 2 in test mode
        if all_urls:
            website_claims = extractor.extract_website_claims(all_urls, claims)
            website_claims_flat = {url: c for url, c in website_claims.items() if c}
        else:
            website_claims_flat = {}

        # 5. Reason
        verdict_data = reasoner.reason_all_claims(claims, website_claims_flat or sources, original_text=raw_text)
        verdict = verdict_data["verdict"]
        reasoning = verdict_data["reasoning"]

        print(f"Verdict: {verdict}")

        # 6. Generate Headline
        print("Generating headline...")
        headline = headline_generator.generate_headline(claims)
        print(f"Headline: {headline}")

        # Save to DB
        db.save_reddit_post(
            reddit_id=post.id,
            title=post.title,
            body=post.selftext,
            url=post.url if not post.is_self else None,
            headline=headline,
            verdict=verdict,
            reasoning=reasoning,
            claims=claims,
            sources=sources,
            author=str(post.author),
            subreddit=self.subreddit_name
        )

        # Moderation
        if not verdict: # False
            print("Verdict is FALSE. Removing post...")
            try:
                post.mod.remove()
                post.mod.send_removal_message("Your post has been removed because it was verified as misinformation by Truth Lens AI.")
                db.mark_reddit_post_removed(post.id)
                print("Post removed successfully.")
            except Exception as e:
                print(f"Failed to remove post: {e}")
        else:
            # True - Approve the post
            print("Verdict is TRUE. Approving post...")
            try:
                post.mod.approve()
                print("Post approved.")
            except Exception as e:
                print(f"Failed to approve post: {e}")

if __name__ == "__main__":
    monitor = RedditMonitor()
    monitor.process_posts()
