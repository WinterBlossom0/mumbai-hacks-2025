"""
Quick script to check if your Apify setup is working correctly.
"""

import os
from dotenv import load_dotenv
from apify_client import ApifyClient

load_dotenv()

def check_apify_setup():
    print("="*70)
    print("APIFY SETUP CHECKER")
    print("="*70)
    
    # Check if token exists
    token = os.getenv("APIFY_API_TOKEN")
    
    if not token:
        print("\n❌ APIFY_API_TOKEN not found in .env file")
        print("\nTo fix:")
        print("1. Get your API token from: https://console.apify.com/account/integrations")
        print("2. Add it to your .env file:")
        print("   APIFY_API_TOKEN=your_token_here")
        return False
    
    if token == "<YOUR_API_TOKEN>":
        print("\n❌ APIFY_API_TOKEN is still set to placeholder value")
        print("\nTo fix:")
        print("1. Get your actual API token from: https://console.apify.com/account/integrations")
        print("2. Replace <YOUR_API_TOKEN> in .env with your real token")
        return False
    
    print(f"\n✓ Token found: {token[:10]}...{token[-5:]}")
    
    # Try to connect
    print("\nTesting connection to Apify...")
    
    try:
        client = ApifyClient(token)
        
        # Try a minimal test run
        run_input = {
            "searchTerms": ["#test"],
            "maxItems": 1,
            "sort": "Latest",
            "tweetLanguage": "en",
        }
        
        print("Running test scrape (1 tweet)...")
        run = client.actor("61RPP7dywgiy0JPD0").call(run_input=run_input)
        
        # Check results
        tweets = list(client.dataset(run["defaultDatasetId"]).iterate_items())
        
        if not tweets:
            print("\n⚠ Connection successful but no tweets returned")
            print("This is normal for the test hashtag")
        elif tweets[0].get("text"):
            print(f"\n✓ SUCCESS! Your Apify setup is working correctly")
            print(f"✓ You have a PAID plan with full tweet access")
            print(f"\nSample tweet: {tweets[0].get('text')[:100]}...")
            return True
        else:
            print("\n⚠ Connection successful but tweets have no content")
            print("❌ You are using the FREE plan")
            print("\nThe free plan does NOT return tweet text content.")
            print("You need to upgrade to a paid plan at: https://apify.com/pricing")
            return False
            
    except Exception as e:
        print(f"\n❌ Error connecting to Apify: {e}")
        print("\nPossible issues:")
        print("1. Invalid API token")
        print("2. Network connection problem")
        print("3. Apify service is down")
        return False
    
    return True


if __name__ == "__main__":
    success = check_apify_setup()
    
    print("\n" + "="*70)
    if success:
        print("✓ READY TO USE")
        print("="*70)
        print("\nYou can now run:")
        print("  python backend/twitter/fetch_and_analyze.py")
    else:
        print("❌ SETUP INCOMPLETE")
        print("="*70)
        print("\nPlease fix the issues above before using the Twitter module")
    print()
