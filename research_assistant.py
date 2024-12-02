import os
import together
from typing import List, Dict
import time

# Set your API key
os.environ["TOGETHER_API_KEY"] = "72485359b7b96fc4c31a44e232cf4b0608c60c5d8b8123f892836192a168c540"

class ResearchAssistant:
    def __init__(self, model="mistralai/Mistral-7B-Instruct-v0.2"):
        print("Debug - Initializing Together client...")  # Debug print
        self.client = together.Together()
        self.model = model
        print(f"Debug - Initialized with model: {model}")  # Debug print
        
    def _call_model(self, prompt: str, temperature: float = 0.7) -> str:
        """Helper method to call the Together API"""
        print(f"Debug - Calling Together API with temperature: {temperature}")  # Debug print
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
                print("Debug - API call successful")  # Debug print
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
                print(f"Debug - API call failed: {str(e)}")  # Debug print
                raise

    def analyze_paper(self, text: str) -> Dict:
        """Analyze the key components of a research paper"""
        prompt = f"""<s>[INST] Please analyze this research text and extract the following components:
        - Main objective/hypothesis
        - Methodology
        - Key findings
        - Limitations
        - Future work suggestions

        Text: {text}
        
        Format your response as a structured analysis with clear headings. [/INST]</s>"""
        
        return self._call_model(prompt, temperature=0.3)

    def generate_questions(self, analysis: str) -> List[str]:
        """Generate insightful follow-up questions"""
        prompt = f"""<s>[INST] Based on this research analysis, generate 3-5 insightful follow-up questions 
        that would help deepen understanding or explore related areas:

        Analysis: {analysis}
        
        Format your response as a numbered list of questions. [/INST]</s>"""
        
        return self._call_model(prompt, temperature=0.7)

    def simplify_explanation(self, analysis: str) -> str:
        """Generate a simplified explanation for non-experts"""
        prompt = f"""<s>[INST] Create a simplified explanation of this research for a general audience.
        Avoid technical jargon and use analogies where helpful:

        Analysis: {analysis}
        
        Make it engaging and easy to understand while maintaining accuracy. [/INST]</s>"""
        
        return self._call_model(prompt, temperature=0.7)

def main():
    # Initialize the assistant
    assistant = ResearchAssistant()
    
    print(" Research Paper Assistant")
    print("Enter your research text (press Return twice on an empty line when done):")
    
    # Collect multiline input
    lines = []
    while True:
        line = input()
        print(f"Debug - Input received: '{line}'")  # Debug print
        if line == "" and (len(lines) == 0 or lines[-1] == ""):
            print("Debug - Detected double Return, ending input")  # Debug print
            break
        lines.append(line)
    
    text = "\n".join(lines)
    print(f"Debug - Final text length: {len(text)} characters")  # Debug print
    
    print("\n Analyzing paper...")
    analysis = assistant.analyze_paper(text)
    print("\nAnalysis:")
    print(analysis)
    
    print("\n Generating follow-up questions...")
    questions = assistant.generate_questions(analysis)
    print("\nQuestions to explore:")
    print(questions)
    
    print("\n Creating simplified explanation...")
    simple_explanation = assistant.simplify_explanation(analysis)
    print("\nSimplified Explanation:")
    print(simple_explanation)

if __name__ == "__main__":
    main()
