import sys
from typing import List, Dict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import settings

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


class ClaimReasoner:
    """
    IMPACT TRACE:
    ╔══════════════════════════════════════════════════════════════════════╗
    ║                     UPSTREAM (Receives data from)                      ║
    ╠══════════════════════════════════════════════════════════════════════╣
    ║  • api/routers/verify.py  → reason_all_claims() at line ~138            ║
    ║  • reddit/monitor.py      → reason_all_claims() at line ~188            ║
    ║  • ClaimExtractor         → user_claims, raw_text                       ║
    ║  • ClaimExtractor.extract_website_claims() → website_claims            ║
    ╚══════════════════════════════════════════════════════════════════════╝

    ╔══════════════════════════════════════════════════════════════════════╗
    ║                     DOWNSTREAM (Sends data to)                         ║
    ╠══════════════════════════════════════════════════════════════════════╣
    ║  • Returns: {verdict: bool, reasoning: str}                            ║
    ║    ↓                                                                  ║
    ║  • SupabaseClient.save_verification()   → reasoning field in DB          ║
    ║  • SupabaseClient.save_reddit_post()    → reasoning field in DB        ║
    ║    ↓                                                                  ║
    ║  • ReasoningText.tsx                    → renders with markers         ║
    ║  • ClassifiedInput.tsx                  → renders classified sentences   ║
    ╚══════════════════════════════════════════════════════════════════════╝

    ╔══════════════════════════════════════════════════════════════════════╗
    ║                     MARKER FORMAT CONTRACT                             ║
    ╠══════════════════════════════════════════════════════════════════════╣
    ║  Generates: ««TRUE_START»»...««TRUE_END»»                               ║
    ║             ««FALSE_START»»...««FALSE_END»»                           ║
    ║             ««UNCONFIRMED_START»»...««UNCONFIRMED_END»»                 ║
    ║             __CLASSIFIED_INPUT__ sentinel                              ║
    ║  Consumer:  ReasoningText.tsx parseSegments() must match these         ║
    ╚══════════════════════════════════════════════════════════════════════╝

    BREAKING CHANGES:
      • Changing marker format → breaks ALL frontend rendering
      • Changing prompt structure → affects verdict accuracy
      • Removing CLASSIFIED_INPUT sentinel → breaks ClassifiedInput.tsx
    """

    def __init__(self, model: str = None):
        """
        Initialize the ClaimReasoner using LangChain with OpenAI.

        Args:
            model: The model to use (default: BIG_MODEL from settings)
        """
        model_name = model or settings.BIG_MODEL
        self.llm = ChatOpenAI(
            model=model_name,
            openai_api_key=settings.OPENAI_API_KEY,
            temperature=0,
            reasoning_effort="high",
        )
        
        # Inline highlight markers — embedded in REASONING text around each claim mention.
        # These are complex bracket sequences that cannot appear in natural language.
        # Frontend parses them to render coloured highlights.
        self.TRUE_START        = "««TRUE_START»»"
        self.TRUE_END          = "««TRUE_END»»"
        self.FALSE_START       = "««FALSE_START»»"
        self.FALSE_END         = "««FALSE_END»»"
        self.UNCONFIRMED_START = "««UNCONFIRMED_START»»"
        self.UNCONFIRMED_END   = "««UNCONFIRMED_END»»"

        self.reasoning_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a STRICT fact-checker with ZERO tolerance for numerical inaccuracies or information manipulation. Your primary duty is to catch false numbers and manipulated information."),
            ("user", """You are a STRICT fact-checking expert. Your job is to REJECT any claims with incorrect numbers or manipulated information.

ORIGINAL USER TEXT (for CLASSIFIED_INPUT section):
{original_text}

EXTRACTED CLAIMS:
{user_claims_text}

EVIDENCE FROM CREDIBLE SOURCES:
{website_evidence_text}

STRICT VERIFICATION PROTOCOL:
1. **NUMBERS ARE CRITICAL**: Numbers, percentages, dates, statistics must match sources accurately.
   - EXACT matches are preferred
   - EXTREMELY CLOSE matches are acceptable (e.g., 50% vs 48-52%, 1000 vs 995-1005)
   - Rounding differences within 5% tolerance are fine (47.8% ≈ 48%)
   - Year/date precision: If source says "2024" and claim says "2024", it's TRUE even if source also mentions late 2023
   - Vague vs specific: "around 1000" supports a claim of "1000"
   - REJECT if difference is significant (>5% off) or clearly manipulated

2. **MANIPULATION DETECTION - BE SUSPICIOUS**:
   - Exaggeration (making numbers bigger/smaller than they are)
   - Cherry-picking (selecting only favorable data points)
   - Context stripping (removing important qualifiers like "estimated", "approximately", "up to")
   - Causation claims without evidence (X caused Y when correlation isn't proven)
   - Misleading framing (technically true but gives wrong impression)
   - Omitting crucial contradicting information
   
3. **VERIFICATION REQUIREMENTS**:
   - Key numbers should have EXACT or EXTREMELY CLOSE matches in evidence
   - Claims need DIRECT quotes or explicit confirmation from sources
   - If a number appears in a claim, find that number or a very close variant (within 5%) in evidence
   - "Approximately close" IS acceptable if within reasonable tolerance

4. **DEFAULT TO FALSE**:
   - If numbers differ by >5% without explanation → FALSE
   - If numbers are clearly manipulated or exaggerated → FALSE
   - If context suggests manipulation → FALSE
   - If evidence is weak or unclear → FALSE
   - When in doubt → FALSE

VERDICT RULES:
- True: If ALL numbers are verified (exact or extremely close within 5%), NO manipulation detected, ALL facts confirmed by credible sources, and NO significant discrepancies.
  
- False: Mark as FALSE if ANY of these apply:
  * Numbers differ by >5% or are clearly exaggerated
  * ANY sign of deliberate information manipulation or misleading framing
  * Numbers lack reasonable confirmation in evidence
  * Important context is omitted to mislead
  * Claims go beyond what evidence actually states
  * Evidence contradicts any part of the claims
  * Cannot find exact or extremely close numerical matches (within 5%)

**DEFAULT STANCE: Assume FALSE unless proven TRUE with solid evidence. Be strict but fair about close numerical matches.**

INLINE CLAIM HIGHLIGHTING:
When you mention a specific user claim or key fact in your REASONING, wrap it with the appropriate markers:
  - If confirmed true:    ««TRUE_START»»the claim text««TRUE_END»»
  - If confirmed false:   ««FALSE_START»»the claim text««FALSE_END»»
  - If unconfirmed:       ««UNCONFIRMED_START»»the claim text««UNCONFIRMED_END»»

These markers will be used to highlight the text in green/red/yellow on the frontend.
Wrap the EXACT claim phrase (or a key part of it) — not your commentary around it.
You may highlight multiple claims per sentence. Do NOT use these markers anywhere outside REASONING.

CLASSIFIED INPUT SECTION:
After REASONING, reproduce the ORIGINAL USER TEXT sentence by sentence.
For EACH sentence, classify it INDEPENDENTLY based on what claims it contains:
  - Sentence contains ONLY true/verified claims:     ««TRUE_START»»sentence««TRUE_END»»
  - Sentence contains ANY false/misleading claim:   ««FALSE_START»»sentence««FALSE_END»»
  - Sentence has no specific claims OR claims can't be verified: ««UNCONFIRMED_START»»sentence««UNCONFIRMED_END»»

IMPORTANT: A sentence with mixed true and false claims should be marked FALSE.
A sentence with only true claims should be marked TRUE regardless of overall verdict.
Do NOT paraphrase — use the EXACT original sentence text inside the markers.
Every sentence must get exactly one marker pair.

Provide your response in this EXACT format (do not deviate):
VERDICT: [True/False]
REASONING: [State EXACTLY which numbers you verified or found incorrect. Quote specific evidence. Wrap each claim mention with the appropriate inline markers as instructed above.]
CLASSIFIED_INPUT: [The original user text reproduced sentence-by-sentence, each sentence wrapped in one marker pair as instructed above.]""")
        ])

        self.CLASSIFIED_INPUT_SENTINEL = "__CLASSIFIED_INPUT__"

        self.output_parser = StrOutputParser()

    def reason_all_claims(
        self, user_claims: List[str], all_website_claims: Dict[str, List[str]],
        original_text: str = ""
    ) -> Dict[str, any]:
        """
        Reason about ALL user claims based on ALL website evidence.

        Args:
            user_claims: Extracted claims list.
            all_website_claims: Evidence from scraped sources.
            original_text: The raw original user input. Used for the CLASSIFIED_INPUT
                           section — each sentence is reproduced with inline markers.

        Returns:
            {
              'verdict':   bool,
              'reasoning': str  — reasoning text with inline markers, followed by
                               __CLASSIFIED_INPUT__ sentinel, followed by the original
                               text with per-sentence inline markers. Frontend splits
                               on the sentinel to render both sections.
            }

        IMPACT TRACE:
          reasoning is stored verbatim in DB (single field, no schema change).
          Frontend ReasoningText splits on __CLASSIFIED_INPUT__ and renders both.
        """
        user_claims_text = "\n".join([f"{i+1}. {claim}" for i, claim in enumerate(user_claims)])

        website_evidence = []
        for url, claims in all_website_claims.items():
            website_evidence.append(f"\nSource: {url}")
            for i, claim in enumerate(claims, 1):
                website_evidence.append(f"  {i}. {claim}")
        website_evidence_text = "\n".join(website_evidence)

        try:
            chain = self.reasoning_prompt | self.llm | self.output_parser
            response_text = chain.invoke({
                "original_text": original_text or "\n".join(user_claims),
                "user_claims_text": user_claims_text,
                "website_evidence_text": website_evidence_text
            }).strip()

            verdict = None
            reasoning_lines = []
            classified_input_lines = []
            section = None  # 'reasoning' | 'classified'

            for line in response_text.split("\n"):
                upper = line.upper().strip()
                if upper.startswith("VERDICT:"):
                    verdict_text = line.split(":", 1)[1].strip().lower()
                    verdict = "true" in verdict_text
                    section = None
                elif upper.startswith("REASONING:"):
                    section = "reasoning"
                    tail = line.split(":", 1)[1].strip()
                    if tail:
                        reasoning_lines.append(tail)
                elif upper.startswith("CLASSIFIED_INPUT:"):
                    section = "classified"
                    tail = line.split(":", 1)[1].strip()
                    if tail:
                        classified_input_lines.append(tail)
                elif section == "reasoning":
                    reasoning_lines.append(line)
                elif section == "classified":
                    classified_input_lines.append(line)

            reasoning = "\n".join(reasoning_lines).strip()
            classified_input = "\n".join(classified_input_lines).strip()

            # Concat both into the reasoning field separated by a sentinel.
            # No new DB column needed — frontend splits on the sentinel.
            combined = reasoning
            if classified_input:
                combined = reasoning + "\n" + self.CLASSIFIED_INPUT_SENTINEL + "\n" + classified_input

            return {
                "verdict": verdict,
                "reasoning": combined,
            }
        except Exception as e:
            print(f"Error reasoning about claim: {e}")
            return {"verdict": None, "reasoning": f"Error: {str(e)}"}
