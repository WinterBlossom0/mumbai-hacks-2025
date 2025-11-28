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
            ("system", "You are a fact-checking expert analyzing claims against credible sources."),
            ("user", """You are a fact-checking expert. Your task is to verify the user's claims using the provided evidence from credible sources.

USER CLAIMS:
{user_claims_text}

EVIDENCE FROM CREDIBLE SOURCES:
{website_evidence_text}

INSTRUCTIONS:
1. Analyze the user's claims against the evidence.
2. Weigh the credibility and relevance of each source.
3. Cross-reference: If one source confirms a claim and another is silent, the claim is likely true. Do not dismiss valid information just because it's not in every single source.
4. Focus on the CORE TRUTH of the content. Do not be pedantic about minor details if the main message is verified.
5. Distinguish between "False" (contradicted by evidence) and "Unsupported" (no evidence found).

VERDICT CRITERIA:
- True: The core claims are supported by credible evidence. Minor discrepancies or missing details in some sources should not invalidate the verdict if the main facts hold up.
- False: The core claims are contradicted by evidence, or the content is fundamentally misleading.

Provide your response in this exact format:
VERDICT: [True/False]
REASONING: [Your detailed reasoning, explaining how you weighed the evidence]""")
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
