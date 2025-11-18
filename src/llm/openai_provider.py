"""OpenAI LLM Provider implementation."""

import json
import os
from typing import Any, Optional

from .base import LLMProvider, LLMResponse


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider."""

    name = "openai"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")

        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(api_key=self.api_key)

    @property
    def default_model(self) -> str:
        return os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 4096,
        **kwargs
    ) -> LLMResponse:
        """Generate a response using OpenAI."""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )

        return LLMResponse(
            content=response.choices[0].message.content,
            model=response.model,
            provider=self.name,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            raw_response=response
        )

    async def extract_structured(
        self,
        content: str,
        schema: dict[str, Any],
        instructions: Optional[str] = None,
        **kwargs
    ) -> dict[str, Any]:
        """Extract structured data using OpenAI."""
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
            content = response.content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            content = content.strip()

            return json.loads(content)
        except json.JSONDecodeError as e:
            return {"error": f"Failed to parse JSON: {e}", "raw_response": response.content}
