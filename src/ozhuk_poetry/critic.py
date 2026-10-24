import logging
from typing import Dict, Any
from .llm_handler import LLMHandler

logger = logging.getLogger(__name__)

class PoetryCritic:
    """
    Specialized module to critique user poems based on the current 
    curriculum milestone.
    """
    def __init__(self):
        self.llm = LLMHandler()

    def critique_poem(self, poem: str, milestone_name: str, stage_name: str) -> Dict[str, Any]:
        """
        Provides a detailed, constructive critique of a poem 
        relative to a specific poetic concept.
        """
        system_prompt = (
            "You are the Ozhuk Critic, a master of the Three-Stone Hearth. "
            "Your goal is to provide constructive, precise, and encouraging "
            "critiques of student poetry. Focus specifically on the target concept "
            "while considering the overall poetic flow."
        )
        
        prompt = (
            f"Student is currently in Stage: {stage_name}\n"
            f"Target Milestone Concept: {milestone_name}\n\n"
            f"Poem for Critique:\n---\n{poem}\n---\n\n"
            "Please provide a critique in the following format:\n"
            "1. **Strengths**: What the poet did well.\n"
            "2. **Technical Analysis**: How well they applied the target concept.\n"
            "3. **Ozhuk's Suggestion**: One concrete way to improve the piece.\n"
            "4. **Verdict**: (Pass/Needs Work) - determine if this meets the milestone requirement."
        )

        res = self.llm.generate(prompt, system_prompt)
        return {"critique": res["text"], "mode": res["mode"]}
