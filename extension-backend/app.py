from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import sys
import os
from pathlib import Path

# Add backend directory to path to import shared modules
backend_dir = Path(__file__).parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Import after adding to path
import main.claim_extractor
import main.claim_discoverer
import main.reasoning
from main.claim_extractor import ClaimExtractor
from main.claim_discoverer import ClaimDiscoverer
from main.reasoning import ClaimReasoner
from database.supabase_client import SupabaseClient

app = FastAPI(title="Web Extension Misinformation Detection API")

# CORS middleware - Allow all origins for browser extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class VerifyRequest(BaseModel):
    input_type: str  # "text" or "url"
    content: str
    user_id: Optional[str] = "0"
    user_email: Optional[str] = "user0@gmail.com"


class VerifyResponse(BaseModel):
    verification_id: str
    verdict: bool
    reasoning: str
    claims: List[str]
    sources: Dict[str, List[str]]
    website_claims: Dict[str, List[str]]


@app.get("/")
async def root():
    return {
        "message": "Truth Lens Extension API",
        "status": "running",
        "version": "1.0.0",
        "port": 8001
    }


@app.get("/test")
async def test():
    """Simple test endpoint to verify API is working."""
    return {"status": "ok", "message": "Extension API is working!"}


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/api/verify", response_model=VerifyResponse)
async def verify_content(request: VerifyRequest):
    """
    Verify content (text or URL) for misinformation.
    """
    try:
        print(f"\n{'='*70}")
        # Safely print content avoiding UnicodeEncodeError on Windows
        safe_content = request.content[:100].encode('ascii', 'replace').decode('ascii')
        print(f"[EXTENSION] Processing {request.input_type}: {safe_content}...")
        print(f"{'='*70}\n")

        # Step 1: Extract claims
        extractor = ClaimExtractor(max_tokens_per_chunk=15000)

        if request.input_type == "url":
            result = extractor.extract_claims_from_url(request.content, key_name="user")
        else:
            result = extractor.extract_claims(request.content, key_name="user")

        if not result["user"]:
            raise HTTPException(
                status_code=400, detail="No claims could be extracted from the content"
            )

        print(f"[EXTENSION] Extracted {len(result['user'])} claims")

        # Step 2: Discover sources
        discoverer = ClaimDiscoverer()
        sources = discoverer.discover_sources(result["user"])

        total_links = sum(len(links) for links in sources.values())
        print(f"[EXTENSION] Discovered {total_links} sources")

        # Step 3: Extract website claims
        all_urls = []
        for urls in sources.values():
            all_urls.extend(urls)
        all_urls = list(set(all_urls))

        if not all_urls:
            raise HTTPException(
                status_code=400,
                detail="No sources discovered. Please check your Tavily API key."
            )
        
        website_claims = extractor.extract_website_claims(all_urls, result["user"])

        # Flatten website claims for response
        all_website_claims_flat = {}
        for url, claims in website_claims.items():
            if claims:
                all_website_claims_flat[url] = claims

        print(f"[EXTENSION] Extracted claims from {len(all_website_claims_flat)} websites")

        # Step 4: Reasoning
        if not all_website_claims_flat:
            raise HTTPException(
                status_code=400,
                detail="No credible sources found for verification. Please check your API keys and try again."
            )
        
        reasoner = ClaimReasoner()
        final_result = reasoner.reason_all_claims(result["user"], all_website_claims_flat)
        print(f"[EXTENSION] Final verdict: {final_result['verdict']}")

        # Save to Supabase
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
        print(f"[EXTENSION] Saved to Supabase with ID: {verification_id}")

        return VerifyResponse(
            verification_id=verification_id,
            verdict=final_result["verdict"],
            reasoning=final_result["reasoning"],
            claims=result["user"],
            sources=sources,
            website_claims=all_website_claims_flat,
        )

    except HTTPException as http_exc:
        # Re-raise HTTPExceptions with their original status code
        print(f"[EXTENSION] Error: {http_exc.detail}")
        raise http_exc
    except Exception as e:
        print(f"[EXTENSION] Unexpected error: {str(e)}")
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
