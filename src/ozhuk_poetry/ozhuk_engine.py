# OZHUK ENGINE.
# AI-ASSISTED DEVELOPMENT BY TEAM FUTRUS (A.A Mirza and M. A. Qaisar) 
# FOR HACKTOBERFEST HACK DAY 24/10/2026
# As part of the Challenge, for best Use, of Gemma4
# WIP

import os
import httpx
from pydantic import BaseModel
from PIL import Image
from .llm_handler import LLMHandler

class OzhukAnalysis(BaseModel):
    title: str
    author: str
    excerpt: str
    hearth_stone_1_setup: str       # Exposure / Setting / Sensory Imagery
    hearth_stone_2_development: str # Mechanics & Poetic Devices
    hearth_stone_3_resolution: str  # Scansion, Rhythm & Core Theme
    socratic_challenge: str         # Interactive prompt for the user

# Instantiate the handler globally for the engine
llm = LLMHandler()

def fetch_poem_excerpt(query: str = "road") -> str:
    """Fetch live poem excerpts from PoetryDB to serve as dynamic examples."""
    try:
        url = f"https://poetrydb.org/title/{query}"
        resp = httpx.get(url, timeout=5)
        if resp.status_code == 200 and len(resp.json()) > 0:
            poem = resp.json()[0]
            lines = "\n".join(poem.get("lines", [])[:8])
            return f"Title: {poem.get('title')}\nAuthor: {poem.get('author')}\n\n{lines}"
    except Exception:
        pass
    return (
        "Title: The Road Not Taken\n"
        "Author: Robert Frost\n\n"
        "Two roads diverged in a yellow wood,\n"
        "And sorry I could not travel both..."
    )

def analyze_poem_with_ozhuk(
    concept: str,
    poem_text: str = "",
    image: Image.Image | None = None
) -> OzhukAnalysis:
    """Sends text or manuscript image to Gemma 4 via the LLMHandler using structured JSON output."""

    prompt = f"""
    You are Ozhuk AI, an open-source poetry tutor and scansion engine structured around the three-stone hearth triad (Ozhuk Dazhy).
    Target Literary Concept: {concept}
    Text Excerpt: {poem_text}

    Break down the input into the Three Hearth Stones of poetic analysis:
    1. Setup/Exposure: The literal scenario, setting, and sensory imagery.
    2. Development: Key poetic devices, metaphors, and stylistic mechanics.
    3. Resolution: Metrical scansion, rhythm breakdown, and core theme synthesis.

    End with a beginner-friendly Socratic exercise or prompt for the user.
    """

    # Note: LLMHandler.generate_structured currently uses cloud API for Pydantic
    return llm.generate_structured(prompt, OzhukAnalysis)
