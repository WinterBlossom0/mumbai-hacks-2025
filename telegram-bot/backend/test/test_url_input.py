import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main.claim_extractor import ClaimExtractor
from main.claim_discoverer import ClaimDiscoverer
from main.reasoning import ClaimReasoner


def test_url_input_pipeline():
    """Test the complete pipeline starting with a URL as input."""
    print("\n" + "=" * 70)
    print("COMPLETE PIPELINE TEST - URL INPUT")
    print("=" * 70 + "\n")

    # Test URL
    test_url = "https://www.tribuneindia.com/news/chandigarh/baseless-emotional-manipulation-union-minister-bittu-slams-rumour-mongering-over-centre-chandigarh-proposal/"

    print(f"Input URL: {test_url}\n")

    # Step 1: Extract claims from URL
    print("=" * 70)
    print("STEP 1: EXTRACTING CLAIMS FROM URL")
    print("=" * 70 + "\n")

    extractor = ClaimExtractor(max_tokens_per_chunk=15000)
    result = extractor.extract_claims_from_url(test_url, key_name="user")

    print(f"\nTotal claims extracted: {len(result['user'])}\n")

    for i, claim in enumerate(result["user"], 1):
        print(f"{i}. {claim}")

    assert "user" in result
    assert isinstance(result["user"], list)
    assert len(result["user"]) > 0

    print("\n✓ Claim extraction successful!")

    # Step 2: Discover sources for the extracted claims
    print("\n" + "=" * 70)
    print("STEP 2: DISCOVERING SOURCES FOR CLAIMS")
    print("=" * 70 + "\n")

    discoverer = ClaimDiscoverer()
    sources = discoverer.discover_sources(result["user"])

    print("\n" + "=" * 70)
    print("DISCOVERED SOURCES (CLAIM → LINKS)")
    print("=" * 70 + "\n")

    for claim, links in sources.items():
        print(f"Claim: {claim}")
        print(f"Links ({len(links)}):")
        for link in links:
            print(f"  - {link}")
        print()

    assert isinstance(sources, dict)

    total_links = sum(len(links) for links in sources.values())

    print("=" * 70)
    print(f"Sources discovered: {total_links}")
    print("=" * 70)

    # Step 3: Extract claims from ALL discovered websites
    print("\n" + "=" * 70)
    print("STEP 3: EXTRACTING CLAIMS FROM ALL WEBSITES")
    print("=" * 70 + "\n")

    all_website_claims = {}
    all_urls = []

    if result["user"] and sources:
        # Collect all unique URLs
        for urls in sources.values():
            all_urls.extend(urls)
        all_urls = list(set(all_urls))  # Remove duplicates

        print(
            f"\nExtracting claims from {len(all_urls)} unique website(s) for ALL original claims\n"
        )

        # Extract website claims (passing all original claims at once)
        website_claims = extractor.extract_website_claims(all_urls, result["user"])

        # Organize by original claim
        for original_claim, urls in sources.items():
            all_website_claims[original_claim] = {
                url: website_claims.get(url, []) for url in urls
            }

        # Display results
        print("\n" + "=" * 70)
        print("WEBSITE CLAIMS ANALYSIS")
        print("=" * 70 + "\n")

        for original_claim, website_data in all_website_claims.items():
            print(f"Original Claim: {original_claim}")
            print(f"Websites analyzed: {len(website_data)}")
            print()

            for url, claims in website_data.items():
                print(f"  URL: {url}")
                print(f"  Claims ({len(claims)}):")
                for i, claim in enumerate(claims, 1):
                    print(f"    {i}. {claim}")
                print()

        total_websites = sum(
            len(website_data) for website_data in all_website_claims.values()
        )
        total_website_claims = sum(
            sum(len(claims) for claims in website_data.values())
            for website_data in all_website_claims.values()
        )

        print("=" * 70)
        print("COMPLETE PIPELINE RESULTS")
        print("=" * 70)
        print(f"Original claims extracted: {len(result['user'])}")
        print(f"Sources discovered: {total_links}")
        print(f"Total websites analyzed: {total_websites}")
        print(f"Total website claims extracted: {total_website_claims}")
        print("=" * 70)

        # Step 4: Reasoning with Gemini 2.5 Pro
        print("\n" + "=" * 70)
        print("STEP 4: REASONING WITH GEMINI 2.5 PRO")
        print("=" * 70 + "\n")

        reasoner = ClaimReasoner()

        # Collect all website claims into one dictionary
        all_website_claims_flat = {}
        for original_claim, website_data in all_website_claims.items():
            for url, claims in website_data.items():
                if url not in all_website_claims_flat:
                    all_website_claims_flat[url] = []
                all_website_claims_flat[url].extend(claims)

        print(
            f"Analyzing {len(result['user'])} user claims against {len(all_website_claims_flat)} sources...\n"
        )

        # Get single overall verdict
        final_result = reasoner.reason_all_claims(
            result["user"], all_website_claims_flat
        )

        print("=" * 70)
        print("FINAL VERDICT")
        print("=" * 70)
        print(f"\nVERDICT: {'✓ TRUE' if final_result['verdict'] else '✗ FALSE'}")
        print(f"\nREASONING:\n{final_result['reasoning']}")
        print("\n" + "=" * 70)

    print("\n✓ Complete pipeline test passed!")


if __name__ == "__main__":
    print("Starting URL Input Pipeline Test...")

    try:
        test_url_input_pipeline()

        print("\n" + "=" * 70)
        print("TEST COMPLETED SUCCESSFULLY! ✓")
        print("=" * 70)

    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
