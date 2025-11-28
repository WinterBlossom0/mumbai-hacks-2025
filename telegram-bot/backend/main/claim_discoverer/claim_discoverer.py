import os
import requests
from typing import List, Dict
from dotenv import load_dotenv
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Load .env from project root
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class ClaimDiscoverer:
    def __init__(self):
        """
        Initialize the ClaimDiscoverer using Tavily API.
        """
        self.api_key = os.getenv("TAVALY_API_KEY")
        self.api_url = "https://api.tavily.com/search"

    def get_links_for_single_claim(self, claim: str) -> List[str]:
        """
        Get credible links for a single claim using Tavily.

        Args:
            claim: Single claim to find sources for

        Returns:
            List of credible URLs
        """
        try:
            payload = {
                "api_key": self.api_key,
                "query": claim,
                "search_depth": "advanced",
                "max_results": 3,
                "include_domains": [],
                "exclude_domains": [],
            }

            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()

            data = response.json()

            # Extract URLs from results
            if "results" in data:
                return [result["url"] for result in data["results"]]

            return []

        except Exception as e:
            print(f"Error getting links for claim: {e}")
            return []

    def discover_sources(self, claims: List[str]) -> Dict[str, List[str]]:
        """
        Discover credible sources for all claims concurrently using Tavily.

        Args:
            claims: List of all claims to find sources for

        Returns:
            Dictionary mapping each claim to its list of related URLs
        """
        claim_to_links = {}

        print(f"Processing {len(claims)} claim(s) concurrently using Tavily...")

        # Process all claims concurrently
        with ThreadPoolExecutor(max_workers=min(len(claims), 10)) as executor:
            future_to_claim = {
                executor.submit(self.get_links_for_single_claim, claim): claim
                for claim in claims
            }

            for future in as_completed(future_to_claim):
                claim = future_to_claim[future]
                try:
                    links = future.result()
                    claim_to_links[claim] = links
                    print(f"[OK] Found {len(links)} link(s) for claim")
                except Exception as e:
                    print(f"Error processing claim: {e}")
                    claim_to_links[claim] = []

        # Count total links
        total_links = sum(len(links) for links in claim_to_links.values())
        claims_with_links = sum(
            1 for links in claim_to_links.values() if len(links) > 0
        )
        print(
            f"\nTotal links discovered: {total_links} across {claims_with_links}/{len(claim_to_links)} claims"
        )

        return claim_to_links
