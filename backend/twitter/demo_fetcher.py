"""
Demo Twitter fetcher that returns sample data.
Use this when API limits are hit or for testing.
"""


class DemoTwitterNewsFetcher:
    """Demo fetcher that returns sample tweets without using any API."""
    
    def __init__(self):
        """Initialize demo fetcher."""
        print("⚠ Using DEMO mode - returning sample tweets")
        print("This doesn't use any API quota\n")
    
    def fetch_news(self, hashtag="news", max_items=1, language="en"):
        """Return sample tweets for testing."""
        print(f"Fetching {max_items} sample tweet(s) for #{hashtag}...")
        
        # Sample tweets based on real news
        sample_tweets = [
            {
                "text": "BREAKING: Trump's revised Ukraine peace plan drops requirement for Kyiv to surrender Luhansk and Donetsk regions. New 19-point framework removes NATO membership ban. Zelensky calls updated plan 'more acceptable' after Geneva talks.",
                "created_at": "2024-11-29T10:30:00.000Z",
                "author": {
                    "userName": "BBCBreaking",
                    "name": "BBC Breaking News",
                    "verified": True
                },
                "likeCount": 15234,
                "retweetCount": 8456,
                "replyCount": 2341,
                "url": "https://twitter.com/BBCBreaking/status/1234567890"
            }
        ]
        
        tweets = sample_tweets[:max_items]
        print(f"✓ Returned {len(tweets)} sample tweet(s)")
        return tweets
    
    def get_combined_text(self, tweets):
        """Combine tweet texts into a single long text for analysis."""
        combined_text = ""
        
        for i, tweet in enumerate(tweets, 1):
            text = tweet.get("text", "")
            if not text:
                continue
                
            author = tweet.get("author", {}).get("userName", "Unknown")
            created_at = tweet.get("created_at", "Unknown date")
            
            combined_text += f"\n{'='*70}\n"
            combined_text += f"Tweet {i} by @{author} ({created_at})\n"
            combined_text += f"{'='*70}\n"
            combined_text += f"{text}\n"
        
        return combined_text
    
    def get_tweet_summaries(self, tweets):
        """Get a list of tweet summaries with key information."""
        summaries = []
        
        for tweet in tweets:
            summary = {
                "text": tweet.get("text", ""),
                "author": tweet.get("author", {}).get("userName", "Unknown"),
                "created_at": tweet.get("created_at", "Unknown"),
                "retweets": tweet.get("retweetCount", 0),
                "likes": tweet.get("likeCount", 0),
                "url": tweet.get("url", "")
            }
            summaries.append(summary)
        
        return summaries


if __name__ == "__main__":
    fetcher = DemoTwitterNewsFetcher()
    tweets = fetcher.fetch_news(hashtag="news", max_items=1)
    
    print("\n" + "="*70)
    print("SAMPLE TWEET")
    print("="*70)
    
    for tweet in tweets:
        print(f"\n@{tweet['author']['userName']}")
        print(f"{tweet['text']}")
    
    print("\n" + "="*70)
    print("COMBINED TEXT")
    print("="*70)
    print(fetcher.get_combined_text(tweets))
