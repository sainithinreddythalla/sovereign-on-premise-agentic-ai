from schemas import ModelInfo


def get_model_health(model: ModelInfo) -> dict:
    """Return basic health information for a model."""

    return {
        "model": model.name,
        "provider": model.provider,
        "available": model.available,
        "status": "healthy" if model.available else "unavailable",
    }


def get_all_model_health(models: list[ModelInfo]) -> list[dict]:
    """Return health information for all registered models."""

    return [get_model_health(model) for model in models]