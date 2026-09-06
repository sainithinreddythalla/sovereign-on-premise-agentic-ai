from ai.router import ModelRouter
from ai.schemas import ModelInfo

def test_router_selects_matching_capability():
    router = ModelRouter()

    models = [
        ModelInfo(
            name="general-model",
            provider="test",
            capabilities=["general"],
            available=True,
        ),
        ModelInfo(
            name="reasoning-model",
            provider="test",
            capabilities=["reasoning"],
            available=True,
        ),
    ]

    selected = router.select_model(
        models=models,
        task_type="reasoning",
    )

    assert selected.name == "reasoning-model"