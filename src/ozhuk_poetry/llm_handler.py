import os
import re
import json
import time
import logging
from typing import Any, Dict, Optional, Type, TypeVar
from google import genai
from google.genai import types
from google.genai import errors
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

def extract_json_string(text: str) -> str:
    """Extracts valid JSON payload from text, stripping any markdown code fences."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()

    first_brace = cleaned.find("{")
    last_brace = cleaned.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        return cleaned[first_brace : last_brace + 1]

    return cleaned

class LLMHandler:
    """
    Unified interface for Gemini API calls:
    - Primary/Heavy: gemma-4-31b-it (for deep literary analysis, scansion, and structured critique)
    - Light / Resilient Failover: gemini-flash-lite-latest (for conversational chat, routing, quick guidance)
    """
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.primary_model = os.getenv("GEMINI_PRIMARY_MODEL", "gemma-4-31b-it")
        self.light_model = os.getenv("GEMINI_LIGHT_MODEL", "gemini-flash-lite-latest")

        self.client = None
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)

    def is_configured(self) -> bool:
        """Returns True if the Gemini client is initialized with an API key."""
        return self.client is not None

    def _get_target_model(self, model_tier: str, override_model: Optional[str] = None) -> str:
        if override_model:
            return override_model
        return self.primary_model if model_tier == "heavy" else self.light_model

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model_tier: str = "light",
        model: Optional[str] = None,
        max_retries: int = 1,
    ) -> Dict[str, Any]:
        """
        Generates standard text response via Gemini API with transient retry and resilient failover.
        """
        if not self.client:
            logger.warning("Gemini API key is not configured.")
            return {
                "text": "Gemini API key is not configured. Please set GEMINI_API_KEY in your .env file.",
                "mode": "unconfigured",
                "model": None,
            }

        target_model = self._get_target_model(model_tier, override_model=model)

        config = None
        if system_prompt:
            config = types.GenerateContentConfig(system_instruction=system_prompt)

        last_error = None
        for attempt in range(max_retries + 1):
            try:
                response = self.client.models.generate_content(
                    model=target_model,
                    contents=prompt,
                    config=config,
                )
                return {
                    "text": response.text or "",
                    "mode": "cloud",
                    "model": target_model,
                }
            except errors.ServerError as e:
                last_error = e
                logger.warning(f"Transient server error on {target_model} (attempt {attempt + 1}/{max_retries + 1}): {e}")
                if attempt < max_retries:
                    time.sleep(1.0 * (attempt + 1))
            except errors.APIError as e:
                logger.error(f"Gemini API error ({target_model}): {e}")
                last_error = e
                break
            except Exception as e:
                logger.error(f"Unexpected error during generation ({target_model}): {e}")
                last_error = e
                break

        # If heavy model failed due to high demand/server error, failover to light model
        if target_model != self.light_model:
            logger.warning(f"Heavy model {target_model} unavailable. Resiliently failing over to {self.light_model}...")
            return self.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                model_tier="light",
                model=self.light_model,
                max_retries=1,
            )

        return {
            "text": f"Ozhuk encountered a temporary server error with {target_model}. Please try again.",
            "mode": "error",
            "model": target_model,
            "error": str(last_error),
        }

    def generate_structured(
        self,
        prompt: str,
        response_schema: Type[T],
        system_prompt: Optional[str] = None,
        model_tier: str = "heavy",
        model: Optional[str] = None,
        max_retries: int = 1,
    ) -> T:
        """
        Generates structured output validated against a Pydantic schema using Gemini API.
        Includes automatic retry and resilient cloud failover if Gemma 4 experiences server capacity spikes.
        """
        if not self.client:
            raise ConnectionError("Gemini API key is not configured. Set GEMINI_API_KEY in .env.")

        target_model = self._get_target_model(model_tier, override_model=model)

        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=response_schema,
            system_instruction=system_prompt if system_prompt else None,
        )

        last_error = None
        for attempt in range(max_retries + 1):
            try:
                response = self.client.models.generate_content(
                    model=target_model,
                    contents=prompt,
                    config=config,
                )

                if response.parsed is not None and isinstance(response.parsed, response_schema):
                    return response.parsed

                if response.text:
                    cleaned_json = extract_json_string(response.text)
                    return response_schema.model_validate_json(cleaned_json)

                raise ValueError(f"Empty response received from {target_model}")
            except errors.ServerError as e:
                last_error = e
                logger.warning(f"Transient server error during structured generation ({target_model}, attempt {attempt + 1}): {e}")
                if attempt < max_retries:
                    time.sleep(1.0 * (attempt + 1))
            except Exception as e:
                logger.error(f"Structured generation error ({target_model}): {e}")
                last_error = e
                break

        # Resilient cloud failover: if primary Gemma 4 has 503 capacity issues, failover to light model
        if target_model != self.light_model:
            logger.warning(f"Primary model {target_model} capacity limit hit. Resiliently failing over to {self.light_model}...")
            return self.generate_structured(
                prompt=prompt,
                response_schema=response_schema,
                system_prompt=system_prompt,
                model_tier="light",
                model=self.light_model,
                max_retries=1,
            )

        raise last_error if last_error else RuntimeError(f"Structured generation failed after {max_retries} retries.")
