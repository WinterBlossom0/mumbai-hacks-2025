import os
from dotenv import load_dotenv
from pathlib import Path
from typing import List

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load .env
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class HeadlineGenerator:
    def __init__(self, model: str = "gemini-2.0-flash-exp"):
        """
        Initialize the HeadlineGenerator using LangChain with Gemini API.
        
        Args:
            model: The Gemini model to use (default: gemini-2.0-flash-exp)
        """
        self.llm = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.7
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
