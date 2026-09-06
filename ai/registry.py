from typing import Iterable

from schemas import ModelInfo


class ModelRegistry:
    """Stores metadata about available AI models."""

    def __init__(self) -> None:
        self._models: dict[str, ModelInfo] = {}

    def register(self, model: ModelInfo) -> None:
        """Register or replace a model."""
        self._models[model.name] = model

    def get(self, name: str) -> ModelInfo | None:
        """Return a model by name."""
        return self._models.get(name)

    def list_models(self) -> list[ModelInfo]:
        """Return all registered models."""
        return list(self._models.values())

    def available_models(self) -> list[ModelInfo]:
        """Return only currently available models."""
        return [model for model in self._models.values() if model.available]

    def names(self) -> Iterable[str]:
        """Return registered model names."""
        return self._models.keys()