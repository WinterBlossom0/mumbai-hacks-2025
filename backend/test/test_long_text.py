import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main.claim_extractor import ClaimExtractor
from main.claim_discoverer import ClaimDiscoverer


def test_comprehensive_pipeline():
    """Test the complete pipeline: extract claims from long text, then discover sources."""
    print("\n=== Comprehensive Test: Claim Extraction + Source Discovery ===\n")
    
    # Use large chunk size for testing
    extractor = ClaimExtractor(max_tokens_per_chunk=15000)
    
    # Create a very long text focused on a SINGLE TOPIC: Climate Change
    long_text = """
Trump’s Ukraine peace plan trimmed to 19 points to drop Luhansk, Donetsk surrender — What's in it?

The United States and Ukraine have worked to bridge their differences over Donald Trump's 28-point peace plan to end the war, after Washington agreed to revise the earlier plan that Kyiv that was criticised as highly favourable to Moscow. After drafting the new plan, Washington and Kyiv said they had drafted a “refined peace framework”.

After the Geneva meeting, Zelensky said, “As of now, after Geneva, there are fewer points – no longer 28 – and many of the right elements have been taken into account in this framework. Our team has reported on the new draft of steps, and this is indeed the right approach – I will discuss the sensitive issues with President Trump.”

What does the new 19-point plan say?
The new plan, which has been cut down from 28 provisions to 19 now, has dropped one of the most contentious elements of Trump's peace proposal – a requirement that Ukraine surrender Luhansk and Donetsk, parts of the Donbas, to Russia, according to the New York Post.

Ukraine has called the provision to cede the Luhansk and Donetsk territories to Russia unacceptable.

According to the reports, Donald Trump and his Ukrainian counterpart Volodymyr Zelensky will meet on a later date to sort out the territorial issue. White House press secretary Karoline Leavitt has meanwhile asserted that Trump wants to seal the deal quickly but there was no meeting currently scheduled between the two leaders. Also Read | What changes for Putin and Zelensky in Trump's 28-point peace plan?

The media reports mention that the new 19-point plan would also remove the part where Ukraine is required to give up NATO hopes for the peace with Russia to prevail.

Zelensky has indicated that the updated plan now includes “correct” points – suggesting his government may be working to shape the proposal in favour of his country.

The old 28-point plan
The 28-point peace proposal had caught many in the US government, Kyiv and Europe off-guard and prompted fresh concerns that the Trump administration might be willing to push Ukraine to sign the peace deal heavily tilted towards Russia.

Countering the Trump-backed blueprint of the plan to end the Russia-Ukraine war, European allies of Zelensky drew up a counter-proposal, suggesting end to fighting at present front lines, and include a NATO-style US security guarantee for Ukraine.

Moscow rejected it. “The European plan, at first glance ... is completely unconstructive and does not work for us,” Kremlin foreign policy aide Yuri Ushakov said.

The old plan mentioned “recognition of Crimea and other regions [Luhansk and Donetsk] that the Russians have taken”, Ukraine cutting down its military more than half to 400,000-600,000 personnel, Kyiv giving up all long-range weapons, and no NATO security to Ukraine.

It also proposed that European fighter jets will be stationed in Poland and in case Russia invades Ukraine again, “all global sanctions will be reinstated, recognition of the new territory and all other benefits of this deal will be revoked.”

As for territories, “Crimea, Luhansk and Donetsk will be recognised as de facto Russian, including by the United States” and “Kherson and Zaporizhzhia will be frozen along the line of contact”

Russia is also required to relinquish other agreed territories it controls outside the five regions.
    """
    
    # Step 1: Extract claims
    print("STEP 1: EXTRACTING CLAIMS")
    print("="*70)
    result = extractor.extract_claims(long_text, key_name="user")
    
    print(f"\nTotal claims extracted: {len(result['user'])}\n")
    
    for i, claim in enumerate(result['user'], 1):
        print(f"{i}. {claim}")
    
    assert "user" in result
    assert isinstance(result["user"], list)
    assert len(result["user"]) > 0
    
    print("\n✓ Claim extraction successful!")
    
    # Step 2: Discover sources for the extracted claims
    print("\n" + "="*70)
    print("STEP 2: DISCOVERING SOURCES FOR CLAIMS")
    print("="*70 + "\n")
    
    discoverer = ClaimDiscoverer()
    sources = discoverer.discover_sources(result['user'])
    
    print("\n" + "="*70)
    print("DISCOVERED SOURCES (CLAIM → LINKS)")
    print("="*70 + "\n")
    
    for claim, links in sources.items():
        print(f"Claim: {claim}")
        print(f"Links ({len(links)}):")
        for link in links:
            print(f"  - {link}")
        print()
    
    assert isinstance(sources, dict)
    
    total_links = sum(len(links) for links in sources.values())
    
    print("="*70)
    print("FINAL RESULTS")
    print("="*70)
    print(f"Claims extracted: {len(result['user'])}")
    print(f"Claims with sources: {len(sources)}")
    print(f"Total sources discovered: {total_links}")
    print("="*70)
    
    # Step 3: Extract claims from ALL discovered websites
    print("\n" + "="*70)
    print("STEP 3: EXTRACTING CLAIMS FROM ALL WEBSITES")
    print("="*70 + "\n")
    
    all_website_claims = {}
    all_urls = []
    
    if result['user'] and sources:
        # Collect all unique URLs
        for urls in sources.values():
            all_urls.extend(urls)
        all_urls = list(set(all_urls))  # Remove duplicates
        
        print(f"\nExtracting claims from {len(all_urls)} unique website(s) for ALL original claims\n")
        
        # Extract website claims (passing all original claims at once)
        website_claims = extractor.extract_website_claims(all_urls, result['user'])
        
        # Organize by original claim
        for original_claim, urls in sources.items():
            all_website_claims[original_claim] = {
                url: website_claims.get(url, []) for url in urls
            }
        
        # Display results
        print("\n" + "="*70)
        print("WEBSITE CLAIMS ANALYSIS")
        print("="*70 + "\n")
        
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
        
        total_websites = sum(len(website_data) for website_data in all_website_claims.values())
        total_website_claims = sum(
            sum(len(claims) for claims in website_data.values())
            for website_data in all_website_claims.values()
        )
        
        print("="*70)
        print("COMPLETE PIPELINE RESULTS")
        print("="*70)
        print(f"Original claims extracted: {len(result['user'])}")
        print(f"Sources discovered: {total_links}")
        print(f"Total websites analyzed: {total_websites}")
        print(f"Total website claims extracted: {total_website_claims}")
        print("="*70)
        
        # Step 4: Reasoning with Gemini 2.5 Pro
        print("\n" + "="*70)
        print("STEP 4: REASONING WITH GEMINI 2.5 PRO")
        print("="*70 + "\n")
        
        from main.reasoning import ClaimReasoner
        
        reasoner = ClaimReasoner()
        
        # Collect all website claims into one dictionary
        all_website_claims_flat = {}
        for original_claim, website_data in all_website_claims.items():
            for url, claims in website_data.items():
                if url not in all_website_claims_flat:
                    all_website_claims_flat[url] = []
                all_website_claims_flat[url].extend(claims)
        
        print(f"Analyzing {len(result['user'])} user claims against {len(all_website_claims_flat)} sources...\n")
        
        # Get single overall verdict
        final_result = reasoner.reason_all_claims(result['user'], all_website_claims_flat)
        
        print("="*70)
        print("FINAL VERDICT")
        print("="*70)
        print(f"\nVERDICT: {'✓ TRUE' if final_result['verdict'] else '✗ FALSE'}")
        print(f"\nREASONING:\n{final_result['reasoning']}")
        print("\n" + "="*70)
    
    print("\n✓ Complete pipeline test passed!")


if __name__ == "__main__":
    print("="*70)
    print("COMPREHENSIVE PIPELINE TEST")
    print("Testing: Claim Extraction → Source Discovery")
    print("="*70)
    
    try:
        test_comprehensive_pipeline()
        print("\n" + "="*70)
        print("ALL TESTS PASSED SUCCESSFULLY! ✓")
        print("="*70)
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
