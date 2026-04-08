"""
Reddit router — verified Reddit posts and community subreddit browsing.

IMPACT TRACE:
  Mounts at:  /api/reddit-posts, /api/reddit-community, /api/community-archives
  Depends on: SupabaseClient.get_reddit_posts, FeedRetriever, SupabaseClient.get_community_archives
  If changed: /reddit page in frontend is affected
  Frontend callers: src/app/reddit/page.tsx
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from database.supabase_client import SupabaseClient

router = APIRouter()


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


@router.get("/reddit-posts", response_model=List[RedditPost])
async def get_reddit_posts(limit: int = 50):
    """Get verified Reddit posts."""
    try:
        db = SupabaseClient()
        return db.get_reddit_posts(limit=limit)
    except Exception as e:
        print(f"Error fetching Reddit posts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reddit-community")
async def get_community_reddit(subreddit: str, limit: int = 10):
    """Fetch posts from any subreddit."""
    try:
        from reddit.feed_retriever import FeedRetriever
        retriever = FeedRetriever()
        return retriever.get_subreddit_posts(subreddit, limit=limit)
    except Exception as e:
        print(f"Error fetching community Reddit: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch subreddit: {str(e)}")


@router.get("/community-archives")
async def get_community_archives(limit: int = 50):
    """Get archived community posts."""
    try:
        db = SupabaseClient()
        return db.get_community_archives(limit=limit)
    except Exception as e:
        print(f"Error fetching community archives: {e}")
        raise HTTPException(status_code=500, detail=str(e))
