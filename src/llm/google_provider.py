"""Google Gemini LLM Provider implementation."""

import json
import os
from typing import Any, Optional

from .base import LLMProvider, LLMResponse


class GoogleProvider(LLMProvider):
    """Google Gemini provider."""

    name = "google"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key is required. Set GOOGLE_API_KEY environment variable.")

        import google.generativeai as genai
        genai.configure(api_key=self.api_key)
        self.genai = genai

    @property
    def default_model(self) -> str:
        return os.getenv("GOOGLE_MODEL", "gemini-pro")

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 4096,
        **kwargs
    ) -> LLMResponse:
        """Generate a response using Google Gemini."""
        model = self.genai.GenerativeModel(self.model)

        # Combine system prompt with user prompt if provided
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        generation_config = self.genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )

        response = await model.generate_content_async(
            full_prompt,
            generation_config=generation_config,
        )

        # Note: Gemini doesn't provide token counts in the same way
        return LLMResponse(
            content=response.text,
            model=self.model,
            provider=self.name,
            usage={},  # Gemini API doesn't always provide usage stats
            raw_response=response
        )

    async def extract_structured(
        self,
        content: str,
        schema: dict[str, Any],
        instructions: Optional[str] = None,
        **kwargs
    ) -> dict[str, Any]:
        """Extract structured data using Google Gemini."""
        prompt = self._build_extraction_prompt(content, schema, instructions)

        system_prompt = """You are a data extraction assistant. Your job is to extract structured information from content and return it as valid JSON. Always return only the JSON object, no explanations or markdown."""

        response = await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.0,
            **kwargs
        )

        # Parse JSON response
        try:
            # Clean up response - remove markdown code blocks if present
            resp_content = response.content.strip()
            if resp_content.startswith("```"):
                resp_content = resp_content.split("```")[1]
                if resp_content.startswith("json"):
                    resp_content = resp_content[4:]
            resp_content = resp_content.strip()

            return json.loads(resp_content)
        except json.JSONDecodeError as e:
            return {"error": f"Failed to parse JSON: {e}", "raw_response": response.content}
