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
  Startup: launches RedditMonitor + AutoPing daemon threads
  If changed: server startup, CORS, or router prefixes affect all API consumers.

  STARTUP SERVICES:
    • RedditMonitor (daemon) → auto-processes Reddit posts from r/eyeoftruth
    • AutoPing (daemon)    → pings Render URLs every 10 min to prevent sleep
      - Pings: https://voidtruth.onrender.com/api/health
      - Pings: https://voidtruth-frontend.onrender.com
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
    
    # Start Reddit monitor
    thread = threading.Thread(target=_run_reddit_monitor, daemon=True)
    thread.start()
    
    # Start auto-ping to keep Render free tier services awake
    # Only runs in production (Render), not locally
    import os
    if os.getenv('RENDER', '0') == '1' or os.getenv('ENVIRONMENT') == 'production':
        from utils.auto_ping import start_auto_ping
        start_auto_ping(interval_minutes=10)
        print("[AutoPing] Enabled for production (Render)")
    else:
        print("[AutoPing] Skipped (not production)")


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
