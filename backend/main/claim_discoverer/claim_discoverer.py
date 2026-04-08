import sys
import requests
from typing import List, Dict
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import settings


class ClaimDiscoverer:
    """
    IMPACT TRACE:
      Called by: api/routers/verify.py, reddit/monitor.py
      Depends on: settings.TAVILY_API_KEY
      If changed: sources dict fed into ClaimExtractor.extract_website_claims changes
      Side-effects: uses ThreadPoolExecutor — concurrent Tavily API calls
    """

    def __init__(self):
        """
        Initialize the ClaimDiscoverer using Tavily API.
        """
        self.api_key = settings.TAVILY_API_KEY
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
                "max_results": settings.TAVILY_MAX_RESULTS,
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

        total_links = sum(len(links) for links in claim_to_links.values())
        claims_with_links = sum(1 for links in claim_to_links.values() if links)
        print(f"\nTotal links discovered: {total_links} across {claims_with_links}/{len(claim_to_links)} claims")

        return claim_to_links

    def discover_sources_from_queries(
        self, rewritten_queries: Dict[str, List[str]]
    ) -> Dict[str, List[str]]:
        """
        Discover sources using pre-rewritten query pairs produced by ClaimRewriter.

        Each claim maps to [query_a, query_b]. Both queries are sent to Tavily
        independently; the resulting URLs are deduplicated and merged so the
        downstream scraper gets broader evidence coverage.

        Args:
            rewritten_queries: {original_claim: [query_a, query_b]}
                               as returned by ClaimRewriter.rewrite_claims()

        Returns:
            {original_claim: [deduplicated_urls]}  — same shape as discover_sources()
        """
        if not rewritten_queries:
            return {}

        # Flatten to (claim, query) pairs so we can parallelise all Tavily calls
        tasks: List[tuple] = []
        for claim, queries in rewritten_queries.items():
            for q in queries:
                if q and q.strip():
                    tasks.append((claim, q))

        print(f"[ClaimDiscoverer] {len(tasks)} rewritten queries across "
              f"{len(rewritten_queries)} claims ...")

        # {claim: set of urls}
        claim_url_sets: Dict[str, set] = {c: set() for c in rewritten_queries}

        with ThreadPoolExecutor(max_workers=min(len(tasks), 10)) as executor:
            future_to_task = {
                executor.submit(self.get_links_for_single_claim, query): (claim, query)
                for claim, query in tasks
            }
            for future in as_completed(future_to_task):
                claim, query = future_to_task[future]
                try:
                    urls = future.result()
                    claim_url_sets[claim].update(urls)
                    print(f"  [OK] {len(urls)} url(s) for query: {query[:60]}")
                except Exception as e:
                    print(f"  [ERR] {e} — query: {query[:60]}")

        result = {claim: list(urls) for claim, urls in claim_url_sets.items()}
        total = sum(len(u) for u in result.values())
        print(f"[ClaimDiscoverer] {total} unique URLs across {len(result)} claims")
        return result
