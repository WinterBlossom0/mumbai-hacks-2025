import os
from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()


class TwitterNewsFetcher:
    """Fetches latest news from Twitter using Apify API."""
    
    def __init__(self, api_token=None):
        """
        Initialize the Twitter News Fetcher.
        
        Args:
            api_token: Apify API token. If None, reads from APIFY_API_TOKEN env variable.
        """
        self.api_token = api_token or os.getenv("APIFY_API_TOKEN")
        if not self.api_token:
            raise ValueError("APIFY_API_TOKEN not found in environment variables")
        
        self.client = ApifyClient(self.api_token)
    
    def fetch_news(self, hashtag="news", max_items=1, sort="Latest", language="en"):
        """
        Fetch latest news tweets for a given hashtag.
        
        Args:
            hashtag: The hashtag to search for (default: "news")
            
            max_items: Maximum number of tweets to fetch (default: 5)
            sort: Sort order - "Latest" or "Top" (default: "Latest")
            language: Tweet language filter (default: "en")
        
        Returns:
            List of tweet dictionaries containing text and metadata
        """
        # Prepare the Actor input
        run_input = {
            "searchTerms": [f"#{hashtag}"],
            "maxItems": max_items,
            "sort": sort,
            "tweetLanguage": language,
        }
        
        print(f"Fetching top {max_items} tweets for #{hashtag}...")
        
        # Run the Actor and wait for it to finish
        run = self.client.actor("61RPP7dywgiy0JPD0").call(run_input=run_input)
        
        # Fetch and collect results
        tweets = []
        for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
            tweets.append(item)
        
        # Check if tweets have actual content
        tweets_with_content = [t for t in tweets if t.get("text", "").strip()]
        
        if tweets_with_content:
            print(f"✓ Successfully fetched {len(tweets_with_content)} tweets with content")
        else:
            print(f"⚠ Fetched {len(tweets)} tweets but none have text content")
            print("This usually means you need a paid Apify plan to access full tweet data")
        
        return tweets_with_content if tweets_with_content else tweets
    
    def get_combined_text(self, tweets):
        """
        Combine tweet texts into a single long text for analysis.
        
        Args:
            tweets: List of tweet dictionaries
        
        Returns:
            Combined text string
        """
        combined_text = ""
        
        for i, tweet in enumerate(tweets, 1):
            text = tweet.get("text", "")
            if not text:  # Skip empty tweets
                continue
                
            author = tweet.get("author", {}).get("userName", "Unknown")
            created_at = tweet.get("createdAt", "Unknown date")
            
            combined_text += f"\n{'='*70}\n"
            combined_text += f"Tweet {i} by @{author} ({created_at})\n"
            combined_text += f"{'='*70}\n"
            combined_text += f"{text}\n"
        
        return combined_text
    
    def get_tweet_summaries(self, tweets):
        """
        Get a list of tweet summaries with key information.
        
        Args:
            tweets: List of tweet dictionaries
        
        Returns:
            List of formatted tweet summaries
        """
        summaries = []
        
        for tweet in tweets:
            summary = {
                "text": tweet.get("text", ""),
                "author": tweet.get("author", {}).get("userName", "Unknown"),
                "created_at": tweet.get("createdAt", "Unknown"),
                "retweets": tweet.get("retweetCount", 0),
                "likes": tweet.get("likeCount", 0),
                "url": tweet.get("url", "")
            }
            summaries.append(summary)
        
        return summaries


if __name__ == "__main__":
    # Test the fetcher
    try:
        fetcher = TwitterNewsFetcher()
        tweets = fetcher.fetch_news(hashtag="news", max_items=1)
        
        print("\n" + "="*70)
        print("FETCHED TWEETS")
        print("="*70)
        
        for i, tweet in enumerate(tweets, 1):
            print(f"\n{i}. @{tweet.get('author', {}).get('userName', 'Unknown')}")
            print(f"   {tweet.get('text', '')[:100]}...")
        
        print("\n" + "="*70)
        print("COMBINED TEXT")
        print("="*70)
        print(fetcher.get_combined_text(tweets))
        
    except Exception as e:
        print(f"Error: {e}")
