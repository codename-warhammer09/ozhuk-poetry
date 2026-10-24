# OZHUK ENGINE.
# AI-ASSISTED DEVELOPMENT BY TEAM FUTRUS (A.A Mirza and M. A. Qaisar) 
# FOR HACKTOBERFEST HACK DAY 24/10/2026
# As part of the Challenge, for best Use, of Gemma4
# WIP

import os
import httpx
from pydantic import BaseModel
from google import genai
from google.genai import types
from PIL import Image

class OzhukAnalysis(BaseModel):
    title: str
    author: str
    excerpt: str
    hearth_stone_1_setup: str       # Exposure / Setting / Sensory Imagery
    hearth_stone_2_development: str # Mechanics & Poetic Devices
    hearth_stone_3_resolution: str  # Scansion, Rhythm & Core Theme
    socratic_challenge: str         # Interactive prompt for the user

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
    """Sends text or manuscript image to Gemma 4 via the Gemini API using structured JSON output."""
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    
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
    
    contents = [prompt]
    if image:
        contents.append(image)
        
    response = client.models.generate_content(
        model="gemma-4-31b-it",
        contents=contents,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=OzhukAnalysis,
        ),
    )
    
    return OzhukAnalysis.model_validate_json(response.text)