import os
import tiktoken
from typing import List, Dict
from dotenv import load_dotenv
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from web_scraper import WebScraper

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load .env from project root
env_path = Path(__file__).parent.parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


class ClaimExtractor:
    def __init__(self, model: str = None, max_tokens_per_chunk: int = 15000):
        """
        Initialize the ClaimExtractor.
        
        Args:
            model: The OpenAI model to use (default: from OPENAI_MODEL env variable)
            max_tokens_per_chunk: Maximum tokens per text chunk (default: 15000)
        """
        model_name = model or os.getenv("OPENAI_MODEL")
        self.llm = ChatOpenAI(
            model=model_name,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0
        )
        self.max_tokens_per_chunk = max_tokens_per_chunk
        self.encoding = tiktoken.encoding_for_model("gpt-4")
        
        # Define prompts for claim extraction
        self.claim_extraction_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a claim extraction assistant. Extract only the 3-7 MOST important and specific claims from the text. Be selective - quality over quantity. Each claim must be DISTINCT and about different aspects. Avoid extracting closely related or redundant claims. Ignore generic statements and filler content. Return them as a Python list of strings."),
            ("user", """Extract the most important and significant claims from the following text.
Focus on 'hot claims' - statements that are:
- Specific and concrete (with numbers, names, dates, or specific details)
- Significant and meaningful
- Not generic or trivial information
- DISTINCT and NOT closely related to each other (avoid redundant or overlapping claims)

Extract only 3-7 of the MOST important claims. Be selective and concise.
Ensure each claim is about a DIFFERENT aspect or topic - avoid extracting multiple similar claims.
Return ONLY a Python list of strings, where each string is a distinct claim.
Format: ['claim1', 'claim2', 'claim3']

Text:
{text}

Claims:""")
        ])
        
        self.website_claim_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a claim extraction assistant. Extract claims from website content that relate to the original claim topic. Return only a Python list of strings."),
            ("user", """You are analyzing website content related to these original claims:

ORIGINAL CLAIMS:
{original_claims_text}

Extract 3-7 important claims from the website content that are:
- Related to ANY of the original claims (about the same topics or providing context)
- Specific and concrete (with numbers, names, dates, or specific details)
- Significant and meaningful
- DISTINCT and NOT closely related to each other

Website content:
{content}

Return ONLY a Python list of strings, where each string is a distinct claim.
Format: ["claim1", "claim2", "claim3"]""")
        ])
        
        self.output_parser = StrOutputParser()
    
    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in a text."""
        return len(self.encoding.encode(text))
    
    def split_text_into_chunks(self, text: str) -> List[str]:
        """
        Split text into chunks based on token limit.
        
        Args:
            text: The input text to split
            
        Returns:
            List of text chunks
        """
        token_count = self.count_tokens(text)
        
        if token_count <= self.max_tokens_per_chunk:
            return [text]
        
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            test_chunk = current_chunk + "\n\n" + paragraph if current_chunk else paragraph
            
            if self.count_tokens(test_chunk) <= self.max_tokens_per_chunk:
                current_chunk = test_chunk
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                
                # If single paragraph is too large, split by sentences
                if self.count_tokens(paragraph) > self.max_tokens_per_chunk:
                    sentences = paragraph.split('. ')
                    temp_chunk = ""
                    
                    for sentence in sentences:
                        test_sentence = temp_chunk + ". " + sentence if temp_chunk else sentence
                        
                        if self.count_tokens(test_sentence) <= self.max_tokens_per_chunk:
                            temp_chunk = test_sentence
                        else:
                            if temp_chunk:
                                chunks.append(temp_chunk)
                            temp_chunk = sentence
                    
                    current_chunk = temp_chunk
                else:
                    current_chunk = paragraph
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks

    def extract_claims_from_chunk(self, chunk: str) -> List[str]:
        """
        Extract claims from a single text chunk using LangChain.
        
        Args:
            chunk: Text chunk to extract claims from
            
        Returns:
            List of extracted claims
        """
        try:
            # Create the chain
            chain = self.claim_extraction_prompt | self.llm | self.output_parser
            
            # Invoke the chain
            content = chain.invoke({"text": chunk})
            
            # Parse the response to extract the list
            # Handle cases where GPT returns the list with or without markdown
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("python"):
                    content = content[6:]
                content = content.strip()
            
            # Safely evaluate the list
            claims = eval(content)
            
            if isinstance(claims, list):
                return [str(claim) for claim in claims]
            else:
                return []
                
        except Exception as e:
            print(f"Error extracting claims: {e}")
            return []
    
    def extract_claims_from_url(self, url: str, key_name: str = "user") -> Dict[str, List[str]]:
        """
        Extract claims from a URL by scraping it first, then extracting claims.
        
        Args:
            url: The URL to scrape and extract claims from
            key_name: The key name for the output dictionary (default: "user")
            
        Returns:
            Dictionary with key_name as key and list of all extracted claims as value
        """
        print(f"Scraping URL: {url}")
        
        scraper = WebScraper()
        scraped_data = scraper.scrape_url(url)
        
        if not scraped_data['content']:
            print(f"Failed to scrape content from {url}")
            return {key_name: []}
        
        print(f"Successfully scraped {len(scraped_data['content'])} characters")
        print(f"Extracting claims from scraped content...\n")
        
        # Extract claims from the scraped content
        return self.extract_claims(scraped_data['content'], key_name)
    
    def extract_claims(self, text: str, key_name: str = "user") -> Dict[str, List[str]]:
        """
        Extract claims from text with automatic chunking and concurrent processing.
        
        Args:
            text: The input text to extract claims from
            key_name: The key name for the output dictionary (default: "user")
            
        Returns:
            Dictionary with key_name as key and list of all extracted claims as value
        """
        # Split text into chunks
        chunks = self.split_text_into_chunks(text)
        
        print(f"Processing {len(chunks)} chunk(s) concurrently...")
        
        # Extract claims from each chunk concurrently
        all_claims = []
        if not chunks:
            raise ValueError("No text chunks to process. Input text may be empty.")
        
        with ThreadPoolExecutor(max_workers=min(len(chunks), 10)) as executor:
            future_to_chunk = {
                executor.submit(self.extract_claims_from_chunk, chunk): i
                for i, chunk in enumerate(chunks, 1)
            }
            
            for future in as_completed(future_to_chunk):
                chunk_num = future_to_chunk[future]
                try:
                    claims = future.result()
                    all_claims.extend(claims)
                    print(f"Completed chunk {chunk_num}/{len(chunks)}")
                except Exception as e:
                    print(f"Error processing chunk {chunk_num}: {e}")
        
        print(f"Total claims extracted: {len(all_claims)}")
        
        return {key_name: all_claims}
    
    def extract_website_claims(self, urls: List[str], original_claims: List[str]) -> Dict[str, List[str]]:
        """
        Scrape websites and extract claims related to the original claims.
        
        Args:
            urls: List of URLs to scrape
            original_claims: List of original user claims to compare against
            
        Returns:
            Dictionary mapping each URL to its list of extracted claims
        """
        scraper = WebScraper()
        url_claims = {}
        
        print(f"\nProcessing {len(urls)} website(s) for claims related to {len(original_claims)} original claim(s)\n")
        
        # Process URLs concurrently
        if not urls:
            raise ValueError("No URLs provided for website claims extraction")
        
        with ThreadPoolExecutor(max_workers=min(len(urls), 5)) as executor:
            future_to_url = {
                executor.submit(self._process_single_url, url, original_claims, scraper): url
                for url in urls
            }
            
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    url_claims[url] = result['claims']
                    print(f"[OK] Extracted {len(result['claims'])} claim(s) from {url}")
                except Exception as e:
                    print(f"[ERROR] Error processing {url}: {e}")
                    url_claims[url] = []
        
        return url_claims
    
    def _process_single_url(self, url: str, original_claim: List[str], scraper: WebScraper) -> Dict[str, List[str]]:
        """
        Process a single URL: scrape and extract claims.
        
        Args:
            url: URL to process
            original_claim: List of original user claims
            scraper: WebScraper instance
            
        Returns:
            Dictionary with 'claims' key
        """
        # Scrape the website
        scraped_data = scraper.scrape_url(url)
        content = scraped_data['content']
        
        if not content:
            return {"claims": []}
        
        # Extract claims related to ALL original claims
        original_claims_text = "\n".join([f"- {claim}" for claim in original_claim])
        
        try:
            # Create the chain
            chain = self.website_claim_prompt | self.llm | self.output_parser
            
            # Invoke the chain
            content_response = chain.invoke({
                "original_claims_text": original_claims_text,
                "content": content[:15000]
            })
            
            # Parse response
            if content_response.startswith("```"):
                content_response = content_response.split("```")[1]
                if content_response.startswith("python"):
                    content_response = content_response[6:]
                content_response = content_response.strip()
            
            claims = eval(content_response)
            
            if isinstance(claims, list):
                return {"claims": [str(claim) for claim in claims]}
            else:
                return {"claims": []}
            
        except Exception as e:
            print(f"Error extracting claims from URL: {e}")
            return {"claims": []}
