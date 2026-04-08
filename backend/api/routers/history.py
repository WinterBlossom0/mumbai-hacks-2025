"""
History router — per-user verification history.

IMPACT TRACE:
  Mounts at:  /api/history/{user_id}
  Depends on: SupabaseClient.get_user_history
  If changed: /history page in frontend is affected
  Frontend callers: src/app/history/page.tsx
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


@router.get("/history/{user_id}", response_model=List[HistoryResponse])
async def get_history(user_id: str, limit: int = 50):
    """Get verification history for a user."""
    try:
        db = SupabaseClient()
        return db.get_user_history(user_id, limit)
    except Exception as e:
        print(f"Error fetching history: {e}")
        raise HTTPException(status_code=500, detail=str(e))
