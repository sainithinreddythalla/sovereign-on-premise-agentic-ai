"""API contract endpoints for RAG, AI generation, and report generation."""

from fastapi import APIRouter, HTTPException

from backend.schemas.contracts import (
    AIGenerateRequest,
    AIGenerateResponse,
    RAGSearchRequest,
    RAGSearchResponse,
    ReportGenerateRequest,
    ReportGenerateResponse,
)

router = APIRouter(tags=["contracts"])


@router.post("/rag/search", response_model=RAGSearchResponse)
def rag_search(request: RAGSearchRequest) -> RAGSearchResponse:
    # RAG implementation is owned by the RAG team.
    return RAGSearchResponse(results=[])


@router.post("/ai/generate", response_model=AIGenerateResponse)
def ai_generate(request: AIGenerateRequest) -> AIGenerateResponse:
    # AI provider integration is owned by the AI team.
    raise HTTPException(
        status_code=503,
        detail={
            "code": "AI_SERVICE_UNAVAILABLE",
            "message": "AI service is not currently available.",
        },
    )


@router.post("/reports/generate", response_model=ReportGenerateResponse)
def generate_report(
    request: ReportGenerateRequest,
) -> ReportGenerateResponse:
    # Report generation implementation is not yet available.
    raise HTTPException(
        status_code=503,
        detail={
            "code": "REPORT_SERVICE_UNAVAILABLE",
            "message": "Report generation service is not currently available.",
        },
    )