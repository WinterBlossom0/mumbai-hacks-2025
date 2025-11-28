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
    def __init__(self, model: str = "gemini-2.0-flash-exp"):
        """
        Initialize the ClaimReasoner using LangChain with Gemini API.

        Args:
            model: The Gemini model to use (default: gemini-2.0-flash-exp)
        """
        self.llm = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0
        )
        
        self.reasoning_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert fact-checker who carefully evaluates claims against evidence with balanced judgment and thorough reasoning."),
            ("user", """You are a fact-checking expert. Your task is to carefully evaluate the user's claims using the provided evidence from credible sources.

USER CLAIMS:
{user_claims_text}

EVIDENCE FROM CREDIBLE SOURCES:
{website_evidence_text}

EVALUATION INSTRUCTIONS:
1. Analyze each claim systematically against the available evidence.
2. Assess the credibility and reliability of each source.
3. Check if specific details (numbers, dates, names, facts) are supported by the evidence.
4. Cross-reference information across multiple sources when available.
5. Consider the context - ensure claims aren't misleading even if partially accurate.
6. Distinguish clearly between:
   - Verified information (directly confirmed by credible sources)
   - Unverified information (no evidence found, but not contradicted)
   - False information (contradicted by credible evidence)
7. Look for any contradictions or inconsistencies in the evidence.
8. Evaluate whether the overall message is accurate, not just individual facts.

VERDICT CRITERIA:
- True: The claims are substantially supported by credible evidence. Key facts and the overall message are verified. Minor gaps in coverage are acceptable if the core assertions hold up and no contradictions exist.
- False: Any of the following apply:
  * Claims are contradicted by credible evidence
  * Key facts or details are demonstrably incorrect
  * The overall message is misleading or misrepresents the truth
  * Insufficient credible evidence exists to support significant claims
  * Evidence shows a distorted or out-of-context representation

Provide balanced, well-reasoned analysis. Support your verdict with specific references to the evidence.

Provide your response in this exact format:
VERDICT: [True/False]
REASONING: [Your detailed, systematic reasoning explaining step-by-step how you evaluated the claims against the evidence, what was verified, what was contradicted, and why you reached your conclusion]""")
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
