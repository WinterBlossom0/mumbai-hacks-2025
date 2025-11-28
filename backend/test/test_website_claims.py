import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main.claim_extractor import ClaimExtractor


def test_website_claims_extraction():
    """Test extracting claims from websites related to an original claim."""
    print("\n" + "=" * 70)
    print("WEBSITE CLAIMS EXTRACTION TEST")
    print("=" * 70 + "\n")

    extractor = ClaimExtractor()

    # Original claim
    original_claim = "Global temperatures have risen by approximately 1.1°C since pre-industrial times"

    # Sample URLs related to climate change
    test_urls = [
        "https://www.climate.gov/news-features/understanding-climate/climate-change-atmospheric-carbon-dioxide",
        "https://www.nasa.gov/climate",
    ]

    print(f"Original Claim: {original_claim}\n")
    print(f"Analyzing {len(test_urls)} website(s)...\n")

    # Extract claims from websites
    results = extractor.extract_website_claims(test_urls, original_claim)

    # Display results
    print("\n" + "=" * 70)
    print("EXTRACTED WEBSITE CLAIMS")
    print("=" * 70 + "\n")

    for url, claims in results.items():
        print(f"URL: {url}")
        print(f"Claims ({len(claims)}):")
        for i, claim in enumerate(claims, 1):
            print(f"  {i}. {claim}")
        print()

    # Assertions
    assert len(results) > 0
    for url, claims in results.items():
        assert isinstance(claims, list)

    total_claims = sum(len(claims) for claims in results.values())

    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Websites analyzed: {len(results)}")
    print(f"Total claims extracted: {total_claims}")
    print("=" * 70)

    print("\n✓ Test passed!")


if __name__ == "__main__":
    print("Starting Website Claims Extraction Test...")

    try:
        test_website_claims_extraction()

        print("\n" + "=" * 70)
        print("TEST COMPLETED SUCCESSFULLY! ✓")
        print("=" * 70)

    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
