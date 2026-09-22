"""Pydantic schemas for the required Section 11 API contracts."""

from typing import Any, Optional

from pydantic import BaseModel, Field


class TaskCreateRequest(BaseModel):
    message: str
    document_ids: list[str] = Field(default_factory=list)


class TaskCreateResponse(BaseModel):
    task_id: str
    status: str


class SourceReference(BaseModel):
    document_id: str
    filename: str
    page: Optional[int] = None
    reference: str


class AuditFinding(BaseModel):
    finding: str
    source: str
    page: Optional[int] = None
    requirement_evidence: str
    observed_source: str
    observed_page: Optional[int] = None
    observed_evidence: str
    verification_status: str
    requires_human_review: bool
    severity: Optional[str] = None
    recommendations: Optional[list[str]] = None


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    answer: Optional[str] = None
    verification_status: Optional[str] = None
    evidence_coverage: Optional[float] = None
    requires_human_review: Optional[bool] = None
    sources: list[SourceReference] = Field(default_factory=list)
    findings: list[AuditFinding] = Field(default_factory=list)
    report_id: Optional[str] = None


class RAGSearchRequest(BaseModel):
    query: str
    document_ids: list[str] = Field(default_factory=list)
    top_k: int = Field(default=5, ge=1)


class RAGSearchResult(BaseModel):
    document_id: str
    filename: str
    page: Optional[int] = None
    text: str
    score: float


class RAGSearchResponse(BaseModel):
    results: list[RAGSearchResult] = Field(default_factory=list)


class AIGenerateRequest(BaseModel):
    task_type: str = "reasoning"
    prompt: str
    context: list[Any] = Field(default_factory=list)


class AIGenerateResponse(BaseModel):
    model: str
    answer: str
    verification_status: str = "requires_review"
    metadata: dict[str, Any] = Field(default_factory=dict)


class ReportGenerateRequest(BaseModel):
    task_id: str
    format: str = "docx"


class ReportGenerateResponse(BaseModel):
    report_id: str
    status: str = "generated"
    filename: str