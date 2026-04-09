# Truth Lens — IMPACT MAP

**This document maps cause-and-effect relationships across the codebase.**

When modifying any component, use this map to understand:
1. What else will be affected (downstream)
2. What you might break (upstream dependencies)
3. Data contracts that must be maintained

---

## 🔄 Core Verification Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         VERIFICATION FLOW                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  User Input ──┬──→ verify/page.tsx ──→ /api/verify ──→ ClaimExtractor   │
│               │                                        (Step 1)          │
│  Reddit Post ─┘                                                        │
│                                                                          │
│  ↓ Summarizer (Step 2)                                                  │
│  ↓ ClaimRewriter (Step 3)                                               │
│  ↓ ClaimDiscoverer → Tavily API (Step 4)                                  │
│  ↓ extract_website_claims → Web Scraping (Step 5)                       │
│  ↓ ClaimReasoner → OpenAI (Step 6)                                      │
│  ↓ SupabaseClient.save_* (Step 7)                                       │
│                                                                          │
│  → ReasoningText.tsx (renders reasoning)                                 │
│  → ClassifiedInput.tsx (renders classified text)                         │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Dependency Matrix

### Backend → Backend

| From | To | Data/Contract | Breaking Changes |
|------|-----|---------------|------------------|
| `verify.py` | `ClaimExtractor` | calls `extract_claims()` or `extract_claims_from_url()` | Changing return format breaks Step 1 |
| `verify.py` | `ClaimReasoner` | calls `reason_all_claims()` | Changing response format breaks all reasoning display |
| `monitor.py` | Same pipeline as verify.py | identical flow | Same as verify.py |
| `ClaimReasoner` | Supabase DB | stores `reasoning` field with markers | Marker format change breaks frontend |

### Backend → Frontend

| From | To | Data/Contract | Breaking Changes |
|------|-----|---------------|------------------|
| `/api/verify` | `verify/page.tsx` | `VerifyResponse` JSON | Schema change breaks UI |
| `/api/reddit-posts` | `reddit/page.tsx` | `RedditPost` array | Schema change breaks Reddit feed |
| `reasoning` field | `ReasoningText.tsx` | Markers: `««TRUE_START»»` etc | Marker format change breaks highlighting |
| `reasoning` field | `ClassifiedInput.tsx` | `__CLASSIFIED_INPUT__` sentinel | Removing sentinel breaks classification |

### Frontend → Frontend

| From | To | Data/Contract | Breaking Changes |
|------|-----|---------------|------------------|
| `reddit/page.tsx` | `verify/page.tsx` | `?text=...&reddit_id=...&auto=true` | URL format change breaks auto-verify |
| `verify/page.tsx` | Reasoning components | `result.reasoning`, `result.claims` | Prop change breaks child components |

---

## 🔗 Critical Data Contracts

### 1. Marker Format (REASONING → ReasoningText)
```
Format: ««TYPE_START»»text««TYPE_END»»
Types: TRUE, FALSE, UNCONFIRMED

Example: ««TRUE_START»»claim text here««TRUE_END»»

If this changes → Update ReasoningText.tsx parseSegments()
```

### 2. Classified Input Sentinel (REASONING → ClassifiedInput)
```
Sentinel: __CLASSIFIED_INPUT__

Splits reasoning into:
  - Part 1: AI reasoning with markers
  - Part 2: Classified original text

If removed → ClassifiedInput.tsx cannot render
```

### 3. Reddit Auto-Verify URL Format
```
URL: /verify?text={title+body}&reddit_id={id}&subreddit={sub}&author={author}&auto=true

If format changes → reddit/page.tsx RedditCard breaks
```

### 4. VerifyRequest Schema
```python
{
  input_type: "text" | "url",  # Changing values breaks detection
  content: string,             # Must be text or URL
  reddit_id?: string,          # If missing → won't archive
  subreddit?: string,
  author?: string
}
```

---

## 🚨 Breaking Change Hotspots

### 1. `backend/main/reasoning/reasoning.py`
**Risk Level: 🔴 CRITICAL**
- Marker format used by all frontend display
- Prompt changes affect verdict accuracy
- 2 upstream callers (verify.py, monitor.py)

### 2. `backend/api/routers/verify.py`
**Risk Level: 🔴 CRITICAL**
- Entry point for ALL verifications
- 2 upstream callers (manual, Reddit auto)
- 7 downstream pipeline steps
- Schema change breaks frontend

### 3. `frontend/src/components/ReasoningText.tsx`
**Risk Level: 🟡 HIGH**
- Parser must match backend marker format
- Used by 4+ pages (verify, reddit, history, feed)
- Breaking change affects all reasoning display

### 4. `backend/reddit/monitor.py`
**Risk Level: 🟡 HIGH**
- Auto-moderation logic
- Changing verdict logic affects post removal/approval
- Same pipeline as verify.py (any change cascades)

---

## 📁 Files with IMPACT TRACE Annotations

### Backend
- [x] `backend/api/routers/verify.py`
- [x] `backend/reddit/monitor.py`
- [x] `backend/main/reasoning/reasoning.py`
- [x] `backend/main/claim_extractor/claim_extractor.py`
- [x] `backend/database/supabase_client.py`

### Frontend
- [x] `frontend/src/app/verify/page.tsx`
- [x] `frontend/src/app/reddit/page.tsx`
- [x] `frontend/src/components/ReasoningText.tsx`

---

## 🎯 Quick Reference: Modifying Common Components

### Adding a new verification step
1. Add to `verify.py` → also add to `monitor.py`
2. Update IMPACT TRACE in both files
3. Update this IMPACT_MAP.md

### Changing marker format
1. Update `reasoning.py` → change marker constants
2. Update `ReasoningText.tsx` → change marker constants
3. Test with existing DB records (backward compatibility?)

### Modifying Reddit flow
1. Check `reddit/page.tsx` → verify button URL format
2. Check `verify/page.tsx` → URL detection logic
3. Check `monitor.py` → auto-moderation logic
4. All three must stay in sync

### Changing database schema
1. Update `supabase_client.py`
2. Update Pydantic models in `verify.py`, `reddit.py`
3. Update frontend types if exposed to UI

---

**Last Updated:** Auto-generated from IMPACT TRACE annotations
**Maintained by:** AI agents reading source code
