import logging
import httpx
from typing import Optional
from pydantic import BaseModel, Field
from .llm_handler import LLMHandler

logger = logging.getLogger(__name__)

class OzhukAnalysis(BaseModel):
    title: str = Field(description="Title of the poem or excerpt")
    author: str = Field(description="Author of the poem or excerpt")
    excerpt: str = Field(description="The analysed lines of poetry")
    hearth_stone_1_setup: str = Field(description="Exposure / Setting / Sensory Imagery (Stone 1)")
    hearth_stone_2_development: str = Field(description="Mechanics & Poetic Devices (Stone 2)")
    hearth_stone_3_resolution: str = Field(description="Scansion, Rhythm & Core Theme (Stone 3)")
    socratic_challenge: str = Field(description="Interactive prompt or exercise for the student")

# Shared LLMHandler instance for engine
llm = LLMHandler()

def fetch_poem_excerpt(query: str = "road") -> str:
    """Fetch live poem excerpts from PoetryDB to serve as dynamic examples."""
    try:
        url = f"https://poetrydb.org/title/{query}"
        resp = httpx.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                poem = data[0]
                lines = "\n".join(poem.get("lines", [])[:8])
                return f"Title: {poem.get('title', 'Unknown')}\nAuthor: {poem.get('author', 'Unknown')}\n\n{lines}"
    except Exception as e:
        logger.warning(f"PoetryDB fetch failed: {e}. Using offline fallback excerpt.")

    return (
        "Title: The Road Not Taken\n"
        "Author: Robert Frost\n\n"
        "Two roads diverged in a yellow wood,\n"
        "And sorry I could not travel both\n"
        "And be one traveler, long I stood\n"
        "And looked down one as far as I could\n"
        "To where it bent in the undergrowth..."
    )

def analyze_poem_with_ozhuk(
    concept: str,
    poem_text: str = "",
) -> OzhukAnalysis:
    """Sends text excerpt to Gemma 4 via LLMHandler using structured JSON output."""

    prompt = f"""
    You are Ozhuk AI, an open-source poetry tutor and scansion engine structured around the three-stone hearth triad (Ozhuk Dazhy).
    Target Literary Concept: {concept}
    Text Excerpt:
    {poem_text}

    Break down the input into the Three Hearth Stones of poetic analysis:
    1. Setup/Exposure (Stone 1): The literal scenario, setting, and sensory imagery.
    2. Development (Stone 2): Key poetic devices, metaphors, and stylistic mechanics.
    3. Resolution (Stone 3): Metrical scansion, rhythm breakdown, and core theme synthesis.

    End with a beginner-friendly Socratic exercise or prompt for the student.
    """

    try:
        return llm.generate_structured(
            prompt=prompt,
            response_schema=OzhukAnalysis,
            model_tier="heavy",
        )
    except Exception as e:
        logger.error(f"Ozhuk analysis generation failed: {e}")
        return OzhukAnalysis(
            title="Analysis Notice",
            author="Ozhuk AI",
            excerpt=poem_text[:200] if poem_text else "No excerpt provided",
            hearth_stone_1_setup="Unable to complete structured analysis due to connection or configuration error.",
            hearth_stone_2_development=str(e),
            hearth_stone_3_resolution="Please check your GEMINI_API_KEY.",
            socratic_challenge="Try again after verifying your API credentials."
        )
