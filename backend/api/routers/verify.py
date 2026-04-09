"""
Verification router — core fact-checking pipeline.

IMPACT TRACE:
  ╔══════════════════════════════════════════════════════════════════════╗
  ║                        UPSTREAM (What calls this)                      ║
  ╠══════════════════════════════════════════════════════════════════════╣
  ║  • POST /api/verify                                                    ║
  ║    - frontend/src/app/verify/page.tsx (manual verify)                  ║
  ║    - frontend/src/app/reddit/page.tsx (auto-verify via ?auto=true)       ║
  ║  • Reddit Monitor: backend/reddit/monitor.py (auto-processes posts)     ║
  ╚══════════════════════════════════════════════════════════════════════╝

  ╔══════════════════════════════════════════════════════════════════════╗
  ║                      DOWNSTREAM (What this calls)                      ║
  ╠══════════════════════════════════════════════════════════════════════╣
  ║  Step 1: ClaimExtractor.extract_claims() / extract_claims_from_url()    ║
  ║          ↓                                                            ║
  ║  Step 2: Summarizer.summarise()                                        ║
  ║          ↓                                                            ║
  ║  Step 3: ClaimRewriter.rewrite_claims()                                ║
  ║          ↓                                                            ║
  ║  Step 4: ClaimDiscoverer.discover_sources_from_queries()                ║
  ║          ↓                                                            ║
  ║  Step 5: ClaimExtractor.extract_website_claims()                       ║
  ║          ↓                                                            ║
  ║  Step 6: ClaimReasoner.reason_all_claims()                               ║
  ║          ↓                                                            ║
  ║  Step 7: SupabaseClient.save_verification() / save_community_archive()    ║
  ╚══════════════════════════════════════════════════════════════════════╝

  ╔══════════════════════════════════════════════════════════════════════╗
  ║                DATA FLOW GAPS (What I missed initially)                  ║
  ╠══════════════════════════════════════════════════════════════════════╣
  ║  Reddit Post Types:                                                    ║
  ║    • Link post (is_self=False, url=external) → URL pipeline            ║
  ║    • Self post (is_self=True, selftext=body) → text pipeline           ║
  ║                                                                        ║
  ║  Backend handlers:                                                     ║
  ║    • monitor.py: lines 152-171 — CORRECTLY handles both types            ║
  ║    • verify.py: relies on input_type from frontend                      ║
  ║                                                                        ║
  ║  DATABASE SCHEMA MISMATCH:                                              ║
  ║    • reddit_posts table: has 'url' column (for monitor.py posts)        ║
  ║    • community_archives table: MISSING 'url' column (for verify page)      ║
  ║    • RedditPost Pydantic model: has 'url' field                         ║
  ║    • Community archives API: no Pydantic model defined!                 ║
  ║                                                                        ║
  ║  FRONTEND DATA INCONSISTENCY:                                           ║
  ║    • /api/reddit-posts: returns RedditPost (has url)                    ║
  ║    • /api/reddit-community: returns raw dict (has is_self, url)         ║
  ║    • /api/community-archives: returns raw dict (has url now)            ║
  ║    • RedditCard receives: id, title, body, url, is_self?                ║
  ╚══════════════════════════════════════════════════════════════════════╝

  ╔══════════════════════════════════════════════════════════════════════╗
  ║                      SIDE EFFECTS & EXTERNAL IO                         ║
  ╠══════════════════════════════════════════════════════════════════════╣
  ║  • OpenAI API:    3+ calls (extraction → summarization → reasoning)    ║
  ║  • Tavily API:    Source discovery                                     ║
  ║  • Web Scraping:  Fetches URLs found by Tavily                        ║
  ║  • Database:      Inserts to verifications + community_archives       ║
  ╚══════════════════════════════════════════════════════════════════════╝

  BREAKING CHANGES:
    • Changing VerifyRequest/VerifyResponse schema → breaks frontend types
    • Removing reddit_id/subreddit/author params → breaks Reddit auto-verify flow
    • Changing pipeline order → affects all verification results
    • Changing save_community_archive() signature → breaks all callers
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


import traceback
import time

def log_trace(step: str, details: dict = None):
    """Structured trace logging for debugging verification flow."""
    timestamp = time.strftime("%H:%M:%S")
    trace = f"[TRACE:{timestamp}] {step}"
    if details:
        trace += f" | {details}"
    print(trace)

@router.post("/verify", response_model=VerifyResponse)
async def verify_content(request: VerifyRequest):
    """Verify content (text or URL) for misinformation."""
    trace_id = f"verify_{int(time.time()*1000)}"
    try:
        log_trace("VERIFY_START", {
            "trace_id": trace_id,
            "input_type": request.input_type,
            "has_reddit_id": bool(request.reddit_id),
            "content_preview": request.content[:80] + "..." if len(request.content) > 80 else request.content
        })
        print(f"\n{'='*70}")
        print(f"Processing {request.input_type}: {request.content[:100]}...")
        print(f"{'='*70}\n")

        extractor = ClaimExtractor(max_tokens_per_chunk=15000)

        # Step 1: Extract claims + raw text
        log_trace("STEP1_CLAIM_EXTRACTION", {"input_type": request.input_type})
        if request.input_type == "url":
            result = extractor.extract_claims_from_url(request.content, key_name="user")
        else:
            result = extractor.extract_claims(request.content, key_name="user")

        if not result["user"]:
            log_trace("STEP1_FAILED", {"reason": "no_claims_extracted"})
            raise HTTPException(status_code=400, detail="No claims could be extracted from the content")

        log_trace("STEP1_COMPLETE", {"claims_count": len(result["user"]), "claims": result["user"][:3]})

        # Step 2: Summarise the source text (sliding window, MEDIUM_MODEL)
        log_trace("STEP2_SUMMARIZATION")
        raw_text = result.get("raw_text", request.content)
        summarizer = Summarizer()
        document_summary = summarizer.summarise(raw_text)
        log_trace("STEP2_COMPLETE", {"summary_length": len(document_summary)})

        # Step 3: Rewrite claims into 2-candidate search queries (SMALL_MODEL)
        print("[Pipeline] Rewriting claims into search queries ...")
        rewriter = ClaimRewriter()
        rewritten = rewriter.rewrite_claims(document_summary, result["user"])
        for claim, queries in rewritten.items():
            print(f"  Claim: {claim[:60]}")
            print(f"    Q_A: {queries[0]}")
            print(f"    Q_B: {queries[1]}")

        # Step 4: Discover sources via rewritten query pairs
        log_trace("STEP4_SOURCE_DISCOVERY")
        discoverer = ClaimDiscoverer()
        sources = discoverer.discover_sources_from_queries(rewritten)

        all_urls = list(set(url for urls in sources.values() for url in urls))
        all_urls = all_urls[:settings.TAVILY_MAX_URLS]  # capped to 2 in test mode
        log_trace("STEP4_COMPLETE", {"sources_found": len(sources), "urls_capped": len(all_urls)})
        if not all_urls:
            log_trace("STEP4_FAILED", {"reason": "no_sources"})
            raise HTTPException(status_code=400, detail="No sources discovered. Please check your Tavily API key.")

        # Step 5: Scrape & extract claims from each source URL
        log_trace("STEP5_WEBSITE_CLAIMS", {"urls_to_scrape": len(all_urls)})
        website_claims = extractor.extract_website_claims(all_urls, result["user"])
        all_website_claims_flat = {url: claims for url, claims in website_claims.items() if claims}

        log_trace("STEP5_COMPLETE", {"websites_with_claims": len(all_website_claims_flat)})

        if not all_website_claims_flat:
            log_trace("STEP5_FAILED", {"reason": "no_credible_sources"})
            raise HTTPException(status_code=400, detail="No credible sources found for verification.")

        log_trace("STEP6_REASONING")
        reasoner = ClaimReasoner()
        final_result = reasoner.reason_all_claims(result["user"], all_website_claims_flat, original_text=raw_text)
        # Coerce None → False so Pydantic bool field never rejects the response
        if final_result.get("verdict") is None:
            final_result["verdict"] = False
        log_trace("STEP6_COMPLETE", {"verdict": final_result["verdict"], "reasoning_length": len(final_result.get("reasoning", ""))})
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
            log_trace("ARCHIVE_REDDIT_POST", {"reddit_id": request.reddit_id, "subreddit": request.subreddit})
            headline = None
            try:
                headline_gen = HeadlineGenerator()
                headline = headline_gen.generate_headline(result["user"])
            except Exception as e:
                print(f"Error generating headline for archive: {e}")
                headline = request.content[:100] + "..."

            # Determine URL for link posts
            post_url = request.content if request.input_type == "url" else None

            db.save_community_archive(
                reddit_id=request.reddit_id,
                title=headline or request.content[:100],
                body=request.content,
                url=post_url,
                subreddit=request.subreddit,
                verdict=final_result["verdict"],
                reasoning=final_result["reasoning"],
                claims=result["user"],
                sources=sources,
                image_url=None,
                author=request.author,
            )

        log_trace("VERIFY_SUCCESS", {"verification_id": verification_id, "verdict": final_result["verdict"]})

        return VerifyResponse(
            verification_id=verification_id,
            verdict=final_result["verdict"],
            reasoning=final_result["reasoning"],
            claims=result["user"],
            sources=sources,
            website_claims=all_website_claims_flat,
        )

    except HTTPException as he:
        log_trace("VERIFY_HTTP_ERROR", {"status": he.status_code, "detail": str(he.detail)})
        raise
    except Exception as e:
        log_trace("VERIFY_ERROR", {"error": str(e)})
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
