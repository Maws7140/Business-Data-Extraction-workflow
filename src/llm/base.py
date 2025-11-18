"""Base classes for LLM providers."""

from abc import ABC, abstractmethod
from typing import Any, Optional
from pydantic import BaseModel


class LLMResponse(BaseModel):
    """Standard response from LLM providers."""

    content: str
    model: str
    provider: str
    usage: dict[str, int] = {}
    raw_response: Optional[Any] = None

    class Config:
        arbitrary_types_allowed = True


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    name: str = "base"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, **kwargs):
        self.api_key = api_key
        self.model = model or self.default_model
        self.kwargs = kwargs

    @property
    @abstractmethod
    def default_model(self) -> str:
        """Return the default model for this provider."""
        pass

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 4096,
        **kwargs
    ) -> LLMResponse:
        """Generate a response from the LLM."""
        pass

    @abstractmethod
    async def extract_structured(
        self,
        content: str,
        schema: dict[str, Any],
        instructions: Optional[str] = None,
        **kwargs
    ) -> dict[str, Any]:
        """Extract structured data from content based on schema."""
        pass

    def _build_extraction_prompt(self, content: str, schema: dict[str, Any], instructions: Optional[str] = None) -> str:
        """Build the extraction prompt with schema."""
        schema_desc = self._schema_to_description(schema)

        prompt = f"""Extract structured data from the following content based on this schema:

## Schema
{schema_desc}

## Instructions
{instructions or "Extract all relevant information that matches the schema. Return valid JSON only."}

## Content
{content}

## Output
Return ONLY valid JSON matching the schema. No explanations or markdown formatting."""

        return prompt

    def _schema_to_description(self, schema: dict[str, Any]) -> str:
        """Convert schema dict to human-readable description."""
        lines = []
        for field, field_type in schema.items():
            if isinstance(field_type, dict):
                if "type" in field_type:
                    type_str = field_type["type"]
                    desc = field_type.get("description", "")
                    lines.append(f"- {field} ({type_str}): {desc}")
                else:
                    lines.append(f"- {field}: nested object")
            else:
                lines.append(f"- {field}: {field_type}")
        return "\n".join(lines)
