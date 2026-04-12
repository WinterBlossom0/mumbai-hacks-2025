"""
Auto-ping service — prevents Render.com free tier sleep by pinging services every 10 min.

=============================================================
IMPACT TRACE
=============================================================
FILE: utils/auto_ping.py
LAST UPDATED: created with change: "auto-ping for Render free tier"

WHAT THIS FILE DOES:
  Runs a background thread that pings configured URLs every 10 minutes.
  Prevents Render.com free tier services from sleeping after 15 min inactivity.
  Logs success/failure for monitoring.

BEHAVIOR CONTRACTS:
  • start_auto_ping(urls: List[str], interval_minutes: int = 10) -> None
      Starts daemon thread that GETs each URL every interval_minutes.
      Non-blocking, runs forever until process exits.
      Logs ping results to stdout.

PROVIDES TO OTHER FILES:
  → api/main.py  |  start_auto_ping() called on startup

NEEDS FROM OTHER FILES:
  (none — self-contained)

IMPACT: If this file changes, it directly affects:
  ⚡ api/main.py  — startup event must call this to activate pinging

ASSUMPTIONS THIS FILE MAKES:
  - URLs provided are publicly accessible
  - 10 min interval keeps Render free tier awake (15 min sleep timeout)
  - One successful ping per interval is sufficient
=============================================================
"""

import threading
import time
import urllib.request
import urllib.error
from typing import List


def _ping_url(url: str) -> bool:
    """Ping a single URL, return True if successful."""
    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'TruthLens-AutoPing/1.0'},
            method='GET'
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            status = response.status
            print(f"[AutoPing] ✓ {url} -> {status}")
            return status == 200
    except Exception as e:
        print(f"[AutoPing] ✗ {url} -> ERROR: {e}")
        return False


def _ping_loop(urls: List[str], interval_seconds: int):
    """Background loop that pings URLs forever."""
    print(f"[AutoPing] Started: pinging {len(urls)} URL(s) every {interval_seconds//60} minutes")
    
    # Initial ping immediately on startup
    for url in urls:
        _ping_url(url)
    
    while True:
        time.sleep(interval_seconds)
        print(f"[AutoPing] Running scheduled ping...")
        for url in urls:
            _ping_url(url)


def start_auto_ping(
    urls: List[str] = None,
    interval_minutes: int = 10
) -> None:
    """
    Start auto-ping service in daemon thread.
    
    Args:
        urls: List of URLs to ping. Defaults to production Render URLs.
        interval_minutes: Ping interval in minutes (default: 10)
    """
    # Default production URLs
    if urls is None:
        urls = [
            "https://voidtruth.onrender.com/api/health",      # Backend
            "https://voidtruth-frontend.onrender.com",        # Frontend
        ]
    
    interval_seconds = interval_minutes * 60
    
    thread = threading.Thread(
        target=_ping_loop,
        args=(urls, interval_seconds),
        daemon=True,
        name="AutoPing"
    )
    thread.start()
    print(f"[AutoPing] Daemon thread started (interval: {interval_minutes} min)")
