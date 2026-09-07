"""Tests for required Section 11 API contract endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database import Base, get_db
from backend.main import app


@pytest.fixture
def client(tmp_path):
    """Create an isolated test database with all application tables."""
    db_file = tmp_path / "test_contracts.db"
    test_engine = create_engine(
        f"sqlite:///{db_file}",
        connect_args={"check_same_thread": False},
    )
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine,
    )

    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    test_client = TestClient(app)

    yield test_client

    app.dependency_overrides.clear()
    test_engine.dispose()


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
    assert response.json()["status"] == "queued"


def test_rag_search_contract(client):
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


def test_ai_generate_contract(client):
    response = client.post(
        "/api/ai/generate",
        json={
            "task_type": "reasoning",
            "prompt": "Analyze evidence.",
            "context": [],
        },
    )

    assert response.status_code == 503


def test_report_generate_contract(client):
    response = client.post(
        "/api/reports/generate",
        json={
            "task_id": "task_001",
            "format": "docx",
        },
    )

    assert response.status_code == 503