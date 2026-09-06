from registry import ModelRegistry
from schemas import ModelInfo


def test_register_and_get_model():
    registry = ModelRegistry()

    model = ModelInfo(
        name="test-model",
        provider="test",
        capabilities=["general"],
        available=True,
    )

    registry.register(model)

    result = registry.get("test-model")

    assert result == model