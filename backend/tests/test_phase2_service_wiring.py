"""Tests for Phase 2 backend service wiring."""

import sys
from types import ModuleType
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)

def test_rag_search_delegates_to_rag_service():
    mock_result = {
        "results": []
    }

    mock_search = MagicMock(return_value=mock_result)

    with patch(
        "backend.routers.contracts._get_rag_search",
        return_value=mock_search,
    ) as mock_get_search:
        response = client.post(
            "/api/rag/search",
            json={
                "query": "test query",
                "document_ids": [],
                "top_k": 5,
            },
        )

    assert response.status_code == 200
    mock_get_search.assert_called_once()
    mock_search.assert_called_once()
def test_ai_generate_delegates_to_ai_service():
    mock_result = MagicMock()
    mock_result.model = "test-model"
    mock_result.answer = "test answer"
    mock_result.verification_status = "requires_review"

    with patch(
        "ai.entrypoint.generate",
        return_value=mock_result,
    ) as mock_generate:
        response = client.post(
            "/api/ai/generate",
            json={
                "task_type": "reasoning",
                "prompt": "test prompt",
                "context": [],
            },
        )

    assert response.status_code == 200
    assert response.json()["model"] == "test-model"
    assert response.json()["answer"] == "test answer"
    mock_generate.assert_called_once()


def test_ai_generate_reports_unavailable_when_provider_missing():
    with patch(
        "ai.entrypoint.generate",
        side_effect=RuntimeError(
            "No local AI provider is configured."
        ),
    ):
        response = client.post(
            "/api/ai/generate",
            json={
                "task_type": "reasoning",
                "prompt": "test prompt",
                "context": [],
            },
        )

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "AI_SERVICE_UNAVAILABLE"


def test_task_creation_delegates_to_agent():
    mock_result = MagicMock()
    mock_result.status = "completed"
    mock_result.answer = "agent answer"
    mock_result.verification_status = "verified"
    mock_result.evidence_coverage = 1.0
    mock_result.requires_human_review = False
    mock_result.report_id = None

    with patch(
        "backend.routers.tasks.execute_task",
        return_value=mock_result,
    ) as mock_execute:
        response = client.post(
            "/api/tasks",
            json={
                "message": "test task",
                "document_ids": [],
            },
        )

    assert response.status_code == 201
    assert response.json()["status"] == "completed"
    mock_execute.assert_called_once()