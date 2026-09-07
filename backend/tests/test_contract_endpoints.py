"""Tests for required Section 11 API contract endpoints."""

from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_create_and_get_task():
    response = client.post(
        "/api/tasks",
        json={
            "message": "Audit equipment.",
            "document_ids": ["doc_001"],
        },
    )

    assert response.status_code == 201

    task_id = response.json()["task_id"]

    response = client.get(f"/api/tasks/{task_id}")

    assert response.status_code == 200
    assert response.json()["task_id"] == task_id
    assert response.json()["status"] == "queued"


def test_rag_search_contract():
    response = client.post(
        "/api/rag/search",
        json={
            "query": "Applicable safety requirements",
            "document_ids": ["doc_001"],
            "top_k": 5,
        },
    )

    assert response.status_code == 200
    assert isinstance(response.json()["results"], list)


def test_ai_generate_contract():
    response = client.post(
        "/api/ai/generate",
        json={
            "task_type": "reasoning",
            "prompt": "Analyze evidence.",
            "context": [],
        },
    )

    assert response.status_code == 503


def test_report_generate_contract():
    response = client.post(
        "/api/reports/generate",
        json={
            "task_id": "task_001",
            "format": "docx",
        },
    )

    assert response.status_code == 503