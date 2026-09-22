"""Tests for required API contract endpoints."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database import Base, get_db
from backend.main import app


@pytest.fixture
def client(tmp_path: Path):
    db_path = tmp_path / "test.db"
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_create_and_get_task(client):
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
    assert response.json()["status"] in {
        "queued",
        "planning",
        "retrieving",
        "analyzing",
        "verifying",
        "generating",
        "completed",
        "failed",
    }


def test_rag_search_contract(client):
    response = client.post(
        "/api/rag/search",
        json={
            "query": "Applicable safety requirements",
            "document_ids": ["doc_001"],
            "top_k": 5,
        },
    )

    assert response.status_code in {200, 503}


def test_ai_generate_contract(client):
    response = client.post(
        "/api/ai/generate",
        json={
            "task_type": "reasoning",
            "prompt": "Summarize the requirements.",
            "context": [],
        },
    )

    assert response.status_code in {200, 503}


def test_report_generate_contract(client):
    response = client.post(
        "/api/reports/generate",
        json={
            "task_id": "task_test123",
            "format": "docx",
        },
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "TASK_NOT_FOUND"