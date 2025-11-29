import os
import praw
from dotenv import load_dotenv
from pathlib import Path
from typing import List, Dict, Any

# Load environment variables
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class FeedRetriever:
    """Retrieve posts from any subreddit."""
    
    def __init__(self):
        """Initialize Reddit API client."""
        self.reddit = praw.Reddit(
            client_id=os.getenv("YOUR_CLIENT_ID"),
            client_secret=os.getenv("YOUR_CLIENT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT", "TruthLens/1.0")
        )
    
    def get_subreddit_posts(self, subreddit_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch the latest posts from a specified subreddit.
        
        Args:
            subreddit_name: Name of the subreddit (without 'r/')
            limit: Number of posts to fetch (default: 10)
            
        Returns:
            List of post dictionaries containing post data
        """
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            posts = []
            
            for post in subreddit.new(limit=limit):
                post_data = {
                    "id": post.id,
                    "title": post.title,
                    "body": post.selftext,
                    "url": post.url if not post.is_self else None,
                    "author": str(post.author),
                    "created_at": post.created_utc,
                    "score": post.score,
                    "num_comments": post.num_comments,
                    "subreddit": post.subreddit.display_name,
                    "permalink": f"https://reddit.com{post.permalink}",
                    "is_self": post.is_self,
                    "upvote_ratio": post.upvote_ratio
                }
                posts.append(post_data)
            
            return posts
        except Exception as e:
            print(f"Error fetching posts from r/{subreddit_name}: {e}")
            raise Exception(f"Failed to fetch subreddit: {str(e)}")


if __name__ == "__main__":
    # Test the feed retriever
    retriever = FeedRetriever()
    
    # Test with a popular subreddit
    test_subreddit = "AskReddit"
    print(f"\nFetching last 5 posts from r/{test_subreddit}...")
    
    try:
        posts = retriever.get_subreddit_posts(test_subreddit, limit=5)
        print(f"\nSuccessfully fetched {len(posts)} posts:")
        for i, post in enumerate(posts, 1):
            print(f"\n{i}. {post['title']}")
            print(f"   Author: u/{post['author']}")
            print(f"   Score: {post['score']} | Comments: {post['num_comments']}")
            print(f"   URL: {post['permalink']}")
    except Exception as e:
        print(f"Error: {e}")
