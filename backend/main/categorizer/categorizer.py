import os
from typing import List
from dotenv import load_dotenv
from pathlib import Path

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load .env from project root
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class ClaimCategorizer:
    def __init__(self, model: str = None):
        """
        Initialize the ClaimCategorizer using LangChain with OpenAI.

        Args:
            model: The OpenAI model to use (default: from OPENAI_MODEL env variable)
        """
        model_name = model or os.getenv("OPENAI_MODEL")
        self.llm = ChatOpenAI(
            model=model_name,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0
        )

        self.categorization_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a content categorization expert. Analyze claims and categorize them into one of the predefined categories."),
            ("user", """Analyze the following claims and categorize them into EXACTLY ONE of these categories:
- sports
- technology
- politics
- finance
- crime

Choose the category that best represents the PRIMARY topic of the claims. If multiple categories could apply, choose the most dominant one.

CLAIMS:
{claims_text}

INSTRUCTIONS:
1. Read all the claims carefully
2. Identify the main topic/theme
3. Return ONLY the category name (lowercase, one word)
4. Do not include any explanation or additional text

CATEGORY:""")
        ])

        self.output_parser = StrOutputParser()

    def categorize_claims(self, claims: List[str]) -> str:
        """
        Categorize claims into one of the predefined categories.

        Args:
            claims: List of claims to categorize

        Returns:
            Category string (one of: sports, technology, politics, finance, crime)
        """
        if not claims:
            return "technology"  # Default fallback

        # Format claims
        claims_text = "\n".join([f"- {claim}" for claim in claims])

        try:
            # Create the chain
            chain = self.categorization_prompt | self.llm | self.output_parser

            # Invoke the chain
            category = chain.invoke({"claims_text": claims_text})

            # Clean and validate the response
            category = category.strip().lower()

            # Ensure it's one of the valid categories
            valid_categories = ["sports", "technology", "politics", "finance", "crime"]
            if category in valid_categories:
                return category
            else:
                # If invalid category returned, default to technology
                print(f"Invalid category '{category}' returned, defaulting to 'technology'")
                return "technology"

        except Exception as e:
            print(f"Error categorizing claims: {e}")
            return "technology"  # Default fallback on error
