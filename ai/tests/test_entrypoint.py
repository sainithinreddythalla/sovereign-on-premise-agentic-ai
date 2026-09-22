import pytest

from ai.config import AIConfig
from ai.entrypoint import generate
from ai.schemas import GenerationRequest


def test_entrypoint_fails_when_local_provider_is_unavailable(monkeypatch):
    monkeypatch.setattr(
        "ai.entrypoint.get_config",
        lambda: AIConfig(base_url=None),
    )

    with pytest.raises(
        RuntimeError,
        match="No local AI provider is configured.",
    ):
        generate(
            GenerationRequest(
                prompt="Analyze the evidence.",
                task_type="reasoning",
            )
        )