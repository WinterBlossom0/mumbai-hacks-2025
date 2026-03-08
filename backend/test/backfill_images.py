import sys
import os
from pathlib import Path
import time

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from database.supabase_client import SupabaseClient
from image_retrieve.image_searcher import ImageSearcher

def backfill_images():
    print("Starting image backfill for public verifications...")
    
    db = SupabaseClient()
    searcher = ImageSearcher()
    
    # Fetch all public verifications
    # Note: Supabase limit is usually 1000, we might need pagination if there are more
    try:
        response = db.client.table("verifications")\
            .select("*")\
            .eq("is_public", True)\
            .execute()
        
        public_verifications = response.data
        print(f"Found {len(public_verifications)} public verifications.")
        
        count = 0
        for verification in public_verifications:
            # Check if image_url is missing or empty
            if not verification.get("image_url"):
                print(f"Processing verification ID: {verification['id']}")
                
                claims = verification.get("claims", [])
                input_content = verification.get("input_content", "")
                
                image_url = None
                
                # Try to find image using claims first
                if claims:
                    print(f"  Searching using claims...")
                    image_url = searcher.get_image_for_claims(claims)
                
                # Fallback to input content if no claims or search failed
                if not image_url and input_content:
                    print(f"  Searching using input content...")
                    # Truncate to avoid overly long queries
                    image_url = searcher.search_image(input_content[:200])
                
                if image_url:
                    print(f"  Found image: {image_url}")
                    
                    # Update the record
                    db.client.table("verifications")\
                        .update({"image_url": image_url})\
                        .eq("id", verification['id'])\
                        .execute()
                    
                    print(f"  Updated record.")
                    count += 1
                else:
                    print(f"  No image found.")
                
                # Sleep briefly to avoid hitting rate limits
                time.sleep(1)
            else:
                # print(f"Skipping {verification['id']} - already has image.")
                pass
                
        print(f"\nBackfill complete. Updated {count} records.")
        
    except Exception as e:
        print(f"Error during backfill: {e}")

if __name__ == "__main__":
    backfill_images()
