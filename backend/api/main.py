"""
FastAPI application entry point.

IMPACT TRACE:
  This file is the composition root for the backend.
  Routers mounted here:
    /api/verify, /api/toggle-public, /api/vote  → api/routers/verify.py
    /api/history                                 → api/routers/history.py
    /api/public-feed, /api/top-headlines         → api/routers/public.py
    /api/reddit-posts, /api/reddit-community,
    /api/community-archives                      → api/routers/reddit.py
  Startup: launches RedditMonitor in a daemon thread
  If changed: server startup, CORS, or router prefixes affect all API consumers.
"""
import sys
import threading
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.routers import verify, history, public, reddit as reddit_router

app = FastAPI(title="Misinformation Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(verify.router, prefix="/api")
app.include_router(history.router, prefix="/api")
app.include_router(public.router, prefix="/api")
app.include_router(reddit_router.router, prefix="/api")


def _run_reddit_monitor():
    print("Starting Reddit Monitor in background thread...")
    try:
        from reddit.monitor import RedditMonitor
        monitor = RedditMonitor()
        monitor.process_posts()
    except Exception as e:
        print(f"Reddit Monitor failed: {e}")


@app.on_event("startup")
async def startup_event():
    from config import settings
    mode = "TEST (gpt-5.4-mini everywhere, Tavily max_results=1, max 2 URLs)" if settings.TEST_MODE else "PRODUCTION (full models)"
    print(f"[Config] Mode: {mode}")
    thread = threading.Thread(target=_run_reddit_monitor, daemon=True)
    thread.start()


@app.get("/")
async def root():
    return {"message": "Truth Lens API", "status": "running", "version": "1.0.0"}


@app.get("/test")
async def test():
    return {"status": "ok", "message": "API is working!"}


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
