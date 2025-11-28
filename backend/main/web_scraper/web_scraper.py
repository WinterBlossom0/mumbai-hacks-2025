import os
import requests
from typing import Dict
from dotenv import load_dotenv
from pathlib import Path
from bs4 import BeautifulSoup

# Load .env from project root
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class WebScraper:
    def __init__(self):
        """
        Initialize the WebScraper using Tavily API with BeautifulSoup fallback.
        """
        self.api_key = os.getenv("TAVALY_API_KEY")
        self.api_url = "https://api.tavily.com/extract"

    def scrape_with_beautifulsoup(self, url: str) -> Dict[str, str]:
        """
        Fallback method to scrape URL using BeautifulSoup.

        Args:
            url: The URL to scrape

        Returns:
            Dictionary with 'url', 'content', and 'title' keys
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # Extract title
            title = soup.find("title")
            title_text = title.get_text().strip() if title else ""

            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()

            # Get text content
            text = soup.get_text()

            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = "\n".join(chunk for chunk in chunks if chunk)

            return {"url": url, "title": title_text, "content": text}

        except Exception as e:
            print(f"Error with BeautifulSoup scraping: {e}")
            return {"url": url, "title": "", "content": ""}

    def scrape_url(self, url: str) -> Dict[str, str]:
        """
        Extract the entire content from a given URL using Tavily.

        Args:
            url: The URL to scrape

        Returns:
            Dictionary with 'url', 'content', and 'title' keys
        """
        try:
            payload = {"api_key": self.api_key, "urls": [url]}

            print(f"Sending request to Tavily extract API...")
            response = requests.post(self.api_url, json=payload)
            
            print(f"Response status: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
            response.raise_for_status()

            data = response.json()

            # Extract content from results
            if "results" in data and len(data["results"]) > 0:
                result = data["results"][0]
                return {
                    "url": url,
                    "title": result.get("title", ""),
                    "content": result.get("raw_content", ""),
                }
            elif "failed_results" in data:
                print(f"Failed to extract: {data['failed_results']}")

            return {"url": url, "title": "", "content": ""}

        except Exception as e:
            print(f"Error scraping URL with Tavily: {e}")
            print("Falling back to BeautifulSoup...")
            return self.scrape_with_beautifulsoup(url)
