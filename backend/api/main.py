from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from main.claim_extractor import ClaimExtractor
from main.claim_discoverer import ClaimDiscoverer
from main.reasoning import ClaimReasoner
from main.headline.generator import HeadlineGenerator
from main.categorizer import ClaimCategorizer
from database.supabase_client import SupabaseClient
from reddit.monitor import RedditMonitor
from image_retrieve.image_searcher import ImageSearcher
import threading
import asyncio

app = FastAPI(title="Misinformation Detection API")

# Background task for Reddit Monitor
def run_reddit_monitor():
    print("Starting Reddit Monitor in background thread...")
    try:
        monitor = RedditMonitor()
        monitor.process_posts()
    except Exception as e:
        print(f"Reddit Monitor failed: {e}")

@app.on_event("startup")
async def startup_event():
    # Start Reddit monitor in a separate thread so it doesn't block FastAPI
    monitor_thread = threading.Thread(target=run_reddit_monitor, daemon=True)
    monitor_thread.start()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class VerifyRequest(BaseModel):
    input_type: str  # "text" or "url"
    content: str
    user_id: Optional[str] = "0"
    user_email: Optional[str] = "user0@gmail.com"
    reddit_id: Optional[str] = None
    subreddit: Optional[str] = None


class VerifyResponse(BaseModel):
    verification_id: str
    verdict: bool
    reasoning: str
    claims: List[str]
    sources: Dict[str, List[str]]
    website_claims: Dict[str, List[str]]


class HistoryResponse(BaseModel):
    id: str
    user_id: str
    user_email: str
    input_content: str
    input_type: str
    verdict: bool
    reasoning: str
    claims: List[str]
    sources: Optional[Dict[str, List[str]]] = None
    is_public: bool
    created_at: str
    upvotes: int = 0
    downvotes: int = 0
    headline: Optional[str] = None
    category: Optional[str] = None
    image_url: Optional[str] = None


class RedditPost(BaseModel):
    id: str
    reddit_id: str
    title: str
    body: Optional[str]
    url: Optional[str]
    headline: Optional[str]
    verdict: bool
    reasoning: str
    claims: List[str]
    sources: Optional[Dict[str, List[str]]] = None
    author: Optional[str]
    subreddit: str
    created_at: str
    upvotes: int = 0
    downvotes: int = 0
    image_url: Optional[str] = None


@app.get("/api/reddit-posts", response_model=List[RedditPost])
async def get_reddit_posts(limit: int = 50):
    """Get verified Reddit posts."""
    try:
        db = SupabaseClient()
        posts = db.get_reddit_posts(limit=limit)
        return posts
    except Exception as e:
        print(f"Error fetching Reddit posts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/reddit-community")
async def get_community_reddit(subreddit: str, limit: int = 10):
    """Fetch posts from any subreddit."""
    try:
        from reddit.feed_retriever import FeedRetriever
        
        retriever = FeedRetriever()
        posts = retriever.get_subreddit_posts(subreddit, limit=limit)
        return posts
    except Exception as e:
        print(f"Error fetching community Reddit: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch subreddit: {str(e)}")


@app.get("/")
async def root():
    return {"message": "Truth Lens API", "status": "running", "version": "1.0.0"}


@app.get("/test")
async def test():
    """Simple test endpoint to verify API is working."""
    return {"status": "ok", "message": "API is working!"}


@app.post("/api/verify", response_model=VerifyResponse)
async def verify_content(request: VerifyRequest):
    """
    Verify content (text or URL) for misinformation.
    """
    try:
        print(f"\n{'='*70}")
        print(f"Processing {request.input_type}: {request.content[:100]}...")
        print(f"{'='*70}\n")

        # Step 1: Extract claims
        extractor = ClaimExtractor(max_tokens_per_chunk=15000)

        if request.input_type == "url":
            result = extractor.extract_claims_from_url(request.content, key_name="user")
        else:
            result = extractor.extract_claims(request.content, key_name="user")

        if not result["user"]:
            raise HTTPException(
                status_code=400, detail="No claims could be extracted from the content"
            )

        print(f"Extracted {len(result['user'])} claims")

        # Step 2: Discover sources
        discoverer = ClaimDiscoverer()
        sources = discoverer.discover_sources(result["user"])

        total_links = sum(len(links) for links in sources.values())
        print(f"Discovered {total_links} sources")

        # Step 3: Extract website claims
        all_urls = []
        for urls in sources.values():
            all_urls.extend(urls)
        all_urls = list(set(all_urls))

        if not all_urls:
            raise HTTPException(
                status_code=400,
                detail="No sources discovered. Please check your Tavily API key."
            )
        
        website_claims = extractor.extract_website_claims(all_urls, result["user"])

        # Flatten website claims for response
        all_website_claims_flat = {}
        for url, claims in website_claims.items():
            if claims:
                all_website_claims_flat[url] = claims

        print(f"Extracted claims from {len(all_website_claims_flat)} websites")

        # Step 4: Reasoning
        if not all_website_claims_flat:
            raise HTTPException(
                status_code=400,
                detail="No credible sources found for verification. Please check your API keys and try again."
            )
        
        reasoner = ClaimReasoner()
        final_result = reasoner.reason_all_claims(result["user"], all_website_claims_flat)
        print(f"Final verdict: {final_result['verdict']}")

        # Save to Supabase
        db = SupabaseClient()
        saved_record = db.save_verification(
            user_id=request.user_id,
            user_email=request.user_email,
            input_content=request.content,
            input_type=request.input_type,
            verdict=final_result["verdict"],
            reasoning=final_result["reasoning"],
            claims=result["user"],
            sources=sources,
        )
        verification_id = saved_record.get("id", "")
        print(f"Saved to Supabase with ID: {verification_id}")

        # Save to Community Archive if reddit_id is present
        if request.reddit_id and request.subreddit:
            print(f"Saving to Community Archive: {request.subreddit} - {request.reddit_id}")
            
            # Generate headline for archive
            headline = None
            try:
                from main.headline.generator import HeadlineGenerator
                headline_gen = HeadlineGenerator()
                headline = headline_gen.generate_headline(result["user"])
            except Exception as e:
                print(f"Error generating headline for archive: {e}")
                headline = request.content[:100] + "..."

            # Try to get image
            image_url = None
            try:
                searcher = ImageSearcher()
                image_url = searcher.get_image_for_claims(result["user"])
            except Exception as e:
                print(f"Error fetching image for archive: {e}")

            db.save_community_archive(
                reddit_id=request.reddit_id,
                title=headline or request.content[:100],
                body=request.content,
                subreddit=request.subreddit,
                verdict=final_result["verdict"],
                reasoning=final_result["reasoning"],
                claims=result["user"],
                sources=sources,
                image_url=image_url
            )

        return VerifyResponse(
            verification_id=verification_id,
            verdict=final_result["verdict"],
            reasoning=final_result["reasoning"],
            claims=result["user"],
            sources=sources,
            website_claims=all_website_claims_flat,
        )

    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/api/history/{user_id}", response_model=List[HistoryResponse])
async def get_history(user_id: str, limit: int = 50):
    """
    Get verification history for a user.
    """
    try:
        db = SupabaseClient()
        history = db.get_user_history(user_id, limit)
        return history
    except Exception as e:
        print(f"Error fetching history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/public-feed", response_model=List[HistoryResponse])
async def get_public_feed(limit: int = 20):
    """
    Get public verifications for the homepage feed.
    """
    try:
        db = SupabaseClient()
        feed = db.get_public_feed(limit)
        return feed
    except Exception as e:
        print(f"Error fetching public feed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/toggle-public/{verification_id}")
async def toggle_public_status(verification_id: str, is_public: bool):
    try:
        db = SupabaseClient()
        headline = None
        category = None
        image_url = None
        
        if is_public:
            # Check if we need to generate a headline, category, or image
            verification = db.get_verification_by_id(verification_id)
            if verification:
                claims = verification.get("claims", [])
                
                # If headline is missing, generate it
                if not verification.get("headline"):
                    print(f"Generating headline for {verification_id}...")
                    try:
                        generator = HeadlineGenerator()
                        # Use claims if available, else input content
                        if not claims and verification.get("input_content"):
                            claims = [verification.get("input_content")]
                        
                        if claims:
                            headline = generator.generate_headline(claims)
                            print(f"Generated headline: {headline}")
                    except Exception as e:
                        print(f"Error generating headline: {e}")
                else:
                    headline = verification.get("headline")
                
                # Generate category from claims
                if not verification.get("category"):
                    if claims:
                        print(f"Categorizing claims for {verification_id}...")
                        try:
                            categorizer = ClaimCategorizer()
                            category = categorizer.categorize_claims(claims)
                            print(f"Category: {category}")
                        except Exception as e:
                            print(f"Error categorizing claims: {e}")
                            category = "technology"  # Default fallback
                else:
                    category = verification.get("category")

                # Generate image if missing
                if not verification.get("image_url"):
                    print(f"Searching for image for {verification_id}...")
                    try:
                        searcher = ImageSearcher()
                        if claims:
                            image_url = searcher.get_image_for_claims(claims)
                        elif verification.get("input_content"):
                             image_url = searcher.search_image(verification.get("input_content")[:200])
                        
                        print(f"Found image: {image_url}")
                    except Exception as e:
                        print(f"Error searching for image: {e}")
                else:
                    image_url = verification.get("image_url")

        result = db.toggle_public_status(verification_id, is_public, headline, category, image_url)
        return {"success": result, "headline": headline, "category": category, "image_url": image_url}
    except Exception as e:
        print(f"Error toggling public status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class VoteRequest(BaseModel):
    verification_id: str
    user_id: str
    vote_type: int  # 1 or -1


@app.post("/api/vote")
async def vote(request: VoteRequest):
    """
    Vote on a verification.
    """
    try:
        db = SupabaseClient()
        result = db.vote_verification(request.verification_id, request.user_id, request.vote_type)
        return result
    except Exception as e:
        print(f"Error voting: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/top-headlines", response_model=List[HistoryResponse])
async def get_top_headlines(limit: int = 9):
    """
    Get top headlines for the ticker.
    """
    try:
        db = SupabaseClient()
        headlines = db.get_top_headlines(limit)
        return headlines
    except Exception as e:
        print(f"Error fetching top headlines: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/community-archives")
async def get_community_archives(limit: int = 50):
    """Get archived community posts."""
    try:
        db = SupabaseClient()
        archives = db.get_community_archives(limit=limit)
        return archives
    except Exception as e:
        print(f"Error fetching community archives: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
