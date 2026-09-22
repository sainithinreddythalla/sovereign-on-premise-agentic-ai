from typing import Protocol

from ai.config import AIConfig
from ai.router import ModelRouter
from ai.schemas import GenerationRequest, GenerationResponse, ModelInfo


class AIProvider(Protocol):
    """Interface that every AI model provider must implement."""

    def generate(
        self,
        model: ModelInfo,
        prompt: str,
        context: list[dict],
        config: AIConfig,
    ) -> str:
        ...


class AIService:
    """Provider-independent AI service."""

    def __init__(
        self,
        config: AIConfig,
        router: ModelRouter,
        provider: AIProvider,
    ) -> None:
        self.config = config
        self.router = router
        self.provider = provider

    def generate(
        self,
        request: GenerationRequest,
        models: list[ModelInfo],
    ) -> GenerationResponse:
        """Route a request to a suitable model and generate an answer."""

        model = self.router.select_model(
            models=models,
            task_type=request.task_type,
            requested_model=request.model,
        )

        answer = self.provider.generate(
            model=model,
            prompt=request.prompt,
            context=request.context,
            config=self.config,
        )

        return GenerationResponse(
            model=model.name,
            answer=answer,
            verification_status="requires_review",
            metadata={
                "generated_analysis": True,
                "evidence_verified": False,
                "verification_owner": "agent",
            },
        )