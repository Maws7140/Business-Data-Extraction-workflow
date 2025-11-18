"""Anthropic Claude LLM Provider implementation."""

import json
import os
from typing import Any, Optional

from .base import LLMProvider, LLMResponse


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider."""

    name = "anthropic"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key is required. Set ANTHROPIC_API_KEY environment variable.")

        from anthropic import AsyncAnthropic
        self.client = AsyncAnthropic(api_key=self.api_key)

    @property
    def default_model(self) -> str:
        return os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 4096,
        **kwargs
    ) -> LLMResponse:
        """Generate a response using Anthropic Claude."""
        messages = [{"role": "user", "content": prompt}]

        create_kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if system_prompt:
            create_kwargs["system"] = system_prompt

        response = await self.client.messages.create(**create_kwargs)

        return LLMResponse(
            content=response.content[0].text,
            model=response.model,
            provider=self.name,
            usage={
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
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
        """Extract structured data using Anthropic Claude."""
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
