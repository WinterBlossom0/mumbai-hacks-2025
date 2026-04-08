import sys
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import settings

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


class HeadlineGenerator:
    """
    IMPACT TRACE:
      Called by: api/routers/verify.py (toggle-public), reddit/monitor.py
      Depends on: settings.SMALL_MODEL, settings.OPENAI_API_KEY
      If changed: headline column in verifications + reddit_posts tables is affected
    """

    def __init__(self, model: str = None):
        """
        Initialize the HeadlineGenerator using LangChain with OpenAI.

        Args:
            model: The model to use (default: SMALL_MODEL from settings)
        """
        model_name = model or settings.SMALL_MODEL
        self.llm = ChatOpenAI(
            model=model_name,
            openai_api_key=settings.OPENAI_API_KEY,
            reasoning_effort="medium",
        )
        
        self.headline_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a sensationalist news editor for a tabloid. Create SPICY, DRAMATIC, and ATTENTION-GRABBING headlines."),
            ("user", """Create a SPICY, DRAMATIC, and ATTENTION-GRABBING headline (max 12 words) based on the following claims.
Make it sound urgent and shocking! It should make people want to click immediately.
Do not reveal the verdict (true/false), just hype up the claim and make the headline short and catchy.

IMPORTANT: Output ONLY plain text. Do NOT use markdown formatting like **bold** or *italics*.

CLAIMS:
{claims_text}

HEADLINE:""")
        ])
        
        self.output_parser = StrOutputParser()

    def generate_headline(self, user_claims: List[str]) -> str:
        """
        Generate a catchy headline based on user claims.
        """
        claims_text = "\n".join([f"- {claim}" for claim in user_claims])
        
        try:
            # Create the chain
            chain = self.headline_prompt | self.llm | self.output_parser
            
            # Invoke the chain
            response = chain.invoke({"claims_text": claims_text})
            
            return response.strip().replace('"', '')
        except Exception as e:
            print(f"Error generating headline: {e}")
            return "Verification Report"
