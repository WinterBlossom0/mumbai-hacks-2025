import os
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from database.supabase_client import SupabaseClient

def set_verdict_false():
    print("Setting all community archive verdicts to FALSE...")
    try:
        db = SupabaseClient()
        
        # Update all records in community_archives
        result = db.client.table("community_archives").update({"verdict": False}).neq("id", "00000000-0000-0000-0000-000000000000").execute()
        
        print(f"Successfully updated records.")
        
    except Exception as e:
        print(f"Error updating verdicts: {e}")

if __name__ == "__main__":
    set_verdict_false()
