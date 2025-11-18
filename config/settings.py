"""Application settings and configuration."""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # LLM Provider Settings
    default_llm_provider: str = Field(default="openai", env="DEFAULT_LLM_PROVIDER")

    # API Keys
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    google_api_key: Optional[str] = Field(default=None, env="GOOGLE_API_KEY")

    # Model Settings
    openai_model: str = Field(default="gpt-4-turbo-preview", env="OPENAI_MODEL")
    anthropic_model: str = Field(default="claude-3-sonnet-20240229", env="ANTHROPIC_MODEL")
    google_model: str = Field(default="gemini-pro", env="GOOGLE_MODEL")
    ollama_model: str = Field(default="llama2", env="OLLAMA_MODEL")
    ollama_base_url: str = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")

    # Server Settings
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    debug: bool = Field(default=False, env="DEBUG")

    # Extraction Settings
    max_content_length: int = Field(default=100000, env="MAX_CONTENT_LENGTH")
    request_timeout: int = Field(default=30, env="REQUEST_TIMEOUT")

    class Config:
        env_file = ".env"
        case_sensitive = False

    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for a specific provider."""
        key_map = {
            "openai": self.openai_api_key,
            "anthropic": self.anthropic_api_key,
            "google": self.google_api_key,
            "ollama": None,  # Ollama doesn't need API key
        }
        return key_map.get(provider.lower())

    def get_model(self, provider: str) -> str:
        """Get default model for a specific provider."""
        model_map = {
            "openai": self.openai_model,
            "anthropic": self.anthropic_model,
            "google": self.google_model,
            "ollama": self.ollama_model,
        }
        return model_map.get(provider.lower(), "")


# Global settings instance
settings = Settings()
