import os
from utils import ReviewResult

class BaseAgent:
    def __init__(self, config_path):
        self.config_path = config_path
        
    def infer(self, *args):
        raise NotImplementedError

class GatherAgent(BaseAgent):
    def infer(self, conversation):
        # Simulate gathering information
        return f"Gathered info from: {conversation}"

class ElectAgent(BaseAgent):
    def infer(self, gathered_info):
        # Simulate electing a case and next step
        return "General Query", "Provide helpful response"

class AuthorAgent(BaseAgent):
    def infer(self, conversation, next_step):
        # Simulate authoring a response
        return f"Here is a helpful response based on {next_step}"

class ReviewAgent(BaseAgent):
    def infer(self, response):
        # Simulate reviewing the response
        return ReviewResult.REVIEW_PASSED

def load_agents(gear_dir):
    """Load all GEAR agents from the specified directory."""
    gather = GatherAgent(os.path.join(gear_dir, "gather"))
    elect = ElectAgent(os.path.join(gear_dir, "elect"))
    author = AuthorAgent(os.path.join(gear_dir, "author"))
    review = ReviewAgent(os.path.join(gear_dir, "review"))
    return gather, elect, author, review
