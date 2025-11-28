"""
Quick script to check if your Twitter API v2 setup is working correctly.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()


def check_twitter_api_setup():
    print("="*70)
    print("TWITTER API V2 SETUP CHECKER")
    print("="*70)
    
    # Check if token exists
    token = os.getenv("TWITTER_BEARER_TOKEN")
    
    if not token:
        print("\n❌ TWITTER_BEARER_TOKEN not found in .env file")
        print("\nTo fix:")
        print("1. Go to: https://developer.twitter.com/en/portal/dashboard")
        print("2. Create a project and app (if you haven't)")
        print("3. Get your Bearer Token from 'Keys and tokens'")
        print("4. Add it to your .env file:")
        print("   TWITTER_BEARER_TOKEN=your_token_here")
        print("\nSee TWITTER_API_SETUP.md for detailed instructions")
        return False
    
    if token == "<YOUR_TWITTER_BEARER_TOKEN>":
        print("\n❌ TWITTER_BEARER_TOKEN is still set to placeholder value")
        print("\nTo fix:")
        print("1. Get your actual Bearer Token from Twitter Developer Portal")
        print("2. Replace <YOUR_TWITTER_BEARER_TOKEN> in .env with your real token")
        print("\nSee TWITTER_API_SETUP.md for detailed instructions")
        return False
    
    print(f"\n✓ Token found: {token[:20]}...{token[-10:]}")
    
    # Try to connect
    print("\nTesting connection to Twitter API v2...")
    
    try:
        url = "https://api.twitter.com/2/tweets/search/recent"
        headers = {
            "Authorization": f"Bearer {token}",
            "User-Agent": "v2RecentSearchPython"
        }
        params = {
            "query": "#test",
            "max_results": 10,
            "tweet.fields": "created_at,public_metrics"
        }
        
        print("Running test search for #test...")
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 401:
            print("\n❌ Authentication failed")
            print("Your Bearer Token is invalid or expired")
            print("\nTo fix:")
            print("1. Go to Twitter Developer Portal")
            print("2. Regenerate your Bearer Token")
            print("3. Update it in your .env file")
            return False
        
        elif response.status_code == 403:
            print("\n❌ Access forbidden")
            print("Your app might not have the required permissions")
            print("\nTo fix:")
            print("1. Check your app settings in Twitter Developer Portal")
            print("2. Make sure you have 'Read' permissions enabled")
            return False
        
        elif response.status_code == 429:
            print("\n⚠ Rate limit exceeded")
            print("You've used your monthly quota")
            print("\nFree tier: 1,500 tweets/month")
            print("Wait until next month or upgrade to paid tier")
            return False
        
        elif response.status_code == 200:
            data = response.json()
            
            if "data" in data and data["data"]:
                print(f"\n✓ SUCCESS! Your Twitter API setup is working correctly")
                print(f"✓ Found {len(data['data'])} tweets for #test")
                print(f"\nSample tweet: {data['data'][0].get('text', '')[:100]}...")
                
                # Show rate limit info
                if "x-rate-limit-remaining" in response.headers:
                    remaining = response.headers.get("x-rate-limit-remaining")
                    limit = response.headers.get("x-rate-limit-limit")
                    print(f"\nRate limit: {remaining}/{limit} requests remaining")
                
                return True
            else:
                print(f"\n✓ Connection successful but no tweets found for #test")
                print("This is normal - the API is working!")
                return True
        
        else:
            print(f"\n❌ Unexpected error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error connecting to Twitter API: {e}")
        print("\nPossible issues:")
        print("1. Network connection problem")
        print("2. Invalid token format")
        print("3. Twitter API service is down")
        return False


if __name__ == "__main__":
    success = check_twitter_api_setup()
    
    print("\n" + "="*70)
    if success:
        print("✓ READY TO USE")
        print("="*70)
        print("\nYou can now run:")
        print("  python backend/twitter/fetch_and_analyze.py")
        print("  python backend/test/test_twitter_long_text.py")
    else:
        print("❌ SETUP INCOMPLETE")
        print("="*70)
        print("\nPlease fix the issues above before using the Twitter module")
        print("See TWITTER_API_SETUP.md for detailed setup instructions")
    print()
