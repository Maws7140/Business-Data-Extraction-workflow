"""Ollama (local) LLM Provider implementation."""

import json
import os
from typing import Any, Optional

import httpx

from .base import LLMProvider, LLMResponse


class OllamaProvider(LLMProvider):
    """Ollama local LLM provider."""

    name = "ollama"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.base_url = kwargs.get("base_url") or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    @property
    def default_model(self) -> str:
        return os.getenv("OLLAMA_MODEL", "llama2")

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 4096,
        **kwargs
    ) -> LLMResponse:
        """Generate a response using Ollama."""
        # Build the full prompt
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json=payload
            )
            response.raise_for_status()
            data = response.json()

        return LLMResponse(
            content=data.get("response", ""),
            model=self.model,
            provider=self.name,
            usage={
                "prompt_tokens": data.get("prompt_eval_count", 0),
                "completion_tokens": data.get("eval_count", 0),
                "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0),
            },
            raw_response=data
        )

    async def extract_structured(
        self,
        content: str,
        schema: dict[str, Any],
        instructions: Optional[str] = None,
        **kwargs
    ) -> dict[str, Any]:
        """Extract structured data using Ollama."""
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
