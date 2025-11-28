"""
Standalone script to fetch Twitter news and run claim analysis.
Uses Twitter API v2 (FREE tier available!)

Usage:
    python backend/twitter/fetch_and_analyze.py
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from twitter.news_fetcher import TwitterNewsFetcher
from main.claim_extractor import ClaimExtractor
from main.claim_discoverer import ClaimDiscoverer
from main.reasoning import ClaimReasoner


def main():
    print("="*70)
    print("TWITTER NEWS ANALYSIS PIPELINE")
    print("="*70)
    print("\nUsing Twitter API v2 (FREE tier: 1,500 tweets/month)")
    print("Fetching minimal tweets for testing...\n")
    
    # Configuration - Using 1 tweet for testing to save API quota
    HASHTAG = "news"
    MAX_TWEETS = 1  # Minimal for testing
    
    # Step 1: Fetch tweets
    print(f"\n{'='*70}")
    print(f"STEP 1: FETCHING TWEETS FOR #{HASHTAG}")
    print(f"{'='*70}\n")
    
    try:
        fetcher = TwitterNewsFetcher()
        tweets = fetcher.fetch_news(hashtag=HASHTAG, max_items=MAX_TWEETS)
        
        if not tweets:
            print("\n❌ ERROR: No tweets fetched")
            print("\nPossible issues:")
            print("1. TWITTER_BEARER_TOKEN not set in .env file")
            print("2. Invalid or expired token")
            print("3. Rate limit exceeded")
            print("\nRun this to check your setup:")
            print("  python backend/twitter/check_twitter_api.py")
            return
        
        # Check for content
        long_text = fetcher.get_combined_text(tweets)
        if not long_text.strip():
            print("\n❌ ERROR: Tweets have no text content")
            print("This shouldn't happen with Twitter API v2")
            return
        
        print(f"\n✓ Successfully fetched {len(tweets)} tweet(s)\n")
        
        # Show summaries
        summaries = fetcher.get_tweet_summaries(tweets)
        for i, summary in enumerate(summaries, 1):
            print(f"{i}. @{summary['author']}")
            print(f"   Likes: {summary['likes']} | Retweets: {summary['retweets']}")
            print(f"   {summary['text'][:200]}...")
            print()
        
    except ValueError as e:
        print(f"\n❌ ERROR: {e}")
        print("\nSetup required:")
        print("1. Get Twitter API access at: https://developer.twitter.com")
        print("2. Add TWITTER_BEARER_TOKEN to your .env file")
        print("3. Run: python backend/twitter/check_twitter_api.py")
        print("\nSee TWITTER_API_SETUP.md for detailed instructions")
        return
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nRun this to diagnose:")
        print("  python backend/twitter/check_twitter_api.py")
        return
    
    # Step 2: Extract claims
    print(f"\n{'='*70}")
    print("STEP 2: EXTRACTING CLAIMS")
    print(f"{'='*70}\n")
    
    extractor = ClaimExtractor(max_tokens_per_chunk=15000)
    result = extractor.extract_claims(long_text, key_name="user")
    
    if not result.get("user"):
        print("❌ No claims extracted")
        return
    
    print(f"✓ Extracted {len(result['user'])} claims:\n")
    for i, claim in enumerate(result['user'], 1):
        print(f"{i}. {claim}")
    
    # Step 3: Discover sources
    print(f"\n{'='*70}")
    print("STEP 3: DISCOVERING SOURCES")
    print(f"{'='*70}\n")
    
    discoverer = ClaimDiscoverer()
    sources = discoverer.discover_sources(result['user'])
    
    total_sources = sum(len(links) for links in sources.values())
    print(f"✓ Found {total_sources} sources for {len(sources)} claims\n")
    
    for claim, links in sources.items():
        print(f"Claim: {claim[:100]}...")
        print(f"Sources: {len(links)}")
        for link in links[:3]:  # Show first 3
            print(f"  - {link}")
        print()
    
    # Step 4: Extract website claims
    print(f"\n{'='*70}")
    print("STEP 4: ANALYZING SOURCES")
    print(f"{'='*70}\n")
    
    all_urls = list(set([url for urls in sources.values() for url in urls]))
    print(f"Analyzing {len(all_urls)} unique sources...\n")
    
    website_claims = extractor.extract_website_claims(all_urls, result['user'])
    
    # Step 5: Reasoning
    print(f"\n{'='*70}")
    print("STEP 5: FINAL VERDICT")
    print(f"{'='*70}\n")
    
    reasoner = ClaimReasoner()
    final_result = reasoner.reason_all_claims(result['user'], website_claims)
    
    print(f"VERDICT: {'✓ TRUE' if final_result['verdict'] else '✗ FALSE'}")
    print(f"\nREASONING:\n{final_result['reasoning']}")
    
    print(f"\n{'='*70}")
    print("ANALYSIS COMPLETE")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
