"""API contract endpoints for RAG, AI generation, and report generation."""

from fastapi import APIRouter

from backend.errors import APIError
from backend.database import SessionLocal
from backend.services.report import generate_report as generate_report_service
from backend.schemas.contracts import (
    AIGenerateRequest,
    AIGenerateResponse,
    RAGSearchRequest,
    RAGSearchResponse,
    ReportGenerateRequest,
    ReportGenerateResponse,
)

router = APIRouter(tags=["contracts"])


def _get_rag_search():
    """Load the RAG service boundary lazily."""
    from rag.src.service import search

    return search


@router.post("/rag/search", response_model=RAGSearchResponse)
def rag_search(request: RAGSearchRequest) -> RAGSearchResponse:
    """Delegate RAG search to the RAG service boundary."""
    try:
        result = _get_rag_search()(request)
        if hasattr(result, "model_dump"):
            result = result.model_dump()
        return RAGSearchResponse.model_validate(result)
    except Exception as exc:
        raise APIError(
            status_code=503,
            code="RAG_SERVICE_UNAVAILABLE",
            message="RAG service is not currently available.",
            details=str(exc),
        ) from exc


@router.post("/ai/generate", response_model=AIGenerateResponse)
def ai_generate(request: AIGenerateRequest) -> AIGenerateResponse:
    """Delegate generation to the AI service boundary."""
    try:
        from ai.entrypoint import generate
        from ai.schemas import GenerationRequest

        ai_request = GenerationRequest(
            prompt=request.prompt,
            task_type=request.task_type,
            context=request.context,
        )

        result = generate(ai_request)

        return AIGenerateResponse(
            model=result.model,
            answer=result.answer,
            verification_status=result.verification_status,
            metadata=result.metadata,
        )
    except RuntimeError as exc:
        raise APIError(
            status_code=503,
            code="AI_SERVICE_UNAVAILABLE",
            message="AI service is not currently available.",
            details=str(exc),
        ) from exc
    except Exception as exc:
        raise APIError(
            status_code=503,
            code="AI_SERVICE_UNAVAILABLE",
            message="AI service failed to generate a response.",
            details=str(exc),
        ) from exc


@router.post(
    "/reports/generate",
    response_model=ReportGenerateResponse,
)
def generate_report(
    request: ReportGenerateRequest,
) -> ReportGenerateResponse:
    """Generate a local DOCX report from persisted task data."""
    db = SessionLocal()

    try:
        report_id, filename = generate_report_service(
            db=db,
            task_id=request.task_id,
            report_format=request.format,
        )

        return ReportGenerateResponse(
            report_id=report_id,
            task_id=request.task_id,
            format=request.format,
            filename=filename,
        )

    except LookupError as exc:
        raise APIError(
            status_code=404,
            code="TASK_NOT_FOUND",
            message=str(exc),
        ) from exc

    except ValueError as exc:
        raise APIError(
            status_code=400,
            code="INVALID_REPORT_FORMAT",
            message=str(exc),
        ) from exc

    except Exception as exc:
        raise APIError(
            status_code=503,
            code="REPORT_SERVICE_UNAVAILABLE",
            message="Report generation service is not currently available.",
            details=str(exc),
        ) from exc

    finally:
        db.close()