from ai.schemas import ModelInfo, TaskType

class ModelRouter:
    """Selects the most suitable model for a requested task."""

    def select_model(
        self,
        models: list[ModelInfo],
        task_type: TaskType,
        requested_model: str | None = None,
    ) -> ModelInfo:
        """Select an available model based on request and capability."""

        available = [model for model in models if model.available]

        if requested_model:
            for model in available:
                if model.name == requested_model:
                    return model

            raise ValueError(
                f"Requested model '{requested_model}' is not available."
            )

        capability = task_type

        for model in available:
            if capability in model.capabilities:
                return model

        if available:
            return available[0]

        raise RuntimeError("No available AI models are registered.")