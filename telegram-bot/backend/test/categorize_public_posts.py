"""
Script to categorize all existing public verifications in Supabase.
This script will update the category column for all verifications where is_public is TRUE.
"""

import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from database.supabase_client import SupabaseClient
from main.categorizer import ClaimCategorizer


def get_public_verifications_without_category():
    """Get all public verifications that don't have a category set."""
    db = SupabaseClient()
    try:
        result = (
            db.client.table("verifications")
            .select("*")
            .eq("is_public", True)
            .execute()
        )
        return result.data if result.data else []
    except Exception as e:
        print(f"Error fetching public verifications: {e}")
        return []


def update_verification_category(verification_id: str, category: str):
    """Update the category for a specific verification."""
    db = SupabaseClient()
    try:
        result = (
            db.client.table("verifications")
            .update({"category": category})
            .eq("id", verification_id)
            .execute()
        )
        return len(result.data) > 0
    except Exception as e:
        print(f"Error updating category: {e}")
        return False


def main():
    """Main function to categorize all public verifications."""
    print("=" * 70)
    print("CATEGORIZING PUBLIC VERIFICATIONS")
    print("=" * 70)
    
    # Initialize categorizer
    categorizer = ClaimCategorizer()
    
    # Get all public verifications
    print("\nFetching public verifications...")
    verifications = get_public_verifications_without_category()
    
    if not verifications:
        print("No public verifications found.")
        return
    
    print(f"Found {len(verifications)} public verification(s).\n")
    
    # Process each verification
    success_count = 0
    error_count = 0
    skipped_count = 0
    
    for i, verification in enumerate(verifications, 1):
        verification_id = verification.get("id")
        claims = verification.get("claims", [])
        current_category = verification.get("category")
        
        print(f"[{i}/{len(verifications)}] Processing verification {verification_id}")
        
        # Skip if already has a category
        if current_category:
            print(f"  ⏩ Already has category: {current_category}")
            skipped_count += 1
            continue
        
        # Skip if no claims
        if not claims:
            print(f"  ⚠️  No claims found, skipping")
            skipped_count += 1
            continue
        
        try:
            # Categorize claims
            print(f"  📋 Analyzing {len(claims)} claim(s)...")
            category = categorizer.categorize_claims(claims)
            print(f"  ✅ Category: {category}")
            
            # Update in database
            success = update_verification_category(verification_id, category)
            
            if success:
                print(f"  💾 Updated in database")
                success_count += 1
            else:
                print(f"  ❌ Failed to update in database")
                error_count += 1
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            error_count += 1
        
        print()
    
    # Print summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total processed: {len(verifications)}")
    print(f"✅ Successfully categorized: {success_count}")
    print(f"⏩ Skipped (already categorized): {skipped_count}")
    print(f"❌ Errors: {error_count}")
    print("=" * 70)


if __name__ == "__main__":
    main()
