import os
import together
from typing import Dict, List, Tuple
import json
from datetime import datetime

# Set your API key
os.environ["TOGETHER_API_KEY"] = "72485359b7b96fc4c31a44e232cf4b0608c60c5d8b8123f892836192a168c540"

class BaseAgent:
    def __init__(self, model="mistralai/Mistral-7B-Instruct-v0.2"):
        self.client = together.Together()
        self.model = model

    def _call_model(self, prompt: str, temperature: float = 0.7) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=1024
        )
        return response.choices[0].message.content

class IntentClassifierAgent(BaseAgent):
    """Identifies the main intent and category of customer inquiry"""
    
    def classify(self, message: str) -> Dict[str, str]:
        prompt = f"""<s>[INST] Analyze this customer message and classify it into:
        1. Primary Intent (question, complaint, feature request, bug report, billing)
        2. Category (technical, account, billing, product, other)
        3. Priority (high, medium, low)
        4. Sentiment (positive, neutral, negative)

        Message: {message}

        Return a JSON object with these classifications. [/INST]</s>"""
        
        result = self._call_model(prompt, temperature=0.3)
        return json.loads(result)

class KnowledgeAgent(BaseAgent):
    """Retrieves relevant information from knowledge base"""
    
    def __init__(self):
        super().__init__()
        # Simulate a knowledge base with some entries
        self.knowledge_base = {
            "technical": {
                "login": "Common login issues and solutions...",
                "performance": "Performance troubleshooting steps...",
                "integration": "API integration guidelines..."
            },
            "billing": {
                "subscription": "Subscription management details...",
                "payment": "Payment processing information...",
                "refund": "Refund policy and procedures..."
            }
        }

    def search(self, category: str, intent: str) -> str:
        # Simulate knowledge base search
        base_info = self.knowledge_base.get(category, {}).get(intent, "")
        
        prompt = f"""<s>[INST] Based on this knowledge base information, 
        provide relevant details that could help address a customer inquiry:

        Category: {category}
        Intent: {intent}
        Base Information: {base_info}

        Format the response in a clear, helpful manner. [/INST]</s>"""
        
        return self._call_model(prompt, temperature=0.5)

class ResponseGeneratorAgent(BaseAgent):
    """Generates personalized customer responses"""
    
    def generate_response(self, 
                         message: str, 
                         classification: Dict[str, str], 
                         knowledge: str) -> str:
        prompt = f"""<s>[INST] Create a customer service response with these components:
        1. Empathetic greeting based on sentiment
        2. Clear acknowledgment of the issue
        3. Specific solution or next steps
        4. Additional helpful resources
        5. Professional closing

        Original Message: {message}
        Classification: {json.dumps(classification)}
        Knowledge Base Info: {knowledge}

        Make the response personal, professional, and solution-focused. [/INST]</s>"""
        
        return self._call_model(prompt, temperature=0.7)

class QualityCheckerAgent(BaseAgent):
    """Ensures response quality and compliance"""
    
    def check_response(self, 
                      original_message: str, 
                      response: str, 
                      classification: Dict[str, str]) -> Tuple[bool, str]:
        prompt = f"""<s>[INST] Evaluate this customer service response for:
        1. Accuracy of solution
        2. Tone appropriateness
        3. Completeness
        4. Compliance with standard practices
        5. Grammar and clarity

        Original Message: {original_message}
        Response: {response}
        Classification: {json.dumps(classification)}

        Return a JSON object with:
        - "approved": boolean
        - "feedback": string with any improvement suggestions [/INST]</s>"""
        
        result = json.loads(self._call_model(prompt, temperature=0.3))
        return result["approved"], result["feedback"]

class CustomerSupportSystem:
    def __init__(self):
        self.intent_classifier = IntentClassifierAgent()
        self.knowledge_agent = KnowledgeAgent()
        self.response_generator = ResponseGeneratorAgent()
        self.quality_checker = QualityCheckerAgent()
        
    def process_inquiry(self, customer_message: str) -> Dict:
        # Step 1: Classify the inquiry
        classification = self.intent_classifier.classify(customer_message)
        print(f"\n1. Classification: {json.dumps(classification, indent=2)}")
        
        # Step 2: Retrieve relevant knowledge
        knowledge = self.knowledge_agent.search(
            classification.get("category"),
            classification.get("primary_intent")
        )
        print("\n2. Retrieved relevant knowledge")
        
        # Step 3: Generate response
        response = self.response_generator.generate_response(
            customer_message,
            classification,
            knowledge
        )
        print("\n3. Generated initial response")
        
        # Step 4: Quality check
        approved, feedback = self.quality_checker.check_response(
            customer_message,
            response,
            classification
        )
        print(f"\n4. Quality check: {'Approved' if approved else 'Needs revision'}")
        
        if not approved:
            # Regenerate response incorporating feedback
            prompt = f"Original response: {response}\nFeedback: {feedback}\nPlease revise accordingly."
            response = self.response_generator._call_model(prompt)
            print("\n5. Generated revised response")
        
        return {
            "classification": classification,
            "response": response,
            "quality_check": {"approved": approved, "feedback": feedback},
            "timestamp": datetime.now().isoformat()
        }

def main():
    support_system = CustomerSupportSystem()
    
    print("🤖 Multi-Agent Customer Support System")
    print("Enter customer message (press Return twice when done):")
    
    lines = []
    while True:
        line = input()
        if line == "" and (len(lines) == 0 or lines[-1] == ""):
            break
        lines.append(line)
    
    customer_message = "\n".join(lines)
    
    print("\n📝 Processing inquiry...")
    result = support_system.process_inquiry(customer_message)
    
    print("\n=== Final Response ===")
    print(result["response"])
    print("\n=== Processing Details ===")
    print(json.dumps(result["classification"], indent=2))
    print("\nQuality Check:", "✅ Approved" if result["quality_check"]["approved"] else "❌ Needs Revision")
    if not result["quality_check"]["approved"]:
        print("Feedback:", result["quality_check"]["feedback"])

if __name__ == "__main__":
    main()
