"""
Public feed router — public verifications and top headlines.

IMPACT TRACE:
  Mounts at:  /api/public-feed, /api/top-headlines
  Depends on: SupabaseClient.get_public_feed, SupabaseClient.get_top_headlines
  If changed: homepage feed + news ticker in frontend are affected
  Frontend callers:
    - src/components/PublicFeed.tsx  → GET /api/public-feed
    - src/components/NewsTicker.tsx  → GET /api/top-headlines
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from database.supabase_client import SupabaseClient

router = APIRouter()


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


@router.get("/public-feed", response_model=List[HistoryResponse])
async def get_public_feed(limit: int = 20):
    """Get public verifications for the homepage feed."""
    try:
        db = SupabaseClient()
        return db.get_public_feed(limit)
    except Exception as e:
        print(f"Error fetching public feed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top-headlines", response_model=List[HistoryResponse])
async def get_top_headlines(limit: int = 9):
    """Get top upvoted public verifications for the news ticker."""
    try:
        db = SupabaseClient()
        return db.get_top_headlines(limit)
    except Exception as e:
        print(f"Error fetching top headlines: {e}")
        raise HTTPException(status_code=500, detail=str(e))
