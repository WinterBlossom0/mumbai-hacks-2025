import os
from pathlib import Path
from dotenv import load_dotenv
from tavily import TavilyClient
from typing import List, Optional

# Load .env from project root
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class ImageSearcher:
    def __init__(self):
        # Check for correct spelling and common typo
        self.api_key = os.getenv("TAVILY_API_KEY") or os.getenv("TAVALY_API_KEY")
        
        if not self.api_key:
            print("Warning: TAVILY_API_KEY (or TAVALY_API_KEY) not set")
        try:
            self.client = TavilyClient(api_key=self.api_key)
        except Exception as e:
            print(f"Error initializing Tavily client: {e}")
            self.client = None

    def search_image(self, query: str) -> Optional[str]:
        """
        Search for an image using Tavily.
        """
        if not self.client:
            return None

        try:
            print(f"Searching for image with query: {query}")
            # Tavily's search method with include_images=True
            response = self.client.search(query, include_images=True, max_results=1, search_depth="basic")
            
            if response and 'images' in response and response['images']:
                image_url = response['images'][0]
                print(f"Found image: {image_url}")
                return image_url
            
            print("No images found in Tavily response")
            return None
        except Exception as e:
            print(f"Error searching for image: {e}")
            return None

    def get_image_for_claims(self, claims: List[str]) -> Optional[str]:
        """
        Generate a search query from claims and fetch an image.
        """
        if not claims:
            return None
        
        # Use the first claim, truncated to avoid overly long queries
        query = claims[0][:200]
        return self.search_image(query)
