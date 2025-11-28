import os
from typing import List, Dict
from dotenv import load_dotenv
from pathlib import Path

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load .env from project root
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class ClaimReasoner:
    def __init__(self, model: str = "gemini-2.5-pro"):
        """
        Initialize the ClaimReasoner using LangChain with Gemini API.

        Args:
            model: The Gemini model to use (default: gemini-2.5-pro)
        """
        self.llm = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0
        )
        
        self.reasoning_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a STRICT fact-checker with ZERO tolerance for numerical inaccuracies or information manipulation. Your primary duty is to catch false numbers and manipulated information."),
            ("user", """You are a STRICT fact-checking expert. Your job is to REJECT any claims with incorrect numbers or manipulated information.

USER CLAIMS:
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

Provide your response in this exact format:
VERDICT: [True/False]
REASONING: [State EXACTLY which numbers you verified or found incorrect. Quote specific evidence. If ANY number is wrong or unverified, explain why it's FALSE. Be explicit about manipulation if detected.]""")
        ])
        
        self.output_parser = StrOutputParser()

    def reason_all_claims(
        self, user_claims: List[str], all_website_claims: Dict[str, List[str]]
    ) -> Dict[str, any]:
        """
        Use Gemini to reason about ALL user claims based on ALL website claims.

        Args:
            user_claims: List of all original claims made by the user
            all_website_claims: Dictionary mapping URLs to their extracted claims

        Returns:
            Dictionary with 'verdict' (True/False) and 'reasoning' keys
        """
        # Format user claims
        user_claims_text = "\n".join([f"{i+1}. {claim}" for i, claim in enumerate(user_claims)])

        # Format website evidence
        website_evidence = []
        for url, claims in all_website_claims.items():
            website_evidence.append(f"\nSource: {url}")
            for i, claim in enumerate(claims, 1):
                website_evidence.append(f"  {i}. {claim}")
        website_evidence_text = "\n".join(website_evidence)

        try:
            # Create the chain
            chain = self.reasoning_prompt | self.llm | self.output_parser
            
            # Invoke the chain
            response_text = chain.invoke({
                "user_claims_text": user_claims_text,
                "website_evidence_text": website_evidence_text
            })
            
            response_text = response_text.strip()
            verdict = None
            reasoning = ""
            lines = response_text.split("\n")
            for i, line in enumerate(lines):
                if line.upper().startswith("VERDICT:"):
                    verdict_text = line.split(":", 1)[1].strip().lower()
                    verdict = "true" in verdict_text
                elif line.upper().startswith("REASONING:"):
                    reasoning = "\n".join(lines[i + 1:]).strip()
                    break
            return {"verdict": verdict, "reasoning": reasoning}
        except Exception as e:
            print(f"Error reasoning about claim: {e}")
            return {"verdict": None, "reasoning": f"Error: {str(e)}"}
