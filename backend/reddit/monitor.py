import os
print("DEBUG: reddit/monitor.py is starting...")
import time
import praw
from dotenv import load_dotenv
from pathlib import Path
import sys

# Add backend directory to path
# Current file: backend/reddit/monitor.py
# Backend dir: backend/
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from main.claim_extractor import ClaimExtractor
from main.claim_discoverer import ClaimDiscoverer
from main.reasoning import ClaimReasoner
from main.headline import HeadlineGenerator
from database.supabase_client import SupabaseClient

# Load env
# .env is in project root (parent of backend)
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Debug: Check if keys are loaded
print(f"Loading .env from: {env_path}")
print(f"YOUR_CLIENT_ID found: {bool(os.getenv('YOUR_CLIENT_ID'))}")


class RedditMonitor:
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=os.getenv("YOUR_CLIENT_ID"),
            client_secret=os.getenv("YOUR_CLIENT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT", "TruthLens/1.0"),
            username=os.getenv("YOUR_USERNAME"),
            password=os.getenv("YOUR_PASSWORD")
        )
        self.subreddit_name = "eyeoftruth"
        self.db = SupabaseClient()
        self.extractor = ClaimExtractor(max_tokens_per_chunk=15000)
        self.discoverer = ClaimDiscoverer()
        self.reasoner = ClaimReasoner()
        self.headline_generator = HeadlineGenerator()

    def process_posts(self):
        try:
            print(f"Successfully logged in as: {self.reddit.user.me()}")
        except Exception as e:
            print(f"Failed to get logged in user: {e}")

        print(f"Monitoring r/{self.subreddit_name}...")
        subreddit = self.reddit.subreddit(self.subreddit_name)
        
        # Process last 5 posts first (to catch up)
        print("Checking last 5 posts...")
        try:
            for post in subreddit.new(limit=5):
                try:
                    self.handle_post(post)
                except Exception as e:
                    print(f"Error processing historical post {post.id}: {e}")
        except Exception as e:
            print(f"Error fetching recent posts: {e}")

        print("Streaming new posts...")
        # Process new posts
        for post in subreddit.stream.submissions(skip_existing=True):
            try:
                self.handle_post(post)
            except Exception as e:
                print(f"Error processing post {post.id}: {e}")

    def handle_post(self, post):
        print(f"New post: {post.title}")
        
        # Check if already processed
        if self.db.check_reddit_post_exists(post.id):
            print("Post already processed.")
            return

        # Content to verify
        content_to_verify = f"{post.title}\n\n{post.selftext}"
        input_type = "text"
        
        # If URL exists and it's not a self-post
        if not post.is_self and post.url:
            content_to_verify = post.url
            input_type = "url"
            print(f"Processing URL: {post.url}")

        # Verify
        print("Verifying content...")
        print(f"Content preview: {content_to_verify[:200]}...")
        
        # 1. Extract Claims (with retry)
        claims = []
        for attempt in range(3):
            try:
                if input_type == "url":
                    claims_data = self.extractor.extract_claims_from_url(content_to_verify, key_name="user")
                else:
                    claims_data = self.extractor.extract_claims(content_to_verify, key_name="user")
                
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
            self.db.save_reddit_post(
                reddit_id=post.id,
                title=post.title,
                body=post.selftext,
                url=post.url if not post.is_self else None,
                headline=None,
                verdict=False,  # Default to False if no claims
                reasoning="No claims could be extracted from this content.",
                claims=[],
                sources={},
                author=str(post.author),
                subreddit=self.subreddit_name
            )
            print("Post saved with no claims.")
            return

        # 2. Discover Sources
        sources = self.discoverer.discover_sources(claims)
        
        # 3. Reason
        verdict_data = self.reasoner.reason_all_claims(claims, sources)
        verdict = verdict_data["verdict"]
        reasoning = verdict_data["reasoning"]

        print(f"Verdict: {verdict}")

        # 4. Generate Headline
        print("Generating headline...")
        headline = self.headline_generator.generate_headline(claims)
        print(f"Headline: {headline}")

        # Save to DB
        self.db.save_reddit_post(
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
                self.db.mark_reddit_post_removed(post.id)
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
