import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from ai.config import AIConfig
from ai.schemas import ModelInfo


class LocalProvider:
    """HTTP adapter for a locally hosted AI model."""

    def generate(
        self,
        model: ModelInfo,
        prompt: str,
        context: list[dict],
        config: AIConfig,
    ) -> str:
        if not config.base_url:
            raise RuntimeError("No local AI provider is configured.")

        payload = {
            "model": model.name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": config.temperature,
                "num_predict": config.max_tokens,
            },
        }

        request = Request(
            config.base_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urlopen(
                request,
                timeout=config.timeout_seconds,
            ) as response:
                result = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError) as exc:
            raise RuntimeError(
                f"Local AI provider request failed: {exc}"
            ) from exc

        answer = result.get("response")

        if not isinstance(answer, str):
            raise RuntimeError(
                "Local AI provider returned an invalid response."
            )

        return answer