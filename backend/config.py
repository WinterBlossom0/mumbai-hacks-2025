"""
Central configuration — loads .env once and exposes typed settings.

IMPACT TRACE:
  Imported by: ALL agents, ALL routers, database/, reddit/
  Depends on:  .env at project root
  If changed:  Any rename of env var keys here affects every consumer.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

_env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=_env_path)


class Settings:
    # ── Test mode (injected by run.py via TRUTH_LENS_TEST_MODE=1) ────────
    # When True: BIG_MODEL → gpt-5.4-mini, Tavily max_results=1, max 2 URLs/claim
    # When False (direct uvicorn / production): full models and limits
    TEST_MODE: bool = os.getenv("TRUTH_LENS_TEST_MODE", "0") == "1"

    # ── Model routing ────────────────────────────────────────────────────
    SMALL_MODEL: str = os.getenv("SMALL_MODEL", "gpt-5.4-nano")
    MEDIUM_MODEL: str = os.getenv("MEDIUM_MODEL", "gpt-5.4-mini")
    # BIG_MODEL degrades to MEDIUM in test mode to cut cost
    BIG_MODEL: str = (
        os.getenv("MEDIUM_MODEL", "gpt-5.4-mini")
        if os.getenv("TRUTH_LENS_TEST_MODE", "0") == "1"
        else os.getenv("BIG_MODEL", "gpt-5.4")
    )

    # ── Tavily limits (reduced in test mode) ─────────────────────────────
    TAVILY_MAX_RESULTS: int = 1 if os.getenv("TRUTH_LENS_TEST_MODE", "0") == "1" else 3
    TAVILY_MAX_URLS: int = 2 if os.getenv("TRUTH_LENS_TEST_MODE", "0") == "1" else 999

    # ── OpenAI ───────────────────────────────────────────────────────────
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # ── Tavily ───────────────────────────────────────────────────────────
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")

    # ── Supabase ─────────────────────────────────────────────────────────
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

    # ── Reddit (PRAW) ────────────────────────────────────────────────────
    REDDIT_CLIENT_ID: str = os.getenv("YOUR_CLIENT_ID", "")
    REDDIT_CLIENT_SECRET: str = os.getenv("YOUR_CLIENT_SECRET", "")
    REDDIT_USERNAME: str = os.getenv("YOUR_USERNAME", "")
    REDDIT_PASSWORD: str = os.getenv("YOUR_PASSWORD", "")
    REDDIT_USER_AGENT: str = os.getenv("REDDIT_USER_AGENT", "TruthLens/1.0")


settings = Settings()
