import json

import pytest

from ai.config import AIConfig
from ai.providers.local import LocalProvider
from ai.schemas import ModelInfo


class FakeResponse:
    def read(self):
        return json.dumps(
            {"response": "Hello from Ollama"}
        ).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False


def test_local_provider_generates_with_mocked_http(monkeypatch):
    def fake_urlopen(request, timeout):
        assert request.method == "POST"
        assert timeout == 120

        payload = json.loads(request.data.decode("utf-8"))

        assert payload["model"] == "test-local-model"
        assert payload["prompt"] == "Hello"
        assert payload["stream"] is False
        assert payload["options"]["temperature"] == 0.2
        assert payload["options"]["num_predict"] == 2048

        return FakeResponse()

    monkeypatch.setattr(
        "ai.providers.local.urlopen",
        fake_urlopen,
    )

    provider = LocalProvider()

    response = provider.generate(
        model=ModelInfo(
            name="test-local-model",
            provider="local",
            capabilities=["general"],
            available=True,
        ),
        prompt="Hello",
        context=[],
        config=AIConfig(
            base_url="http://127.0.0.1:11434/api/generate"
        ),
    )

    assert response == "Hello from Ollama"


def test_local_provider_requires_base_url():
    provider = LocalProvider()

    with pytest.raises(
        RuntimeError,
        match="No local AI provider is configured.",
    ):
        provider.generate(
            model=ModelInfo(
                name="test-local-model",
                provider="local",
                capabilities=["general"],
                available=True,
            ),
            prompt="Hello",
            context=[],
            config=AIConfig(base_url=None),
        )