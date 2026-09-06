from dataclasses import dataclass, field
from typing import Any, Literal


TaskType = Literal[
    "general",
    "reasoning",
    "vision",
]


@dataclass
class GenerationRequest:
    """Input passed to the AI service."""

    prompt: str
    task_type: TaskType = "general"
    context: list[dict[str, Any]] = field(default_factory=list)
    model: str | None = None


@dataclass
class GenerationResponse:
    """Standard response returned by the AI service."""

    model: str
    answer: str
    verification_status: str = "requires_review"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelInfo:
    """Metadata describing an available AI model."""

    name: str
    provider: str
    capabilities: list[str] = field(default_factory=list)
    available: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)