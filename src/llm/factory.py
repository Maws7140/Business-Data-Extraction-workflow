"""Factory for creating LLM providers."""

import os
from typing import Optional

from .base import LLMProvider
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .google_provider import GoogleProvider
from .ollama_provider import OllamaProvider


PROVIDERS = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "google": GoogleProvider,
    "ollama": OllamaProvider,
}


def get_provider(
    provider_name: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    **kwargs
) -> LLMProvider:
    """
    Get an LLM provider instance.

    Args:
        provider_name: Name of the provider (openai, anthropic, google, ollama)
        api_key: API key for the provider
        model: Model name to use
        **kwargs: Additional provider-specific arguments

    Returns:
        LLMProvider instance
    """
    if provider_name is None:
        provider_name = os.getenv("DEFAULT_LLM_PROVIDER", "openai")

    provider_name = provider_name.lower()

    if provider_name not in PROVIDERS:
        raise ValueError(
            f"Unknown provider: {provider_name}. "
            f"Available providers: {list(PROVIDERS.keys())}"
        )

    provider_class = PROVIDERS[provider_name]
    return provider_class(api_key=api_key, model=model, **kwargs)


def list_providers() -> list[str]:
    """Return list of available provider names."""
    return list(PROVIDERS.keys())
