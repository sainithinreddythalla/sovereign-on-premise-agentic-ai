"""Contract scaffolding for the shared API payloads in PROJECT_SPEC.md.

The runnable tests validate payload examples against the existing agent schemas.
The endpoint tests remain explicitly skipped until the corresponding backend,
RAG, AI, document, and report modules expose local integration clients.
"""

import pytest

from agent.schemas import (
    AIGenerateRequest,
    AIGenerateResponse,
    AuditFinding,
    RAGSearchRequest,
    RAGSearchResponse,
    RAGSearchResult,
    ReportGenerateRequest,
    ReportGenerateResponse,
    SourceReference,
    TaskCreateRequest,
    TaskCreateResponse,
    TaskStatus,
    TaskStatusResponse,
    VerificationStatus,
)


DOCUMENT_ID = "doc_001"
TASK_ID = "task_001"
REPORT_ID = "report_001"


def test_task_creation_contract_uses_shared_agent_models():
    """Validate the Section 11.3 task request and response examples."""
    request = TaskCreateRequest(
        message="Audit this equipment against the safety standard.",
        document_ids=[DOCUMENT_ID, "doc_002"],
    )
    response = TaskCreateResponse(task_id=TASK_ID)

    assert request.model_dump() == {
        "message": "Audit this equipment against the safety standard.",
        "document_ids": [DOCUMENT_ID, "doc_002"],
    }
    assert response.model_dump() == {"task_id": TASK_ID, "status": TaskStatus.QUEUED}


def test_task_status_contract_supports_nested_evidence_and_findings():
    """Validate the Section 11.4 status payload and nested evidence models."""
    response = TaskStatusResponse(
        task_id=TASK_ID,
        status=TaskStatus.COMPLETED,
        answer="Three potential deviations were identified.",
        verification_status=VerificationStatus.VERIFIED_WITH_EVIDENCE,
        evidence_coverage=0.92,
        requires_human_review=True,
        sources=[
            SourceReference(
                document_id=DOCUMENT_ID,
                filename="Safety_Manual.pdf",
                page=17,
                reference="Relevant safety requirement...",
            )
        ],
        findings=[],
        report_id=REPORT_ID,
    )

    assert response.model_dump() == {
        "task_id": TASK_ID,
        "status": TaskStatus.COMPLETED,
        "answer": "Three potential deviations were identified.",
        "verification_status": VerificationStatus.VERIFIED_WITH_EVIDENCE,
        "evidence_coverage": 0.92,
        "requires_human_review": True,
        "sources": [
            {
                "document_id": DOCUMENT_ID,
                "filename": "Safety_Manual.pdf",
                "page": 17,
                "reference": "Relevant safety requirement...",
            }
        ],
        "findings": [],
        "report_id": REPORT_ID,
    }


def test_rag_search_contract_uses_shared_agent_models():
    """Validate the Section 11.5 request and response payload examples."""
    request = RAGSearchRequest(
        query="Applicable safety requirements",
        document_ids=[DOCUMENT_ID],
        top_k=5,
    )
    response = RAGSearchResponse(
        results=[
            RAGSearchResult(
                document_id=DOCUMENT_ID,
                filename="Safety_Manual.pdf",
                page=17,
                text="Relevant document content...",
                score=0.91,
            )
        ]
    )

    assert request.model_dump() == {
        "query": "Applicable safety requirements",
        "document_ids": [DOCUMENT_ID],
        "top_k": 5,
    }
    assert response.results[0].model_dump() == {
        "document_id": DOCUMENT_ID,
        "filename": "Safety_Manual.pdf",
        "page": 17,
        "text": "Relevant document content...",
        "score": 0.91,
    }


def test_ai_generation_contract_uses_shared_agent_models():
    """Validate the Section 11.6 request and response payload examples."""
    request = AIGenerateRequest(
        task_type="reasoning",
        prompt="Analyze the retrieved evidence.",
        context=[],
    )
    response = AIGenerateResponse(
        model="selected-model",
        answer="...",
        verification_status="requires_review",
    )

    assert request.model_dump() == {
        "task_type": "reasoning",
        "prompt": "Analyze the retrieved evidence.",
        "context": [],
    }
    assert response.model_dump() == {
        "model": "selected-model",
        "answer": "...",
        "verification_status": "requires_review",
    }


def test_report_generation_contract_uses_shared_agent_models():
    """Validate the Section 11.7 request and response payload examples."""
    request = ReportGenerateRequest(task_id=TASK_ID, format="docx")
    response = ReportGenerateResponse(
        report_id=REPORT_ID,
        status="generated",
        filename="industrial_audit_report.docx",
    )

    assert request.model_dump() == {"task_id": TASK_ID, "format": "docx"}
    assert response.model_dump() == {
        "report_id": REPORT_ID,
        "status": "generated",
        "filename": "industrial_audit_report.docx",
    }


@pytest.mark.skip(reason="Pending backend document-upload integration")
def test_document_upload_endpoint_contract_pending():
    """Future test: POST /api/documents/upload accepts multipart file data.

    Once the backend exposes a local test client, verify the response contains
    document_id, filename, and the initial processing status from Section 11.1.
    """


@pytest.mark.skip(reason="Pending backend document-status integration")
def test_document_status_endpoint_contract_pending():
    """Future test: GET /api/documents/{document_id} returns document status.

    Once document storage is integrated, verify the response contains
    document_id, filename, and one of the statuses defined in Section 11.2.
    """


@pytest.mark.skip(reason="Pending backend task API integration")
def test_create_task_endpoint_contract_pending():
    """Future test: POST /api/tasks validates and creates a task locally."""


@pytest.mark.skip(reason="Pending backend task API integration")
def test_task_status_endpoint_contract_pending():
    """Future test: GET /api/tasks/{task_id} returns the shared task contract."""


@pytest.mark.skip(reason="Pending RAG API integration")
def test_rag_search_endpoint_contract_pending():
    """Future test: POST /api/rag/search returns source-preserving results."""


@pytest.mark.skip(reason="Pending AI module integration")
def test_ai_generation_endpoint_contract_pending():
    """Future test: POST /api/ai/generate uses a local model abstraction."""


@pytest.mark.skip(reason="Pending report-generation integration")
def test_report_generation_endpoint_contract_pending():
    """Future test: POST /api/reports/generate returns a generated report ID."""