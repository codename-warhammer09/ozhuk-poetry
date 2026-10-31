import logging
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
from .llm_handler import LLMHandler

logger = logging.getLogger(__name__)

class CritiqueVerdict(str, Enum):
    PASS = "PASS"
    NEEDS_WORK = "NEEDS_WORK"

class CritiqueResult(BaseModel):
    strengths: str = Field(description="What the poet did well in terms of imagery, rhythm, or word choice.")
    technical_analysis: str = Field(description="Detailed technical breakdown of how the target milestone concept was applied.")
    suggestion: str = Field(description="Actionable, concrete recommendations for polishing the poem.")
    verdict: CritiqueVerdict = Field(description="PASS if the poem meets the milestone criteria, otherwise NEEDS_WORK.")

class PoetryCritic:
    """
    Specialized module to critique user poems based on the current 
    curriculum milestone using Gemma 4 on the heavy model tier.
    """
    def __init__(self, llm: Optional[LLMHandler] = None):
        self.llm = llm if llm is not None else LLMHandler()

    def critique_poem(self, poem: str, milestone_name: str, stage_name: str) -> CritiqueResult:
        """
        Provides a structured, constructive critique of a poem 
        relative to a specific poetic milestone concept using Gemma 4.
        """
        system_prompt = (
            "You are the Ozhuk Critic, a master of the Three-Stone Hearth (Ozhuk Dazhy). "
            "Your goal is to provide constructive, precise, and encouraging critiques "
            "of student poetry. Focus rigorously on the target concept while evaluating "
            "metrical flow, imagery, and structural cohesion. If the poem genuinely demonstrates "
            "competence in the target concept, grant a PASS verdict. If it requires significant rework, "
            "grant NEEDS_WORK."
        )

        prompt = (
            f"Curriculum Stage: {stage_name}\n"
            f"Target Milestone Concept: {milestone_name}\n\n"
            f"Poem for Critique:\n"
            f"---\n"
            f"{poem}\n"
            f"---\n\n"
            "Analyze the poem and provide your critique matching the required schema."
        )

        try:
            return self.llm.generate_structured(
                prompt=prompt,
                response_schema=CritiqueResult,
                system_prompt=system_prompt,
                model_tier="heavy",
            )
        except Exception as e:
            logger.error(f"Structured critique generation failed: {e}")
            # Fallback return in case API is unavailable or unconfigured
            return CritiqueResult(
                strengths="Unable to generate automated critique at this moment.",
                technical_analysis=f"Analysis unavailable: {str(e)}",
                suggestion="Please verify your GEMINI_API_KEY and network connection.",
                verdict=CritiqueVerdict.NEEDS_WORK,
            )
