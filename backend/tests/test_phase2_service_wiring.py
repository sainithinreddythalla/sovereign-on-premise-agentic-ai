"""Tests for Phase 2 and Phase 3 backend service wiring."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from agent.schemas import AuditFinding, SourceReference, VerificationStatus
from backend.database import Base, get_db
from backend.main import app


@pytest.fixture
def client(tmp_path: Path):
    db_path = tmp_path / "test_phase2.db"
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


def test_rag_search_preserves_source_and_page_metadata(client):
    mock_result = {
        "results": [
            {
                "document_id": "doc-123",
                "filename": "policy.pdf",
                "page": 7,
                "text": "Evidence from page seven.",
                "score": 0.95,
            }
        ]
    }

    with patch(
        "backend.routers.contracts._get_rag_search"
    ) as mock_search:
        mock_search.return_value = lambda request: mock_result

        response = client.post(
            "/api/rag/search",
            json={
                "query": "test evidence",
                "document_ids": ["doc-123"],
                "top_k": 5,
            },
        )

    assert response.status_code == 200
    body = response.json()

    assert body["results"][0]["document_id"] == "doc-123"
    assert body["results"][0]["filename"] == "policy.pdf"
    assert body["results"][0]["page"] == 7


def test_ai_metadata_reaches_backend_response(client):
    mock_result = MagicMock()
    mock_result.model = "test-model"
    mock_result.answer = "Generated analysis."
    mock_result.verification_status = "requires_review"
    mock_result.metadata = {
        "generated_analysis": True,
        "evidence_verified": False,
        "verification_owner": "agent",
    }

    with patch("ai.entrypoint.generate") as mock_generate:
        mock_generate.return_value = mock_result

        response = client.post(
            "/api/ai/generate",
            json={
                "task_type": "reasoning",
                "prompt": "Analyze the evidence.",
                "context": [],
            },
        )

    assert response.status_code == 200
    body = response.json()

    assert body["metadata"]["generated_analysis"] is True
    assert body["metadata"]["evidence_verified"] is False
    assert body["metadata"]["verification_owner"] == "agent"
    assert body["verification_status"] == "requires_review"


def test_agent_verified_finding_reaches_task_response(client):
    source = SourceReference(
        document_id="doc-123",
        filename="policy.pdf",
        page=7,
        reference="Evidence from page seven.",
    )

    finding = AuditFinding(
        finding="Requirement is satisfied.",
        source="policy.pdf",
        page=7,
        requirement_evidence="The requirement is explicitly stated.",
        observed_source="policy.pdf",
        observed_page=7,
        observed_evidence="The document confirms compliance.",
        verification_status=VerificationStatus.VERIFIED_WITH_EVIDENCE,
        requires_human_review=False,
        severity="low",
        recommendations="No action required.",
    )

    mock_result = MagicMock()
    mock_result.status = "completed"
    mock_result.answer = "The requirement is satisfied."
    mock_result.verification_status = VerificationStatus.VERIFIED_WITH_EVIDENCE
    mock_result.evidence_coverage = 1.0
    mock_result.requires_human_review = False
    mock_result.sources = [source]
    mock_result.findings = [finding]
    mock_result.report_id = "report-123"

    with patch("backend.routers.tasks.execute_task") as mock_execute:
        mock_execute.return_value = mock_result

        create_response = client.post(
            "/api/tasks",
            json={
                "message": "Verify the requirement.",
                "document_ids": ["doc-123"],
            },
        )

    assert create_response.status_code == 201
    task_id = create_response.json()["task_id"]

    get_response = client.get(f"/api/tasks/{task_id}")

    assert get_response.status_code == 200
    body = get_response.json()

    assert body["answer"] == "The requirement is satisfied."
    assert body["verification_status"] == "verified_with_evidence"
    assert body["evidence_coverage"] == 1.0
    assert body["requires_human_review"] is False
    assert body["report_id"] == "report-123"

    assert body["sources"][0]["document_id"] == "doc-123"
    assert body["sources"][0]["filename"] == "policy.pdf"
    assert body["sources"][0]["page"] == 7

    assert body["findings"][0]["verification_status"] == "verified_with_evidence"
    assert body["findings"][0]["requires_human_review"] is False


def test_requires_human_review_reaches_task_response(client):
    finding = AuditFinding(
        finding="Evidence is insufficient.",
        source="policy.pdf",
        page=7,
        requirement_evidence="Requirement evidence is incomplete.",
        observed_source="policy.pdf",
        observed_page=7,
        observed_evidence="Only partial evidence was found.",
        verification_status=VerificationStatus.REQUIRES_REVIEW,
        requires_human_review=True,
        severity="medium",
        recommendations="Human review required.",
    )

    mock_result = MagicMock()
    mock_result.status = "completed"
    mock_result.answer = "Evidence requires review."
    mock_result.verification_status = VerificationStatus.REQUIRES_REVIEW
    mock_result.evidence_coverage = 0.0
    mock_result.requires_human_review = True
    mock_result.sources = []
    mock_result.findings = [finding]
    mock_result.report_id = "report-review"

    with patch("backend.routers.tasks.execute_task") as mock_execute:
        mock_execute.return_value = mock_result

        create_response = client.post(
            "/api/tasks",
            json={
                "message": "Check evidence.",
                "document_ids": [],
            },
        )

    assert create_response.status_code == 201
    task_id = create_response.json()["task_id"]

    get_response = client.get(f"/api/tasks/{task_id}")

    assert get_response.status_code == 200
    body = get_response.json()

    assert body["verification_status"] == "requires_review"
    assert body["requires_human_review"] is True
    assert body["findings"][0]["verification_status"] == "requires_review"
    assert body["findings"][0]["requires_human_review"] is True


def test_insufficient_evidence_is_not_reported_as_verified(client):
    finding = AuditFinding(
        finding="Evidence is incomplete.",
        source="policy.pdf",
        page=7,
        requirement_evidence="Insufficient evidence.",
        observed_source="policy.pdf",
        observed_page=7,
        observed_evidence="Evidence is missing.",
        verification_status=VerificationStatus.VERIFICATION_INCOMPLETE,
        requires_human_review=True,
        severity="high",
        recommendations="Collect additional evidence.",
    )

    mock_result = MagicMock()
    mock_result.status = "completed"
    mock_result.answer = "Verification is incomplete."
    mock_result.verification_status = VerificationStatus.VERIFICATION_INCOMPLETE
    mock_result.evidence_coverage = 0.0
    mock_result.requires_human_review = True
    mock_result.sources = []
    mock_result.findings = [finding]
    mock_result.report_id = "report-incomplete"

    with patch("backend.routers.tasks.execute_task") as mock_execute:
        mock_execute.return_value = mock_result

        create_response = client.post(
            "/api/tasks",
            json={
                "message": "Verify with insufficient evidence.",
                "document_ids": [],
            },
        )

    assert create_response.status_code == 201
    task_id = create_response.json()["task_id"]

    get_response = client.get(f"/api/tasks/{task_id}")

    assert get_response.status_code == 200
    body = get_response.json()

    assert body["verification_status"] == "verification_incomplete"
    assert body["verification_status"] != "verified_with_evidence"
    assert body["requires_human_review"] is True

    assert body["findings"][0]["verification_status"] == "verification_incomplete"
    assert body["findings"][0]["verification_status"] != "verified_with_evidence"
    assert body["findings"][0]["requires_human_review"] is True