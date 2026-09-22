import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AIConfig:
    """Configuration for the AI/LLM layer."""

    provider: str = os.getenv("AI_PROVIDER", "local")
    default_model: str = os.getenv(
        "AI_DEFAULT_MODEL",
        "local-reasoning-model",
    )
    temperature: float = float(os.getenv("AI_TEMPERATURE", "0.2"))
    max_tokens: int = int(os.getenv("AI_MAX_TOKENS", "2048"))
    timeout_seconds: int = int(os.getenv("AI_TIMEOUT_SECONDS", "120"))
    base_url: str | None = os.getenv("AI_BASE_URL")


def get_config() -> AIConfig:
    """Return the current AI configuration."""
    return AIConfig()