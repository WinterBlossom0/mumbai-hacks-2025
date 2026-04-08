"""
Sliding-window summarizer using MEDIUM_MODEL (gpt-5.4-mini, 1M token context).

Algorithm
---------
  Given a body of text that may be arbitrarily long:

  1. Split text into TOKEN-SAFE chunks (chunk_tokens ≤ max_chunk_tokens).
  2. Process chunk-by-chunk with a rolling summary:
       summary[0]  = summarise(chunk[0])
       summary[t]  = summarise(summary[t-1] + chunk[t])   ← sliding window
  3. Final summary[N] is the compressed, informative output.

  The model has a 1 M-token context so even large rolling summaries fit
  comfortably, but we keep individual summaries short (~400 tokens) to
  avoid compounding noise.

IMPACT TRACE:
  Called by:   api/routers/verify.py (before ClaimRewriter)
  Depends on:  settings.MEDIUM_MODEL, settings.OPENAI_API_KEY
  Output used: ClaimRewriter.rewrite_claims(summary, claims)
  If changed:  quality of search queries (downstream) and verification accuracy change
"""
import sys
import tiktoken
from typing import List
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import settings

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


class Summarizer:
    """
    Iterative sliding-window summarizer.

    IMPACT TRACE:
      Called by:  api/routers/verify.py, reddit/monitor.py
      Depends on: settings.MEDIUM_MODEL (gpt-5.4-mini, 1M ctx), settings.OPENAI_API_KEY
      Output:     concise factual summary string fed to ClaimRewriter
      If changed: all downstream search queries change
    """

    # Max tokens per raw text chunk fed into the model at once.
    # gpt-5.4-mini has 1M context; we keep chunks small so rolling
    # summaries remain dense and cheap.
    DEFAULT_CHUNK_TOKENS = 120_000
    # Target length of each intermediate summary (in words, approximate).
    SUMMARY_TARGET_WORDS = 300

    def __init__(self, model: str = None):
        model_name = model or settings.MEDIUM_MODEL
        self.llm = ChatOpenAI(
            model=model_name,
            openai_api_key=settings.OPENAI_API_KEY,
            reasoning_effort="medium",
        )
        try:
            self._enc = tiktoken.encoding_for_model("gpt-4")
        except Exception:
            self._enc = tiktoken.get_encoding("cl100k_base")

        self._first_prompt = ChatPromptTemplate.from_messages([
            ("system",
             "You are a precise summarizer. Produce a concise, fact-dense summary "
             f"in ~{self.SUMMARY_TARGET_WORDS} words. Preserve all key facts, "
             "numbers, names, dates, and claims. Drop filler and repetition."),
            ("user", "Summarise the following text:\n\n{text}"),
        ])

        self._continuation_prompt = ChatPromptTemplate.from_messages([
            ("system",
             "You are a precise summarizer maintaining a rolling summary. "
             f"Merge the previous summary with the new text into a single concise summary "
             f"of ~{self.SUMMARY_TARGET_WORDS} words. Preserve all key facts, numbers, "
             "names, dates, and claims. Drop filler and repetition."),
            ("user",
             "PREVIOUS SUMMARY:\n{prev_summary}\n\n"
             "NEW TEXT SEGMENT:\n{new_text}\n\n"
             "Produce an updated merged summary:"),
        ])

        self._parser = StrOutputParser()

    def _token_count(self, text: str) -> int:
        return len(self._enc.encode(text))

    def _split_into_chunks(self, text: str, max_tokens: int) -> List[str]:
        """Split text into chunks that each fit within max_tokens."""
        words = text.split()
        chunks: List[str] = []
        current: List[str] = []
        current_tokens = 0

        for word in words:
            word_tokens = self._token_count(word + " ")
            if current_tokens + word_tokens > max_tokens and current:
                chunks.append(" ".join(current))
                current = [word]
                current_tokens = word_tokens
            else:
                current.append(word)
                current_tokens += word_tokens

        if current:
            chunks.append(" ".join(current))

        return chunks if chunks else [text]

    def summarise(self, text: str, max_chunk_tokens: int = DEFAULT_CHUNK_TOKENS) -> str:
        """
        Produce a concise summary of `text` using the sliding-window algorithm.

        Args:
            text:             Raw input text (any length).
            max_chunk_tokens: Tokens per chunk window (default 120k).

        Returns:
            Compact, informative summary string.
        """
        if not text or not text.strip():
            return ""

        total_tokens = self._token_count(text)

        # Short text — single-pass summarisation
        if total_tokens <= max_chunk_tokens:
            chain = self._first_prompt | self.llm | self._parser
            return chain.invoke({"text": text}).strip()

        # Long text — sliding window
        chunks = self._split_into_chunks(text, max_chunk_tokens)
        print(f"[Summarizer] {total_tokens} tokens split into {len(chunks)} chunks")

        # Bootstrap with first chunk
        chain_first = self._first_prompt | self.llm | self._parser
        rolling_summary = chain_first.invoke({"text": chunks[0]}).strip()

        chain_cont = self._continuation_prompt | self.llm | self._parser
        for i, chunk in enumerate(chunks[1:], start=1):
            print(f"[Summarizer] merging chunk {i}/{len(chunks)-1} ...")
            rolling_summary = chain_cont.invoke({
                "prev_summary": rolling_summary,
                "new_text": chunk,
            }).strip()

        return rolling_summary
