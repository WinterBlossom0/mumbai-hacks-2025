# Truth Lens — Architecture & Impact Traces

> **For AI agents:** Every section lists what each component depends on and what breaks if it changes. Follow these traces before modifying any file.

---

## Directory Map

```
mumbai-hacks-2025/
├── .env                     ← secrets (never commit)
├── .env.example             ← template — all keys documented here
├── ARCHITECTURE.md          ← this file
├── run.py                   ← dev launcher (backend + frontend + reddit monitor)
├── venv/                    ← Python virtualenv (created by uv)
├── backend/
│   ├── config.py            ← SINGLE source of truth for all env vars
│   ├── api/
│   │   ├── main.py          ← FastAPI app factory + router mounting
│   │   └── routers/
│   │       ├── verify.py    ← POST /api/verify, toggle-public, vote
│   │       ├── history.py   ← GET  /api/history/{user_id}
│   │       ├── public.py    ← GET  /api/public-feed, /api/top-headlines
│   │       └── reddit.py    ← GET  /api/reddit-posts, reddit-community, community-archives
│   ├── main/
│   │   ├── claim_extractor/ ← SMALL_MODEL: extracts claims from text/URLs
│   │   ├── claim_discoverer/← Tavily: finds source URLs per claim (+ rewritten queries)
│   │   ├── summarizer/      ← MEDIUM_MODEL: sliding-window doc summary
│   │   ├── rewriter/        ← SMALL_MODEL: rewrites claims → 2 Tavily queries each
│   │   ├── reasoning/       ← BIG_MODEL: final verdict + per-claim statuses
│   │   ├── categorizer/     ← SMALL_MODEL: classifies claims into category
│   │   ├── headline/        ← SMALL_MODEL: generates spicy headline
│   │   └── web_scraper/     ← Tavily extract + BS4 fallback
│   ├── database/
│   │   └── supabase_client.py ← all DB operations (single class)
│   ├── reddit/
│   │   ├── monitor.py       ← streams r/eyeoftruth, auto-moderates posts
│   │   └── feed_retriever.py← read-only browse of any subreddit
│   └── image_retrieve/
│       └── image_searcher.py← Tavily image search for public feed cards
└── frontend/
    ├── src/
    │   ├── lib/api.ts        ← fetchAPI() — single HTTP client for all API calls
    │   ├── app/
    │   │   ├── page.tsx      ← homepage: hero + feed
    │   │   ├── verify/       ← fact-check input form
    │   │   ├── history/      ← per-user verification history
    │   │   └── reddit/       ← Reddit posts + community browse
    │   └── components/
    │       ├── PublicFeed.tsx ← fetches /api/public-feed
    │       ├── NewsTicker.tsx ← fetches /api/top-headlines
    │       ├── CategoryFilter.tsx
    │       ├── Navbar.tsx
    │       └── CustomCursor.tsx
    └── package.json
```

---

## Data Flow — Verification Pipeline

```
User input (text or URL)
        │
        ▼
[ClaimExtractor]   ── SMALL_MODEL ──► { claims[], raw_text }
        │
        ▼
[Summarizer]       ── MEDIUM_MODEL ─► document_summary  (sliding-window, gpt-4.1-mini 1M ctx)
        │                               concise ~300-word fact-dense summary
        ▼
[ClaimRewriter]    ── SMALL_MODEL ──► { claim → [query_a, query_b] }
        │                               2 search queries per claim for broader coverage
        ▼
[ClaimDiscoverer.discover_sources_from_queries]
        │  ── Tavily Search ──► { claim → [deduped_urls] }  (2× Tavily calls per claim)
        ▼
[ClaimExtractor.extract_website_claims]
        │  scrapes each URL (WebScraper → Tavily extract / BS4)
        │  extracts claims from each page (SMALL_MODEL)
        ▼
{ url → [website_claims] }
        │
        ▼
[ClaimReasoner]    ── BIG_MODEL ────► { verdict, reasoning, annotated_claims[] }
        │                               each claim: CONFIRMED_TRUE | CONFIRMED_FALSE | UNCONFIRMED
        ▼
[SupabaseClient.save_verification]
        │
        ▼
  API response → Frontend /verify page
                 ClaimsList renders highlight colours (green/red/yellow)
```

---

## Model Routing

| Env Var | Default | Used by |
|---|---|---|
| `SMALL_MODEL` | `gpt-5.4-nano` | ClaimExtractor, ClaimCategorizer, HeadlineGenerator, ClaimRewriter — `reasoning_effort=medium` |
| `MEDIUM_MODEL` | `gpt-5.4-mini` | Summarizer (1M token context window) — `reasoning_effort=medium` |
| `BIG_MODEL` | `gpt-5.4` | ClaimReasoner — `reasoning_effort=xhigh` |

> Changing `SMALL_MODEL` → affects extraction quality and categorization.  
> Changing `BIG_MODEL` → affects verdict accuracy and reasoning depth.  
> Both read from `backend/config.py → Settings`.

---

## Component Impact Traces

### `backend/config.py`
- **Imported by:** every single backend module
- **Depends on:** `.env` file at project root
- **If you rename a key here:** grep for `settings.<KEY>` and update all consumers

### `backend/api/main.py`
- **Role:** composition root — mounts routers, starts Reddit monitor thread
- **If you add a new router:** import it here and call `app.include_router(...)`
- **If CORS changes:** affects all frontend → backend requests

### `backend/api/routers/verify.py`
- **Endpoints:** `POST /api/verify`, `POST /api/toggle-public/{id}`, `POST /api/vote`
- **Pipeline order (must not reorder):**
  1. ClaimExtractor → 2. ClaimDiscoverer → 3. ClaimExtractor.extract_website_claims → 4. ClaimReasoner → 5. SupabaseClient.save_verification
- **Frontend callers:** `/verify` page, `/history` page (toggle), feed cards (vote)

### `backend/api/routers/history.py`
- **Endpoints:** `GET /api/history/{user_id}`
- **Frontend callers:** `src/app/history/page.tsx`

### `backend/api/routers/public.py`
- **Endpoints:** `GET /api/public-feed`, `GET /api/top-headlines`
- **Frontend callers:** `PublicFeed.tsx`, `NewsTicker.tsx`

### `backend/api/routers/reddit.py`
- **Endpoints:** `GET /api/reddit-posts`, `GET /api/reddit-community`, `GET /api/community-archives`
- **Frontend callers:** `src/app/reddit/page.tsx`

### `backend/main/claim_extractor/claim_extractor.py`
- **Called by:** `routers/verify.py`, `reddit/monitor.py`
- **Depends on:** `settings.SMALL_MODEL`, `settings.OPENAI_API_KEY`, `WebScraper`
- **If chunking logic changes:** token counts and parallel execution budget change
- **Downstream effect:** all claim lists fed into ClaimDiscoverer and ClaimReasoner change

### `backend/main/claim_discoverer/claim_discoverer.py`
- **Called by:** `routers/verify.py`, `reddit/monitor.py`
- **Depends on:** `settings.TAVILY_API_KEY`
- **If `max_results` changes:** number of sources per claim changes → affects evidence quality
- **Downstream effect:** URL list passed to `extract_website_claims` changes

### `backend/main/reasoning/reasoning.py`
- **Called by:** `routers/verify.py`, `reddit/monitor.py`
- **Depends on:** `settings.BIG_MODEL`, `settings.OPENAI_API_KEY`
- **This is the FINAL step** — its output (`verdict`, `reasoning`, `annotated_claims`) is returned to the user
- **Per-claim statuses:** each claim gets `CONFIRMED_TRUE` / `CONFIRMED_FALSE` / `UNCONFIRMED` via unique markers `««CONFIRMED_TRUE»»` etc. that cannot appear in natural text
- **If the prompt changes:** verdict strictness AND per-claim colours in frontend change; re-evaluate test cases

### `frontend/src/components/ClaimsList.tsx`
- **Used by:** `verify/page.tsx`, `history/page.tsx`, `PublicFeed.tsx` (modal), `app/page.tsx` (hero)
- **Props:** `annotatedClaims` (preferred) or `claims` (fallback plain list); `compact` for tighter rows
- **Rendering:** claim text highlighted in status colour — no dots, no badges
  - `CONFIRMED_TRUE` → green text on green tinted row
  - `CONFIRMED_FALSE` → red text on red tinted row
  - `UNCONFIRMED` → yellow text on yellow tinted row
- **If changed:** claim display changes everywhere simultaneously

### `backend/main/summarizer/summarizer.py`
- **Called by:** `api/routers/verify.py`, `reddit/monitor.py`
- **Depends on:** `settings.MEDIUM_MODEL` (gpt-4.1-mini, 1M token ctx), `settings.OPENAI_API_KEY`
- **Algorithm:** sliding-window — `summary[t] = merge(summary[t-1], chunk[t])`; target ~300 words per summary
- **Output:** passed directly to `ClaimRewriter.rewrite_claims(summary, claims)`
- **If changed:** all downstream search query quality changes

### `backend/main/rewriter/rewriter.py`
- **Called by:** `api/routers/verify.py`, `reddit/monitor.py`
- **Depends on:** `settings.SMALL_MODEL`, `settings.OPENAI_API_KEY`, Summarizer output
- **Output:** `{claim: [query_a, query_b]}` — two search angles per claim
  - Query A: direct factual lookup (numbers, names, dates)
  - Query B: verification/cross-reference angle
- **Consumed by:** `ClaimDiscoverer.discover_sources_from_queries()`
- **Separator marker:** `««QUERY_SEP»»` (cannot appear in natural text)
- **If changed:** search coverage and evidence breadth change for all verifications

### `backend/main/categorizer/categorizer.py`
- **Called by:** `routers/verify.py` (toggle-public only)
- **Depends on:** `settings.SMALL_MODEL`, `settings.OPENAI_API_KEY`
- **Output stored in:** `verifications.category` column
- **Used by frontend:** `CategoryFilter.tsx` filters on this value

### `backend/main/headline/generator.py`
- **Called by:** `routers/verify.py` (toggle-public), `reddit/monitor.py`
- **Depends on:** `settings.SMALL_MODEL`, `settings.OPENAI_API_KEY`
- **Output stored in:** `verifications.headline`, `reddit_posts.headline`
- **Used by frontend:** `NewsTicker.tsx`, `PublicFeed.tsx` display this

### `backend/main/web_scraper/web_scraper.py`
- **Called by:** `ClaimExtractor._process_single_url`, `ClaimExtractor.extract_claims_from_url`
- **Depends on:** `settings.TAVILY_API_KEY`
- **Fallback:** BeautifulSoup if Tavily extract fails
- **If changed:** all URL-scraping in both user verification and Reddit processing is affected

### `backend/database/supabase_client.py`
- **Called by:** all routers, `reddit/monitor.py`
- **Depends on:** `settings.SUPABASE_URL`, `settings.SUPABASE_KEY`
- **Tables:** `verifications`, `ratings`, `reddit_posts`, `community_archives`
- **If schema changes:** update method signatures here AND the SQL migration files in `database/*.sql`

### `backend/reddit/monitor.py`
- **Entry points:** `run.py` (subprocess), `api/main.py` (daemon thread on startup)
- **Pipeline:** same as verification pipeline + auto-moderation (approve/remove posts)
- **Link extraction fix:** if post body contains a URL → scrapes URL first; else uses title+body text
- **If subreddit name changes:** update `self.subreddit_name`

### `backend/reddit/feed_retriever.py`
- **Called by:** `routers/reddit.py` (`/api/reddit-community`)
- **Depends on:** `settings.REDDIT_CLIENT_ID/SECRET/USER_AGENT`
- **Read-only** — does not write to DB

### `backend/image_retrieve/image_searcher.py`
- **Called by:** `routers/verify.py` (toggle-public)
- **Depends on:** `settings.TAVILY_API_KEY`
- **Output stored in:** `verifications.image_url`
- **Used by frontend:** `PublicFeed.tsx` card images

---

## Frontend → Backend API Map

| Frontend file | HTTP call | Backend router |
|---|---|---|
| `src/app/verify/page.tsx` | `POST /api/verify` | `routers/verify.py` |
| `src/app/history/page.tsx` | `GET /api/history/{id}` | `routers/history.py` |
| `src/app/history/page.tsx` | `POST /api/toggle-public/{id}` | `routers/verify.py` |
| `src/components/PublicFeed.tsx` | `GET /api/public-feed` | `routers/public.py` |
| `src/components/NewsTicker.tsx` | `GET /api/top-headlines` | `routers/public.py` |
| `src/app/page.tsx` | `POST /api/vote` | `routers/verify.py` |
| `src/app/reddit/page.tsx` | `GET /api/reddit-posts` | `routers/reddit.py` |
| `src/app/reddit/page.tsx` | `GET /api/reddit-community` | `routers/reddit.py` |

All requests go through `src/lib/api.ts → fetchAPI()` which reads `NEXT_PUBLIC_API_URL`.

---

## Environment Variables Quick Reference

```
SMALL_MODEL          → lightweight agents (extraction, categorization, headline, rewriter)
MEDIUM_MODEL         → summarizer — needs large context window (gpt-4.1-mini = 1M tokens)
BIG_MODEL            → final synthesis / verdict agent (reasoning)
OPENAI_API_KEY       → all LLM calls
TAVILY_API_KEY       → web search + URL scraping + image search
NEXT_PUBLIC_API_URL  → frontend base URL for API (default: http://localhost:8000)
SUPABASE_URL         → DB host
SUPABASE_KEY         → DB anon key
YOUR_CLIENT_ID       → Reddit app client ID
YOUR_CLIENT_SECRET   → Reddit app client secret
YOUR_USERNAME        → Reddit bot username
YOUR_PASSWORD        → Reddit bot password
REDDIT_USER_AGENT    → Reddit API user agent string
```

---

## How to Add a New Agent

1. Create `backend/main/<agent_name>/<agent_name>.py`
2. Import `from config import settings` — never call `os.getenv` directly
3. Add an `IMPACT TRACE` docstring to the class
4. If it uses a model: use `settings.SMALL_MODEL` or `settings.BIG_MODEL`
5. If it adds a new endpoint: create `backend/api/routers/<domain>.py` and mount in `api/main.py`
6. Update this file's directory map and data flow diagram
