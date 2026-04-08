"""
Verification router — core fact-checking pipeline.

IMPACT TRACE:
  Mounts at:   /api/verify, /api/toggle-public/{id}, /api/vote
  Pipeline:    ClaimExtractor → Summarizer → ClaimRewriter
               → ClaimDiscoverer.discover_sources_from_queries
               → ClaimExtractor.extract_website_claims → ClaimReasoner → SupabaseClient
               HeadlineGenerator, ClaimCategorizer, ImageSearcher (on toggle-public)
  If changed:  The primary user-facing verification flow is affected.
  Frontend callers:
    - /verify page  → POST /api/verify
    - /history page → POST /api/toggle-public/{id}
    - feed cards    → POST /api/vote
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from main.claim_extractor import ClaimExtractor
from main.claim_discoverer import ClaimDiscoverer
from main.reasoning import ClaimReasoner
from main.headline.generator import HeadlineGenerator
from main.categorizer import ClaimCategorizer
from main.summarizer import Summarizer
from main.rewriter import ClaimRewriter
from database.supabase_client import SupabaseClient
from image_retrieve.image_searcher import ImageSearcher
from config import settings

router = APIRouter()


class VerifyRequest(BaseModel):
    input_type: str
    content: str
    user_id: Optional[str] = "0"
    user_email: Optional[str] = "user0@gmail.com"
    reddit_id: Optional[str] = None
    subreddit: Optional[str] = None
    author: Optional[str] = None


class VerifyResponse(BaseModel):
    verification_id: str
    verdict: bool
    reasoning: str
    claims: List[str]
    sources: Dict[str, List[str]]
    website_claims: Dict[str, List[str]]


class VoteRequest(BaseModel):
    verification_id: str
    user_id: str
    vote_type: int


@router.post("/verify", response_model=VerifyResponse)
async def verify_content(request: VerifyRequest):
    """Verify content (text or URL) for misinformation."""
    try:
        print(f"\n{'='*70}")
        print(f"Processing {request.input_type}: {request.content[:100]}...")
        print(f"{'='*70}\n")

        extractor = ClaimExtractor(max_tokens_per_chunk=15000)

        # Step 1: Extract claims + raw text
        if request.input_type == "url":
            result = extractor.extract_claims_from_url(request.content, key_name="user")
        else:
            result = extractor.extract_claims(request.content, key_name="user")

        if not result["user"]:
            raise HTTPException(status_code=400, detail="No claims could be extracted from the content")

        print(f"Extracted {len(result['user'])} claims")

        # Step 2: Summarise the source text (sliding window, MEDIUM_MODEL)
        raw_text = result.get("raw_text", request.content)
        print("[Pipeline] Summarising source text ...")
        summarizer = Summarizer()
        document_summary = summarizer.summarise(raw_text)
        print(f"[Pipeline] Summary: {document_summary[:120]}...")

        # Step 3: Rewrite claims into 2-candidate search queries (SMALL_MODEL)
        print("[Pipeline] Rewriting claims into search queries ...")
        rewriter = ClaimRewriter()
        rewritten = rewriter.rewrite_claims(document_summary, result["user"])
        for claim, queries in rewritten.items():
            print(f"  Claim: {claim[:60]}")
            print(f"    Q_A: {queries[0]}")
            print(f"    Q_B: {queries[1]}")

        # Step 4: Discover sources via rewritten query pairs
        discoverer = ClaimDiscoverer()
        sources = discoverer.discover_sources_from_queries(rewritten)

        all_urls = list(set(url for urls in sources.values() for url in urls))
        all_urls = all_urls[:settings.TAVILY_MAX_URLS]  # capped to 2 in test mode
        if not all_urls:
            raise HTTPException(status_code=400, detail="No sources discovered. Please check your Tavily API key.")

        # Step 5: Scrape & extract claims from each source URL
        website_claims = extractor.extract_website_claims(all_urls, result["user"])
        all_website_claims_flat = {url: claims for url, claims in website_claims.items() if claims}

        print(f"Extracted claims from {len(all_website_claims_flat)} websites")

        if not all_website_claims_flat:
            raise HTTPException(status_code=400, detail="No credible sources found for verification.")

        reasoner = ClaimReasoner()
        final_result = reasoner.reason_all_claims(result["user"], all_website_claims_flat, original_text=raw_text)
        # Coerce None → False so Pydantic bool field never rejects the response
        if final_result.get("verdict") is None:
            final_result["verdict"] = False
        print(f"Final verdict: {final_result['verdict']}")

        db = SupabaseClient()
        saved_record = db.save_verification(
            user_id=request.user_id,
            user_email=request.user_email,
            input_content=request.content,
            input_type=request.input_type,
            verdict=final_result["verdict"],
            reasoning=final_result["reasoning"],
            claims=result["user"],
            sources=sources,
        )
        verification_id = saved_record.get("id", "")
        print(f"Saved to Supabase with ID: {verification_id}")

        if request.reddit_id and request.subreddit:
            print(f"Saving to Community Archive: {request.subreddit} - {request.reddit_id}")
            headline = None
            try:
                headline_gen = HeadlineGenerator()
                headline = headline_gen.generate_headline(result["user"])
            except Exception as e:
                print(f"Error generating headline for archive: {e}")
                headline = request.content[:100] + "..."

            db.save_community_archive(
                reddit_id=request.reddit_id,
                title=headline or request.content[:100],
                body=request.content,
                subreddit=request.subreddit,
                verdict=final_result["verdict"],
                reasoning=final_result["reasoning"],
                claims=result["user"],
                sources=sources,
                image_url=None,
                author=request.author,
            )

        return VerifyResponse(
            verification_id=verification_id,
            verdict=final_result["verdict"],
            reasoning=final_result["reasoning"],
            claims=result["user"],
            sources=sources,
            website_claims=all_website_claims_flat,
        )

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/toggle-public/{verification_id}")
async def toggle_public_status(verification_id: str, is_public: bool):
    """Toggle public visibility; generates headline, category, and image if missing."""
    try:
        db = SupabaseClient()
        headline = None
        category = None
        image_url = None

        if is_public:
            verification = db.get_verification_by_id(verification_id)
            if verification:
                claims = verification.get("claims", [])

                if not verification.get("headline"):
                    try:
                        generator = HeadlineGenerator()
                        claims_for_headline = claims or ([verification.get("input_content")] if verification.get("input_content") else [])
                        if claims_for_headline:
                            headline = generator.generate_headline(claims_for_headline)
                            print(f"Generated headline: {headline}")
                    except Exception as e:
                        print(f"Error generating headline: {e}")
                else:
                    headline = verification.get("headline")

                if not verification.get("category") and claims:
                    try:
                        categorizer = ClaimCategorizer()
                        category = categorizer.categorize_claims(claims)
                        print(f"Category: {category}")
                    except Exception as e:
                        print(f"Error categorizing claims: {e}")
                        category = "technology"
                else:
                    category = verification.get("category")

                if not verification.get("image_url"):
                    try:
                        searcher = ImageSearcher()
                        image_url = searcher.get_image_for_claims(claims) if claims else searcher.search_image(verification.get("input_content", "")[:200])
                        print(f"Found image: {image_url}")
                    except Exception as e:
                        print(f"Error searching for image: {e}")
                else:
                    image_url = verification.get("image_url")

        result = db.toggle_public_status(verification_id, is_public, headline, category, image_url)
        return {"success": result, "headline": headline, "category": category, "image_url": image_url}

    except Exception as e:
        print(f"Error toggling public status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/vote")
async def vote(request: VoteRequest):
    """Vote on a verification."""
    try:
        db = SupabaseClient()
        result = db.vote_verification(request.verification_id, request.user_id, request.vote_type)
        return result
    except Exception as e:
        print(f"Error voting: {e}")
        raise HTTPException(status_code=500, detail=str(e))
