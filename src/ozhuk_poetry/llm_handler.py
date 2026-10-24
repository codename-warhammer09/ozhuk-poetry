import os
import json
import logging
from typing import Any, Dict, Optional, Union
import httpx
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMHandler:
    """
    Unified interface for LLM calls with a priority-based fallback:
    gemma4:31b-it (Primary/Cloud) -> Local Ollama (Fallback)
    """
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.ollama_url = "http://localhost:11434/api/generate"
        self.primary_model = "gemma4:31b-it"
        self.light_model = "gemma4:e4b-it"
        self.fallback_model = "gemma4:e4b"

        self.client = None
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)

        self.current_mode = "cloud" # 'cloud' or 'local'

    def _call_ollama(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Calls the local Ollama instance using the chat API."""
        try:
            # Using /api/chat for better compatibility with modern Ollama
            url = "http://localhost:11434/api/chat"
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            payload = {
                "model": self.fallback_model,
                "messages": messages,
                "stream": False
            }
            response = httpx.post(url, json=payload, timeout=30.0)
            response.raise_for_status()
            return response.json().get("message", {}).get("content", "")
        except Exception as e:
            logger.error(f"Ollama call failed: {e}")
            raise ConnectionError(f"Local LLM unavailable: {e}")

    def _call_gemini(self, prompt: str, system_prompt: Optional[str] = None, model: Optional[str] = None) -> str:
        """Calls the Gemini API."""
        if not self.client:
            raise ConnectionError("Gemini API key not configured")

        # Use provided model or default to primary
        model_id = model if model else self.primary_model

        # For simple chat, we can use generate_content
        # In a real app, we'd maintain chat history here or pass it in
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        response = self.client.models.generate_content(
            model=model_id,
            contents=full_prompt
        )
        return response.text

    def generate(self, prompt: str, system_prompt: Optional[str] = None, model_tier: str = "light") -> Dict[str, Any]:
        """
        Generates a response with fallback logic.
        model_tier: "light" (for chat/routing) or "heavy" (for analysis/critique).
        Returns a dict containing the text and the mode used.
        """
        # Select model based on tier
        target_model = self.primary_model if model_tier == "heavy" else self.light_model

        # Priority: Cloud -> Local
        try:
            # Try Cloud first
            text = self._call_gemini(prompt, system_prompt, model=target_model)
            self.current_mode = "cloud"
            return {"text": text, "mode": "cloud"}
        except Exception as e:
            logger.warning(f"Primary LLM failed, attempting fallback: {e}")
            try:
                # Fallback to Local (which is always the light version gemma4:4b)
                text = self._call_ollama(prompt, system_prompt)
                self.current_mode = "local"
                return {"text": text, "mode": "local"}
            except Exception as e_local:
                logger.error(f"Both LLMs failed: {e_local}")
                return {"text": "I'm sorry, I'm having trouble connecting to my brain right now. Please check your connection.", "mode": "error"}

    def generate_structured(self, prompt: str, response_schema: Any, system_prompt: Optional[str] = None) -> Any:
        """
        Generates structured output using Pydantic schema.
        Currently, structured output is best supported by the Cloud API.
        """
        try:
            if not self.client:
                raise ConnectionError("Gemini API key not configured")

            # Structured output is a primary feature of the 31B model via genai
            response = self.client.models.generate_content(
                model=self.primary_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=response_schema,
                ),
            )
            return response.parsed
        except Exception as e:
            logger.error(f"Structured generation failed: {e}")
            # Fallback for structured: Prompt local model to return JSON and manually parse
            # (This is a simplification, a full implementation would use a JSON parser)
            res = self.generate(f"{prompt}\n\nPlease return the response strictly as JSON matching the schema.", system_prompt)
            return res["text"]
