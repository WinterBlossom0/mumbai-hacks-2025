import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main.web_scraper import WebScraper


def test_single_url():
    """Test scraping a single URL."""
    print("\n" + "=" * 70)
    print("WEB SCRAPER TEST - Single URL")
    print("=" * 70 + "\n")

    scraper = WebScraper()

    # Test with a reliable news article URL
    test_url = "https://www.climate.gov/news-features/understanding-climate/climate-change-atmospheric-carbon-dioxide"

    print(f"Scraping URL: {test_url}\n")

    result = scraper.scrape_url(test_url)

    print("=" * 70)
    print("SCRAPED CONTENT")
    print("=" * 70)
    print(f"\nURL: {result['url']}")
    print(f"Title: {result['title']}")
    print(f"\nContent Length: {len(result['content'])} characters")
    print(f"\nContent Preview (first 1000 chars):")
    print("-" * 70)
    print(result["content"][:1000])
    print("-" * 70)
    print(f"\nContent Preview (middle section):")
    print("-" * 70)
    mid_point = len(result["content"]) // 2
    print(result["content"][mid_point:mid_point + 500])
    print("-" * 70)

    assert result["url"] == test_url
    assert len(result["content"]) > 0

    print("\n✓ Test passed!")
    print("=" * 70)


if __name__ == "__main__":
    print("Starting Web Scraper Test...")

    try:
        test_single_url()

        print("\n" + "=" * 70)
        print("TEST COMPLETED SUCCESSFULLY! ✓")
        print("=" * 70)

    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
