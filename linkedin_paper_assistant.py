import os
import together
import requests
import PyPDF2
import io
from typing import List, Dict
import time
from urllib.parse import urlparse

# Set your API key
os.environ["TOGETHER_API_KEY"] = "72485359b7b96fc4c31a44e232cf4b0608c60c5d8b8123f892836192a168c540"

class LinkedInPaperAssistant:
    def __init__(self, model="mistralai/Mistral-7B-Instruct-v0.2"):
        print("Debug - Initializing Together client...")
        self.client = together.Together()
        self.model = model
        print(f"Debug - Initialized with model: {model}")
        
    def _call_model(self, prompt: str, temperature: float = 0.7) -> str:
        """Helper method to call the Together API"""
        print(f"Debug - Calling Together API with temperature: {temperature}")
        max_retries = 3
        retry_delay = 5  # seconds
        
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=1024
                )
                print("Debug - API call successful")
                return response.choices[0].message.content
            except together.error.RateLimitError as e:
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (attempt + 1)
                    print(f"Debug - Rate limit hit, waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                else:
                    print("Debug - Rate limit persists after all retries")
                    raise
            except Exception as e:
                print(f"Debug - API call failed: {str(e)}")
                raise

    def convert_arxiv_to_pdf_url(self, url: str) -> str:
        """Convert arXiv abstract URL to PDF URL"""
        # Convert abstract URL to PDF URL
        if "arxiv.org/abs/" in url:
            arxiv_id = url.split("/abs/")[1]
            return f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        return url

    def extract_text_from_pdf_url(self, pdf_url: str) -> str:
        """Download and extract text from a PDF URL"""
        try:
            # Convert URL if it's an arXiv abstract URL
            pdf_url = self.convert_arxiv_to_pdf_url(pdf_url)
            print(f"Debug - Accessing PDF at: {pdf_url}")
            
            # Download PDF
            response = requests.get(pdf_url)
            response.raise_for_status()
            
            # Read PDF content
            pdf_file = io.BytesIO(response.content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Extract text from all pages
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text
        except Exception as e:
            print(f"Error processing PDF: {str(e)}")
            raise

    def analyze_paper(self, text: str) -> Dict:
        """Analyze the key components of a research paper"""
        prompt = f"""<s>[INST] Please analyze this research paper and extract the following components:
        - Title and Authors (if available)
        - Main research question or objective
        - Key technical innovations
        - Most significant results/findings
        - Real-world applications or impact
        - Future research implications

        Text: {text}
        
        Format your response as a structured analysis with clear headings. Focus on the most novel and impactful aspects. [/INST]</s>"""
        
        return self._call_model(prompt, temperature=0.3)

    def create_linkedin_post(self, analysis: str) -> str:
        """Create an engaging LinkedIn post about the research"""
        prompt = f"""<s>[INST] Create an engaging LinkedIn post about this AI research paper. The post should:
        1. Start with a compelling hook about the innovation or impact
        2. Highlight ONE groundbreaking finding or contribution
        3. Explain its practical implications for AI/tech industry
        4. Use simple analogies to explain complex concepts
        5. Include 3-4 relevant hashtags (e.g., #AI #MachineLearning)
        6. Keep it under 1300 characters
        7. Use 2-3 relevant emojis maximum
        8. End with an engaging question or call-to-action

        Research Analysis: {analysis}
        
        Make it accessible to a technical audience while maintaining scientific accuracy. Focus on what makes this research novel and exciting. [/INST]</s>"""
        
        return self._call_model(prompt, temperature=0.7)

def main():
    # Initialize the assistant
    assistant = LinkedInPaperAssistant()
    
    print("📚 LinkedIn Research Paper Assistant")
    print("Enter the URL of the research paper PDF:")
    pdf_url = input().strip()
    
    try:
        # Validate URL
        parsed_url = urlparse(pdf_url)
        if not all([parsed_url.scheme, parsed_url.netloc]):
            raise ValueError("Invalid URL format")
            
        print("\n📥 Downloading and processing PDF...")
        paper_text = assistant.extract_text_from_pdf_url(pdf_url)
        
        print("\n📊 Analyzing paper...")
        analysis = assistant.analyze_paper(paper_text)
        print("\nAnalysis:")
        print(analysis)
        
        print("\n✍️ Creating LinkedIn post...")
        linkedin_post = assistant.create_linkedin_post(analysis)
        print("\nLinkedIn Post:")
        print("=" * 50)
        print(linkedin_post)
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("Please make sure the URL is accessible and points to a valid PDF file.")

if __name__ == "__main__":
    main()
