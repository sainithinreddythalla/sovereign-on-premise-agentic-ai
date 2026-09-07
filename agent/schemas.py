"""
agent/schemas.py
Module 3: Agent + Industrial Workflow Data Schemas & Contracts.

Strictly grounded in SIH26117 PROJECT_SPEC.md:
- Section 7: Primary Demonstration Workflow & Expected Outputs
- Section 11: API Contracts (11.3, 11.4, 11.5, 11.6, 11.7)
- Section 14: Agent Flow
- Section 15: Verification Layer
- Section 16: Evidence and Grounding
- Section 17: Deliverable Generation
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ============================================================================
# PART 1: ENUM DEFINITIONS
# ============================================================================

class TaskStatus(str, Enum):
    """
    Task lifecycle statuses explicitly enumerated in Section 11.4 of PROJECT_SPEC.md:
    queued, planning, retrieving, analyzing, verifying, generating, completed, failed.
    """
    QUEUED = "queued"
    PLANNING = "planning"
    RETRIEVING = "retrieving"
    ANALYZING = "analyzing"
    VERIFYING = "verifying"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class VerificationStatus(str, Enum):
    """
    Verification status values derived from PROJECT_SPEC.md:
    - Section 11.4 API Contract: "verified_with_evidence"
    - Section 11.6 API Contract: "requires_review"
    - Section 15 Prose: "Requires human review" or "Verification incomplete"
    - Section 16 Example: "Requires review"

    Standardized using snake_case as required by Section 11 REST API contracts.
    """
    VERIFIED_WITH_EVIDENCE = "verified_with_evidence"
    REQUIRES_REVIEW = "requires_review"
    VERIFICATION_INCOMPLETE = "verification_incomplete"


class AgentActionType(str, Enum):
    """
    Controlled actions permitted in Section 14 (Agent Flow) of PROJECT_SPEC.md:
    - RAG Search
    - Vision Analysis
    - Document Reading
    - Calculation Tool
    - AI Model
    - Report Generation
    """
    RAG_SEARCH = "rag_search"
    VISION_ANALYSIS = "vision_analysis"
    DOCUMENT_READING = "document_reading"
    CALCULATION_TOOL = "calculation_tool"
    AI_MODEL = "ai_model"
    REPORT_GENERATION = "report_generation"


# ============================================================================
# PART 2: EXTERNAL API CONTRACT SCHEMAS (Section 11)
# These match the exact JSON payloads specified in PROJECT_SPEC.md.
# ============================================================================

# --- 11.3 Create Task ---
class TaskCreateRequest(BaseModel):
    """
    Request body contract for POST /api/tasks (Section 11.3).
    """
    message: str = Field(..., description="User prompt or task instruction")
    document_ids: List[str] = Field(..., description="List of uploaded document IDs to analyze")


class TaskCreateResponse(BaseModel):
    """
    Response body contract for POST /api/tasks (Section 11.3).
    """
    task_id: str = Field(..., description="Unique task identifier")
    status: TaskStatus = Field(default=TaskStatus.QUEUED, description="Initial task status (queued)")


# --- 11.4 Sources & Citations ---
class SourceReference(BaseModel):
    """
    Source reference item inside 'sources' list of Section 11.4 (GET /api/tasks/{task_id}).
    Also aligns with Section 16 (Evidence and Grounding).
    """
    document_id: str = Field(..., description="Identifier of the source document")
    filename: str = Field(..., description="Original filename of the source document")
    page: Optional[int] = Field(None, description="Page number where available (None if unpaged/scanned/unavailable)")
    reference: str = Field(..., description="Extracted requirement or reference text from the document")


# --- 11.4 Findings (Derived from Section 7, 15, and 16) ---
class AuditFinding(BaseModel):
    """
    Industrial Audit Finding schema derived from Section 16 (Example Finding),
    Section 7 (Expected Output), and Section 15 (Verification Layer).

    Note on Ambiguity:
    - In Section 11.4, 'findings: []' is an empty array in the sample JSON.
    - The explicit structure is detailed in Section 16 text example and Section 7 output list.
    - 'severity': Section 7 mentions 'Severity/status where applicable', but
      [SPEC DOES NOT DEFINE THIS] with a fixed enum (e.g. low/medium/high/critical).
      Therefore, it is kept as Optional[str] with no default value.
    """
    finding: str = Field(..., description="Title/summary of the potential deviation or safety issue")
    source: str = Field(..., description="Standard document filename or document_id defining the requirement")
    page: Optional[int] = Field(None, description="Page number in the standard document where available")
    requirement_evidence: str = Field(..., description="Text of the applicable requirement from the standard")
    observed_source: str = Field(..., description="Inspection report, P&ID, or equipment document filename/id")
    observed_page: Optional[int] = Field(None, description="Page number in the observed document where available")
    observed_evidence: str = Field(..., description="Observed condition or deviation text/data")
    verification_status: VerificationStatus = Field(
        default=VerificationStatus.REQUIRES_REVIEW,
        description="Verification state of this specific finding"
    )
    requires_human_review: bool = Field(
        default=True,
        description="Whether this finding requires human engineer review (default True per Section 7 & 15)"
    )
    severity: Optional[str] = Field(
        default=None,
        description="Severity level if applicable (SPEC DOES NOT DEFINE fixed enum values)"
    )
    recommendations: Optional[str] = Field(
        default=None,
        description="Corrective recommendations for this finding (Section 7)"
    )


# --- 11.4 Get Task Status ---
class TaskStatusResponse(BaseModel):
    """
    Response body contract for GET /api/tasks/{task_id} (Section 11.4).
    """
    task_id: str = Field(..., description="Unique task identifier")
    status: TaskStatus = Field(..., description="Current lifecycle status of the task")
    answer: Optional[str] = Field(None, description="Summary answer text (populated upon completion)")
    verification_status: Optional[VerificationStatus] = Field(None, description="Overall verification outcome")
    evidence_coverage: Optional[float] = Field(None, description="Evidence grounding coverage score (0.0 to 1.0)")
    requires_human_review: Optional[bool] = Field(None, description="Flag indicating human engineering review required")
    sources: List[SourceReference] = Field(default_factory=list, description="Referenced source documents and excerpts")
    findings: List[AuditFinding] = Field(default_factory=list, description="List of generated industrial audit findings")
    report_id: Optional[str] = Field(None, description="ID of generated report deliverable if available")


# ============================================================================
# PART 3: EXTERNAL MODULE COORDINATION SCHEMAS (Section 11.5, 11.6, 11.7)
# These match the request/response contracts for interacting with other modules.
# ============================================================================

# --- 11.5 RAG Search Contract ---
class RAGSearchRequest(BaseModel):
    """Request body contract for POST /api/rag/search (Section 11.5)."""
    query: str = Field(..., description="Search query string")
    document_ids: List[str] = Field(..., description="Target document IDs to search within")
    top_k: int = Field(default=5, description="Maximum number of relevant chunks to retrieve")


class RAGSearchResult(BaseModel):
    """Individual search result item in POST /api/rag/search response (Section 11.5)."""
    document_id: str = Field(..., description="Document identifier")
    filename: str = Field(..., description="Filename of the source document")
    page: Optional[int] = Field(None, description="Page number where available")
    text: str = Field(..., description="Extracted chunk text")
    score: float = Field(..., description="Relevance score")


class RAGSearchResponse(BaseModel):
    """Response body contract for POST /api/rag/search (Section 11.5)."""
    results: List[RAGSearchResult] = Field(default_factory=list, description="List of retrieved chunks")


# --- 11.6 AI Generation Contract ---
class AIGenerateRequest(BaseModel):
    """Request body contract for POST /api/ai/generate (Section 11.6)."""
    task_type: str = Field(default="reasoning", description="Type of task (e.g. reasoning, analysis)")
    prompt: str = Field(..., description="Prompt instructions for the model")
    context: List[Any] = Field(default_factory=list, description="Retrieved evidence chunks or context items")


class AIGenerateResponse(BaseModel):
    """Response body contract for POST /api/ai/generate (Section 11.6)."""
    model: str = Field(..., description="Name/identifier of the model selected by the model router")
    answer: str = Field(..., description="Generated text response from the model")
    verification_status: Optional[str] = Field(None, description="Verification tag returned by model layer")


# --- 11.7 Report Generation Contract ---
class ReportGenerateRequest(BaseModel):
    """Request body contract for POST /api/reports/generate (Section 11.7)."""
    task_id: str = Field(..., description="Task ID containing findings to compile into report")
    format: str = Field(default="docx", description="Deliverable format (Section 11.7 specifies docx)")


class ReportGenerateResponse(BaseModel):
    """Response body contract for POST /api/reports/generate (Section 11.7)."""
    report_id: str = Field(..., description="Identifier of the generated deliverable")
    status: str = Field(default="generated", description="Status of report generation")
    filename: str = Field(..., description="Generated file name (e.g. industrial_audit_report.docx)")


# ============================================================================
# PART 4: INTERNAL AGENT WORKFLOW & VERIFICATION SCHEMAS (Section 14 & 15)
# [SPEC DOES NOT DEFINE THESE EXTERNALLY - Internal to M3 Agent Engine]
# ============================================================================

class PlanStep(BaseModel):
    """
    Internal representation of a single planned action step (Section 14).
    [SPEC DOES NOT DEFINE THIS AS AN API CONTRACT - Internal to M3]
    """
    step_number: int = Field(..., description="Sequential step index (1-based)")
    description: str = Field(..., description="Human-readable description of what this step accomplishes")
    action: AgentActionType = Field(..., description="The controlled action/tool to be executed")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Input parameters passed to the tool")
    completed: bool = Field(default=False, description="Whether this step has finished executing")
    result: Optional[Any] = Field(None, description="Output returned by the tool execution")


class TaskPlan(BaseModel):
    """
    Internal representation of the overall plan created during the 'planning' status (Section 14).
    [SPEC DOES NOT DEFINE THIS AS AN API CONTRACT - Internal to M3]
    """
    task_id: str = Field(..., description="Associated task identifier")
    goal: str = Field(..., description="High-level goal parsed from user message")
    steps: List[PlanStep] = Field(default_factory=list, description="Ordered sequence of execution steps")


class VerificationReport(BaseModel):
    """
    Internal representation of the verification check results (Section 15).
    Calculates grounding metrics, citation existence, and uncertainty flags.
    [SPEC DOES NOT DEFINE THIS AS AN API CONTRACT - Internal to M3]
    """
    task_id: str = Field(..., description="Associated task identifier")
    total_findings: int = Field(default=0, description="Total count of candidate findings evaluated")
    verified_findings_count: int = Field(default=0, description="Count of findings successfully supported by evidence")
    evidence_coverage: float = Field(default=0.0, description="Ratio of verified claims with source backing (0.0 to 1.0)")
    requires_human_review: bool = Field(default=True, description="Whether human review is required")
    verification_status: VerificationStatus = Field(
        default=VerificationStatus.REQUIRES_REVIEW,
        description="Final aggregated verification status"
    )
    notes: List[str] = Field(default_factory=list, description="Detailed diagnostic notes or missing evidence warnings")
