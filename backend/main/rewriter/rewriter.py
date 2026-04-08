"""
Claim rewriter — converts raw claims into optimised Tavily search queries.

How it works
------------
  For each claim the model receives:
    - The concise document summary (context)
    - The raw claim text

  It produces EXACTLY 2 candidate search queries separated by the unique
  marker  ««QUERY_SEP»»  which cannot appear in natural text.

  Two queries per claim cover different facets:
    Query A — direct factual lookup (who/what/when/number)
    Query B — contextual / verification angle (fact-check, source cross-ref)

  ClaimDiscoverer then uses BOTH queries, deduplicates URLs, and merges
  the combined source list — giving broader evidence coverage.

IMPACT TRACE:
  Called by:  api/routers/verify.py (replaces direct claim→Tavily search)
  Depends on: settings.SMALL_MODEL, settings.OPENAI_API_KEY, Summarizer output
  Output:     Dict[original_claim → List[2 rewritten queries]]
              consumed by ClaimDiscoverer.discover_sources_from_queries()
  If changed: search coverage and evidence quality change for ALL verifications
"""
import sys
from typing import List, Dict
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import settings

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


_QUERY_SEP = "««QUERY_SEP»»"


class ClaimRewriter:
    """
    Rewrites raw claims into 2-candidate search queries using document context.

    IMPACT TRACE:
      Called by:  api/routers/verify.py, reddit/monitor.py
      Depends on: settings.SMALL_MODEL, settings.OPENAI_API_KEY
      Input:      summary (str) from Summarizer, claims (List[str]) from ClaimExtractor
      Output:     {claim: [query_a, query_b]}  → fed to ClaimDiscoverer
      If changed: search query quality changes; re-check evidence recall
    """

    QUERY_SEP = _QUERY_SEP

    def __init__(self, model: str = None):
        model_name = model or settings.SMALL_MODEL
        self.llm = ChatOpenAI(
            model=model_name,
            openai_api_key=settings.OPENAI_API_KEY,
            temperature=0,
        )

        self._prompt = ChatPromptTemplate.from_messages([
            ("system",
             "You are a search-query specialist for a fact-checking system. "
             "Given a document summary (context) and a specific claim, produce "
             "EXACTLY 2 distinct search queries that together maximise evidence coverage:\n"
             "  Query A — direct factual lookup (specific numbers, names, dates, events)\n"
             "  Query B — verification / cross-reference angle (fact-check framing, "
             "             alternative sources, contradicting evidence)\n\n"
             "Rules:\n"
             "- Each query must be concise (≤12 words)\n"
             "- Queries must be meaningfully different — cover different facets\n"
             "- Use the context to add specificity (year, entity name, location)\n"
             f"- Output ONLY the two queries separated by  {_QUERY_SEP}  — nothing else"),
            ("user",
             "DOCUMENT SUMMARY (context):\n{summary}\n\n"
             "CLAIM TO REWRITE:\n{claim}\n\n"
             f"Output Query A  {_QUERY_SEP}  Query B"),
        ])

        self._parser = StrOutputParser()

    def _rewrite_single(self, summary: str, claim: str) -> List[str]:
        """Return [query_a, query_b] for one claim."""
        try:
            raw = (self._prompt | self.llm | self._parser).invoke({
                "summary": summary,
                "claim": claim,
            }).strip()

            if _QUERY_SEP in raw:
                parts = [p.strip() for p in raw.split(_QUERY_SEP) if p.strip()]
            else:
                # Fallback: split on newline or use full text as query_a
                parts = [p.strip() for p in raw.split("\n") if p.strip()]

            # Guarantee exactly 2 queries
            if len(parts) >= 2:
                return [parts[0], parts[1]]
            elif len(parts) == 1:
                return [parts[0], claim]   # second fallback: original claim
            else:
                return [claim, claim]

        except Exception as e:
            print(f"[ClaimRewriter] error rewriting claim: {e}")
            return [claim, claim]

    def rewrite_claims(
        self,
        summary: str,
        claims: List[str],
        max_workers: int = 4,
    ) -> Dict[str, List[str]]:
        """
        Rewrite all claims concurrently.

        Args:
            summary:     Concise document summary from Summarizer.
            claims:      Raw claim strings from ClaimExtractor.
            max_workers: Thread pool size for parallel LLM calls.

        Returns:
            {original_claim: [query_a, query_b]}
        """
        if not claims:
            return {}

        results: Dict[str, List[str]] = {}

        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            future_to_claim = {
                pool.submit(self._rewrite_single, summary, claim): claim
                for claim in claims
            }
            for future in as_completed(future_to_claim):
                claim = future_to_claim[future]
                try:
                    results[claim] = future.result()
                except Exception as e:
                    print(f"[ClaimRewriter] future error: {e}")
                    results[claim] = [claim, claim]

        return results
