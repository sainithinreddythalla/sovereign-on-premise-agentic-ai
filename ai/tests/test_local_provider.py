import json

from ai.config import AIConfig
from ai.providers.local import LocalProvider
from ai.schemas import ModelInfo


class FakeResponse:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self):
        return json.dumps({"answer": "Local model response"}).encode("utf-8")


def test_local_provider_generates_with_mocked_http(monkeypatch):
    def fake_urlopen(request, timeout):
        assert request.method == "POST"
        assert timeout == 120
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
        config=AIConfig(base_url="http://127.0.0.1:8000/generate"),
    )

    assert response == "Local model response"


def test_local_provider_fails_without_configuration():
    provider = LocalProvider()

    try:
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
    except RuntimeError as exc:
        assert str(exc) == "No local AI provider is configured."
    else:
        raise AssertionError("Expected RuntimeError")