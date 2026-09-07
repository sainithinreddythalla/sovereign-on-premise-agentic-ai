from ai.config import get_config
from ai.providers.local import LocalProvider
from ai.registry import ModelRegistry
from ai.router import ModelRouter
from ai.schemas import GenerationRequest, GenerationResponse, ModelInfo
from ai.service import AIService


def create_ai_service() -> tuple[AIService, ModelRegistry]:
    """Create the configured AI service and model registry."""

    config = get_config()

    if not config.base_url:
        raise RuntimeError("No local AI provider is configured.")

    registry = ModelRegistry()

    registry.register(
        ModelInfo(
            name=config.default_model,
            provider=config.provider,
            capabilities=["general", "reasoning", "vision"],
            available=True,
        )
    )

    service = AIService(
        config=config,
        router=ModelRouter(),
        provider=LocalProvider(),
    )

    return service, registry


def generate(request: GenerationRequest) -> GenerationResponse:
    """Generate a response through the existing AI service."""

    service, registry = create_ai_service()

    return service.generate(
        request=request,
        models=registry.list_models(),
    )