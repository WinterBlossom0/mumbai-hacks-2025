import os
from supabase import create_client, Client
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Load .env from project root
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class SupabaseClient:
    def __init__(self):
        """Initialize Supabase client."""
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        
        self.client: Client = create_client(url, key)
    
    def save_verification(
        self,
        user_id: str,
        user_email: str,
        input_content: str,
        input_type: str,
        verdict: bool,
        reasoning: str,
        claims: List[str],
        sources: Dict[str, List[str]],
        is_public: bool = False,
    ) -> Dict:
        """
        Save a verification result to Supabase.
        
        Args:
            user_id: User ID (default: "0" for user0)
            user_email: User email (default: "user0@gmail.com")
            input_content: The original input (text or URL)
            input_type: Type of input ("text" or "url")
            verdict: True/False verdict
            reasoning: AI reasoning for the verdict
            claims: List of extracted claims
            sources: Dictionary of sources found
            
        Returns:
            Dictionary with the saved record
        """
        try:
            data = {
                "user_id": user_id,
                "user_email": user_email,
                "input_content": input_content[:10000],  # Limit to 10000 chars
                "input_type": input_type,
                "verdict": verdict,
                "reasoning": reasoning,
                "claims": claims,
                "sources": sources,
                "is_public": is_public,
                "created_at": datetime.utcnow().isoformat(),
            }
            
            result = self.client.table("verifications").insert(data).execute()
            return result.data[0] if result.data else {}
            
        except Exception as e:
            print(f"Error saving to Supabase: {e}")
            raise
    
    def get_user_history(
        self, user_id: str, limit: int = 50
    ) -> List[Dict]:
        """
        Get verification history for a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of records to return
            
        Returns:
            List of verification records
        """
        try:
            result = (
                self.client.table("verifications")
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            
            return result.data if result.data else []
            
        except Exception as e:
            print(f"Error fetching history from Supabase: {e}")
            return []
    
    def get_verification_by_id(self, verification_id: str) -> Optional[Dict]:
        """
        Get a specific verification by ID.
        
        Args:
            verification_id: Verification record ID
            
        Returns:
            Verification record or None
        """
        try:
            result = (
                self.client.table("verifications")
                .select("*")
                .eq("id", verification_id)
                .execute()
            )
            
            return result.data[0] if result.data else None
            
        except Exception as e:
            print(f"Error fetching verification from Supabase: {e}")
            return None
    
    def get_public_feed(self, limit: int = 20) -> List[Dict]:
        """
        Get public verifications for the homepage feed.
        
        Args:
            limit: Maximum number of records to return (default: 20)
            
        Returns:
            List of public verification records
        """
        try:
            result = (
                self.client.table("verifications")
                .select("*")
                .eq("is_public", True)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            
            return result.data if result.data else []
            
        except Exception as e:
            print(f"Error fetching public feed from Supabase: {e}")
            return []
    
    def toggle_public_status(self, verification_id: str, is_public: bool, headline: Optional[str] = None, category: Optional[str] = None, image_url: Optional[str] = None) -> bool:
        """
        Toggle the public status of a verification.
        
        Args:
            verification_id: Verification record ID
            is_public: New public status
            headline: Optional headline to set
            category: Optional category to set
            image_url: Optional image URL to set
            
        Returns:
            True if successful, False otherwise
        """
        try:
            data = {"is_public": is_public, "updated_at": datetime.utcnow().isoformat()}
            if headline:
                data["headline"] = headline
            if category:
                data["category"] = category
            if image_url:
                data["image_url"] = image_url

            result = (
                self.client.table("verifications")
                .update(data)
                .eq("id", verification_id)
                .execute()
            )
            
            return len(result.data) > 0
            
        except Exception as e:
            print(f"Error toggling public status in Supabase: {e}")
            return False
            
    def vote_verification(self, verification_id: str, user_id: str, vote_type: int) -> Dict:
        """
        Vote on a verification (Upvote/Downvote).
        
        Args:
            verification_id: Verification record ID
            user_id: User ID
            vote_type: 1 for upvote, -1 for downvote
            
        Returns:
            Dictionary with new upvotes and downvotes counts
        """
        try:
            # 1. Upsert into ratings table
            data = {
                "verification_id": verification_id,
                "user_id": user_id,
                "vote_type": vote_type,
                "created_at": datetime.utcnow().isoformat()
            }
            # Note: on_conflict needs to match the UNIQUE constraint in SQL
            self.client.table("ratings").upsert(data, on_conflict="verification_id, user_id").execute()
            
            # 2. Recalculate counts
            # Fetch all ratings for this verification to get accurate counts
            ratings_response = self.client.table("ratings").select("vote_type").eq("verification_id", verification_id).execute()
            
            if ratings_response.data:
                upvotes = sum(1 for r in ratings_response.data if r['vote_type'] == 1)
                downvotes = sum(1 for r in ratings_response.data if r['vote_type'] == -1)
            else:
                upvotes = 0
                downvotes = 0
            
            # 3. Update verifications table with new counts
            self.client.table("verifications").update({
                "upvotes": upvotes, 
                "downvotes": downvotes
            }).eq("id", verification_id).execute()
            
            return {"upvotes": upvotes, "downvotes": downvotes}
            
        except Exception as e:
            print(f"Error voting in Supabase: {e}")
            raise

    def get_top_headlines(self, limit: int = 9) -> List[Dict]:
        """
        Get top upvoted public verifications for the news ticker.
        """
        try:
            result = (
                self.client.table("verifications")
                .select("*")
                .eq("is_public", True)
                .order("upvotes", desc=True)
                .limit(limit)
                .execute()
            )
            return result.data if result.data else []
        except Exception as e:
            print(f"Error fetching top headlines: {e}")
            return []
    def save_reddit_post(
        self,
        reddit_id: str,
        title: str,
        body: str,
        url: Optional[str],
        headline: Optional[str],
        verdict: bool,
        reasoning: str,
        claims: List[str],
        sources: Dict[str, List[str]],
        author: str,
        subreddit: str = "eyeoftruth",
    ) -> Dict:
        """Save a verified Reddit post."""
        try:
            data = {
                "reddit_id": reddit_id,
                "title": title,
                "body": body,
                "url": url,
                "headline": headline,
                "verdict": verdict,
                "reasoning": reasoning,
                "claims": claims,
                "sources": sources,
                "author": author,
                "subreddit": subreddit,
                "created_at": datetime.utcnow().isoformat(),
            }
            
            result = self.client.table("reddit_posts").insert(data).execute()
            return result.data[0] if result.data else {}
        except Exception as e:
            print(f"Error saving Reddit post: {e}")
            raise

    def get_reddit_posts(self, limit: int = 50) -> List[Dict]:
        """Get verified Reddit posts (only TRUE ones are typically shown)."""
        try:
            result = (
                self.client.table("reddit_posts")
                .select("*")
                .eq("is_removed", False)  # Only show non-removed posts
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            return result.data if result.data else []
        except Exception as e:
            print(f"Error fetching Reddit posts: {e}")
            return []

    def save_community_archive(
        self,
        reddit_id: str,
        title: str,
        body: str,
        subreddit: str,
        verdict: bool,
        reasoning: str,
        claims: List[str],
        sources: Dict[str, List[str]],
        image_url: Optional[str] = None
    ) -> Dict:
        """Save a verified community post to archive."""
        try:
            # Check if exists first
            existing = self.client.table("community_archives").select("id").eq("reddit_id", reddit_id).execute()
            if existing.data:
                return existing.data[0]

            data = {
                "reddit_id": reddit_id,
                "title": title,
                "body": body,
                "subreddit": subreddit,
                "verdict": verdict,
                "reasoning": reasoning,
                "claims": claims,
                "sources": sources,
                "image_url": image_url,
                "created_at": datetime.utcnow().isoformat(),
            }
            
            result = self.client.table("community_archives").insert(data).execute()
            return result.data[0] if result.data else {}
        except Exception as e:
            print(f"Error saving community archive: {e}")
            # Don't raise, just log error to prevent breaking the flow
            return {}

    def get_community_archives(self, limit: int = 50) -> List[Dict]:
        """Get archived community posts."""
        try:
            result = (
                self.client.table("community_archives")
                .select("*")
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            return result.data if result.data else []
        except Exception as e:
            print(f"Error fetching community archives: {e}")
            return []

    def check_reddit_post_exists(self, reddit_id: str) -> bool:
        """Check if a Reddit post has already been processed."""
        try:
            result = (
                self.client.table("reddit_posts")
                .select("id")
                .eq("reddit_id", reddit_id)
                .execute()
            )
            return len(result.data) > 0
        except Exception as e:
            print(f"Error checking Reddit post: {e}")
            return False

    def mark_reddit_post_removed(self, reddit_id: str):
        """Mark a Reddit post as removed."""
        try:
            self.client.table("reddit_posts").update({"is_removed": True}).eq("reddit_id", reddit_id).execute()
        except Exception as e:
            print(f"Error marking Reddit post as removed: {e}")
