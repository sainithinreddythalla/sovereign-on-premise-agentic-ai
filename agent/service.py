"""
agent/service.py
Module 3: Agent + Industrial Workflow Service Boundary.

Phase 2 Agent Service Integration strictly aligned with SIH26117 PROJECT_SPEC.md:
- Section 7: Primary Demonstration Workflow & Expected Outputs
- Section 10: Development and Integration Principle (Modular callable service boundary)
- Section 11: API Contracts (TaskStatusResponse, RAG, AI, Report schemas)
- Section 14: Agent Flow (Task Understanding -> Planning -> Execution -> Verification -> Deliverable)
- Section 15: Verification Layer (Evidence checking, coverage, human review flag)
- Section 16: Evidence and Grounding (Traceable findings with requirement & observed evidence)
- Section 17: Deliverable Generation (Report compilation trigger)
"""

from typing import Any, Callable, Dict, List, Optional, Protocol, Union
import uuid

from .schemas import (
    AgentActionType,
    AIGenerateRequest,
    AIGenerateResponse,
    AuditFinding,
    PlanStep,
    RAGSearchRequest,
    RAGSearchResponse,
    RAGSearchResult,
    ReportGenerateRequest,
    ReportGenerateResponse,
    SourceReference,
    TaskPlan,
    TaskStatus,
    TaskStatusResponse,
    VerificationReport,
    VerificationStatus,
)


# ============================================================================
# PART 1: PROTOCOLS / INTERFACES FOR INJECTABLE DEPENDENCIES
# ============================================================================

class RAGServiceProtocol(Protocol):
    """Protocol for injectable RAG search dependency."""
    def search(self, request: RAGSearchRequest) -> Union[RAGSearchResponse, Dict[str, Any]]:
        ...


class AIServiceProtocol(Protocol):
    """Protocol for injectable AI model reasoning dependency."""
    def generate(self, request: AIGenerateRequest) -> Union[AIGenerateResponse, Dict[str, Any]]:
        ...


class ReportServiceProtocol(Protocol):
    """Protocol for injectable deliverable report generation dependency."""
    def generate(self, request: ReportGenerateRequest) -> Union[ReportGenerateResponse, Dict[str, Any]]:
        ...


class VerifierProtocol(Protocol):
    """Protocol for injectable verification engine dependency."""
    def verify(
        self,
        task_id: str,
        findings: List[AuditFinding],
        sources: List[SourceReference],
    ) -> Union[VerificationReport, Dict[str, Any]]:
        ...


# ============================================================================
# PART 2: DEFAULT IN-MEMORY / STUB IMPLEMENTATIONS (No external services needed)
# ============================================================================

class DefaultRAGClient:
    """
    Default in-memory RAG client for standalone execution and unit tests.
    Does not require vector databases, external APIs, or network access.
    """
    def search(self, request: RAGSearchRequest) -> RAGSearchResponse:
        results: List[RAGSearchResult] = []
        for i, doc_id in enumerate(request.document_ids[: request.top_k]):
            results.append(
                RAGSearchResult(
                    document_id=doc_id,
                    filename=f"{doc_id}.pdf" if not doc_id.endswith((".pdf", ".docx", ".txt")) else doc_id,
                    page=i + 1,
                    text=f"Standard requirement excerpt from {doc_id} addressing: '{request.query}'",
                    score=round(max(0.5, 0.95 - (i * 0.05)), 2),
                )
            )
        return RAGSearchResponse(results=results)


class DefaultAIClient:
    """
    Default AI client for industrial reasoning tasks.
    Does not require local GPU, Ollama, or remote model endpoints.
    """
    def generate(self, request: AIGenerateRequest) -> AIGenerateResponse:
        context_count = len(request.context)
        return AIGenerateResponse(
            model="default-industrial-reasoner",
            answer=(
                f"Industrial audit analysis complete for task: '{request.prompt}'. "
                f"Evaluated {context_count} evidence items across provided documents."
            ),
            verification_status=VerificationStatus.REQUIRES_REVIEW.value,
        )


class DefaultReportClient:
    """
    Default report deliverable generation client.
    Does not require filesystem or document compiler services.
    """
    def generate(self, request: ReportGenerateRequest) -> ReportGenerateResponse:
        clean_task_id = request.task_id or "task_default"
        return ReportGenerateResponse(
            report_id=f"report_{clean_task_id}",
            status="generated",
            filename=f"industrial_audit_report_{clean_task_id}.{request.format}",
        )


class DefaultVerifier:
    """
    Default verification engine implementing Section 15 of PROJECT_SPEC.md.
    Evaluates grounding, evidence presence, and human review requirements.
    """
    def verify(
        self,
        task_id: str,
        findings: List[AuditFinding],
        sources: List[SourceReference],
    ) -> VerificationReport:
        total = len(findings)
        if total == 0:
            return VerificationReport(
                task_id=task_id,
                total_findings=0,
                verified_findings_count=0,
                evidence_coverage=1.0 if sources else 0.0,
                requires_human_review=True,
                verification_status=VerificationStatus.REQUIRES_REVIEW,
                notes=["No candidate audit findings generated for evaluation."],
            )

        known_docs = {s.document_id for s in sources} | {s.filename for s in sources}
        verified_count = 0
        notes: List[str] = []

        for finding in findings:
            has_req = bool(finding.requirement_evidence and finding.requirement_evidence.strip())
            has_obs = bool(finding.observed_evidence and finding.observed_evidence.strip())
            source_grounded = bool(finding.source and (finding.source in known_docs or len(known_docs) == 0))

            if has_req and has_obs and source_grounded:
                verified_count += 1
                finding.verification_status = VerificationStatus.VERIFIED_WITH_EVIDENCE
            else:
                finding.verification_status = VerificationStatus.REQUIRES_REVIEW
                notes.append(f"Finding '{finding.finding}' lacks complete verified evidence grounding.")

        coverage = round(verified_count / total, 2)

        if coverage >= 0.8:
            status = VerificationStatus.VERIFIED_WITH_EVIDENCE
        elif coverage < 0.5:
            status = VerificationStatus.VERIFICATION_INCOMPLETE
        else:
            status = VerificationStatus.REQUIRES_REVIEW

        return VerificationReport(
            task_id=task_id,
            total_findings=total,
            verified_findings_count=verified_count,
            evidence_coverage=coverage,
            requires_human_review=True,  # Industrial audit findings require human review (Section 7 & 15)
            verification_status=status,
            notes=notes,
        )


# ============================================================================
# PART 3: AGENT SERVICE CORE IMPLEMENTATION
# ============================================================================

class AgentService:
    """
    Module 3 Agent Service orchestrator.
    Manages task planning, multi-step execution, controlled tool calling,
    lifecycle progression, verification, and deliverable handoff.
    """

    def __init__(
        self,
        *,
        rag_service: Optional[Any] = None,
        ai_service: Optional[Any] = None,
        report_service: Optional[Any] = None,
        verifier: Optional[Any] = None,
        findings_generator: Optional[Callable[[str, List[SourceReference], AIGenerateResponse], List[AuditFinding]]] = None,
    ):
        self.rag_service = rag_service or DefaultRAGClient()
        self.ai_service = ai_service or DefaultAIClient()
        self.report_service = report_service or DefaultReportClient()
        self.verifier = verifier or DefaultVerifier()
        self.findings_generator = findings_generator

        # State tracking
        self.task_id: Optional[str] = None
        self.current_status: TaskStatus = TaskStatus.QUEUED
        self.status_history: List[TaskStatus] = []
        self.plan: Optional[TaskPlan] = None
        self.verification_report: Optional[VerificationReport] = None
        self.sources: List[SourceReference] = []
        self.findings: List[AuditFinding] = []
        self.last_response: Optional[TaskStatusResponse] = None

    def _transition(
        self,
        status: TaskStatus,
        status_callback: Optional[Callable[[TaskStatus, Optional[TaskPlan]], None]] = None,
    ) -> None:
        """Record lifecycle progression and notify callback if present."""
        self.current_status = status
        self.status_history.append(status)
        if status_callback:
            status_callback(status, self.plan)

    def _create_plan(self, task_id: str, message: str, document_ids: List[str]) -> TaskPlan:
        """
        Create structured TaskPlan using Section 14 Agent Flow:
        1. RAG Search
        2. AI Model Analysis
        3. Verification
        4. Deliverable Report Generation
        """
        doc_str = ", ".join(document_ids) if document_ids else "all available documents"
        steps = [
            PlanStep(
                step_number=1,
                description=f"Retrieve relevant internal standards and inspection excerpts for: {doc_str}",
                action=AgentActionType.RAG_SEARCH,
                parameters={"query": message, "document_ids": document_ids, "top_k": 5},
            ),
            PlanStep(
                step_number=2,
                description="Analyze retrieved documentation and formulate candidate industrial audit findings",
                action=AgentActionType.AI_MODEL,
                parameters={"task_type": "reasoning", "prompt": message},
            ),
            PlanStep(
                step_number=3,
                description="Verify candidate findings against source evidence and calculate coverage",
                action=AgentActionType.DOCUMENT_READING,
                parameters={"task_id": task_id},
            ),
            PlanStep(
                step_number=4,
                description="Compile deliverable audit report",
                action=AgentActionType.REPORT_GENERATION,
                parameters={"task_id": task_id, "format": "docx"},
            ),
        ]
        return TaskPlan(task_id=task_id, goal=message, steps=steps)

    def _call_rag(self, request: RAGSearchRequest) -> RAGSearchResponse:
        """Invoke injectable RAG dependency with schema conversion."""
        if hasattr(self.rag_service, "search"):
            res = self.rag_service.search(request)
        elif callable(self.rag_service):
            res = self.rag_service(request)
        else:
            raise TypeError("rag_service must be callable or have a 'search' method")

        if isinstance(res, RAGSearchResponse):
            return res
        if isinstance(res, dict):
            return RAGSearchResponse(**res)
        raise ValueError(f"Unexpected RAG response type: {type(res)}")

    def _call_ai(self, request: AIGenerateRequest) -> AIGenerateResponse:
        """Invoke injectable AI dependency with schema conversion."""
        if hasattr(self.ai_service, "generate"):
            res = self.ai_service.generate(request)
        elif callable(self.ai_service):
            res = self.ai_service(request)
        else:
            raise TypeError("ai_service must be callable or have a 'generate' method")

        if isinstance(res, AIGenerateResponse):
            return res
        if isinstance(res, dict):
            return AIGenerateResponse(**res)
        raise ValueError(f"Unexpected AI response type: {type(res)}")

    def _call_report(self, request: ReportGenerateRequest) -> ReportGenerateResponse:
        """Invoke injectable report generator dependency with schema conversion."""
        if hasattr(self.report_service, "generate"):
            res = self.report_service.generate(request)
        elif callable(self.report_service):
            res = self.report_service(request)
        else:
            raise TypeError("report_service must be callable or have a 'generate' method")

        if isinstance(res, ReportGenerateResponse):
            return res
        if isinstance(res, dict):
            return ReportGenerateResponse(**res)
        raise ValueError(f"Unexpected Report response type: {type(res)}")

    def _call_verifier(
        self,
        task_id: str,
        findings: List[AuditFinding],
        sources: List[SourceReference],
    ) -> VerificationReport:
        """Invoke injectable verifier dependency with schema conversion."""
        if hasattr(self.verifier, "verify"):
            res = self.verifier.verify(task_id, findings, sources)
        elif callable(self.verifier):
            res = self.verifier(task_id, findings, sources)
        else:
            raise TypeError("verifier must be callable or have a 'verify' method")

        if isinstance(res, VerificationReport):
            return res
        if isinstance(res, dict):
            return VerificationReport(**res)
        raise ValueError(f"Unexpected Verifier response type: {type(res)}")

    def _extract_findings(
        self,
        message: str,
        sources: List[SourceReference],
        ai_response: AIGenerateResponse,
    ) -> List[AuditFinding]:
        """
        Generate candidate AuditFinding items based on retrieved evidence and analysis.
        Follows Section 16 schema format.
        """
        if self.findings_generator:
            return self.findings_generator(message, sources, ai_response)

        if not sources:
            return []

        findings: List[AuditFinding] = []
        for i, source in enumerate(sources):
            findings.append(
                AuditFinding(
                    finding=f"Potential deviation observed in {source.filename or source.document_id}",
                    source=source.filename or source.document_id,
                    page=source.page,
                    requirement_evidence=source.reference,
                    observed_source=source.filename or source.document_id,
                    observed_page=source.page,
                    observed_evidence=f"Observed specification or inspection condition corresponding to '{message}'",
                    verification_status=VerificationStatus.REQUIRES_REVIEW,
                    requires_human_review=True,
                    severity="medium",
                    recommendations="Review against engineering standard and verify on-site installation.",
                )
            )
        return findings

    def execute(
        self,
        message: str,
        document_ids: List[str],
        *,
        task_id: Optional[str] = None,
        status_callback: Optional[Callable[[TaskStatus, Optional[TaskPlan]], None]] = None,
    ) -> TaskStatusResponse:
        """
        Execute full agent task workflow through Section 11.4 TaskStatus lifecycle:
        queued -> planning -> retrieving -> analyzing -> verifying -> generating -> completed (or failed).
        """
        # Validate task input
        if not isinstance(message, str):
            raise TypeError("message must be a string")
        if not isinstance(document_ids, list) or not all(isinstance(d, str) for d in document_ids):
            raise TypeError("document_ids must be a list of strings")

        self.task_id = task_id or f"task_{uuid.uuid4().hex[:8]}"
        self.status_history = []
        self.sources = []
        self.findings = []
        self.verification_report = None

        try:
            # 1. QUEUED
            self._transition(TaskStatus.QUEUED, status_callback)

            # 2. PLANNING
            self._transition(TaskStatus.PLANNING, status_callback)
            self.plan = self._create_plan(self.task_id, message, document_ids)

            # 3. RETRIEVING
            self._transition(TaskStatus.RETRIEVING, status_callback)
            rag_req = RAGSearchRequest(
                query=message,
                document_ids=document_ids,
                top_k=5,
            )
            rag_res = self._call_rag(rag_req)
            self.sources = [
                SourceReference(
                    document_id=r.document_id,
                    filename=r.filename,
                    page=r.page,
                    reference=r.text,
                )
                for r in rag_res.results
            ]
            if len(self.plan.steps) > 0:
                self.plan.steps[0].completed = True
                self.plan.steps[0].result = {"sources_retrieved": len(self.sources)}

            # 4. ANALYZING
            self._transition(TaskStatus.ANALYZING, status_callback)
            context_payload = [
                {"document_id": s.document_id, "filename": s.filename, "page": s.page, "text": s.reference}
                for s in self.sources
            ]
            ai_req = AIGenerateRequest(
                task_type="reasoning",
                prompt=message,
                context=context_payload,
            )
            ai_res = self._call_ai(ai_req)
            self.findings = self._extract_findings(message, self.sources, ai_res)
            if len(self.plan.steps) > 1:
                self.plan.steps[1].completed = True
                self.plan.steps[1].result = {
                    "model": ai_res.model,
                    "findings_generated": len(self.findings),
                }

            # 5. VERIFYING
            self._transition(TaskStatus.VERIFYING, status_callback)
            self.verification_report = self._call_verifier(self.task_id, self.findings, self.sources)
            if len(self.plan.steps) > 2:
                self.plan.steps[2].completed = True
                self.plan.steps[2].result = {
                    "coverage": self.verification_report.evidence_coverage,
                    "verification_status": self.verification_report.verification_status.value,
                }

            # 6. GENERATING
            self._transition(TaskStatus.GENERATING, status_callback)
            report_req = ReportGenerateRequest(task_id=self.task_id, format="docx")
            report_res = self._call_report(report_req)
            if len(self.plan.steps) > 3:
                self.plan.steps[3].completed = True
                self.plan.steps[3].result = {
                    "report_id": report_res.report_id,
                    "filename": report_res.filename,
                }

            # 7. COMPLETED
            self._transition(TaskStatus.COMPLETED, status_callback)
            response = TaskStatusResponse(
                task_id=self.task_id,
                status=TaskStatus.COMPLETED,
                answer=ai_res.answer,
                verification_status=self.verification_report.verification_status,
                evidence_coverage=self.verification_report.evidence_coverage,
                requires_human_review=self.verification_report.requires_human_review,
                sources=self.sources,
                findings=self.findings,
                report_id=report_res.report_id,
            )
            self.last_response = response
            return response

        except Exception as e:
            self._transition(TaskStatus.FAILED, status_callback)
            failed_response = TaskStatusResponse(
                task_id=self.task_id,
                status=TaskStatus.FAILED,
                answer=f"Task execution failed: {str(e)}",
                verification_status=VerificationStatus.REQUIRES_REVIEW,
                evidence_coverage=0.0,
                requires_human_review=True,
                sources=self.sources,
                findings=self.findings,
                report_id=None,
            )
            self.last_response = failed_response
            return failed_response


# ============================================================================
# PART 4: PUBLIC CALLABLE SERVICE BOUNDARY
# ============================================================================

def execute_task(
    message: str,
    document_ids: List[str],
    *,
    task_id: Optional[str] = None,
    rag_service: Optional[Any] = None,
    ai_service: Optional[Any] = None,
    report_service: Optional[Any] = None,
    verifier: Optional[Any] = None,
    findings_generator: Optional[Callable[[str, List[SourceReference], AIGenerateResponse], List[AuditFinding]]] = None,
    status_callback: Optional[Callable[[TaskStatus, Optional[TaskPlan]], None]] = None,
) -> TaskStatusResponse:
    """
    Clean callable service boundary for Phase 2 Agent Service Integration.

    Backend usage:
        from agent.service import execute_task

        response = execute_task(
            message="Audit this equipment against the safety standard.",
            document_ids=["doc_001", "doc_002"]
        )

    Parameters:
        message (str): User instruction or task prompt.
        document_ids (List[str]): List of document IDs uploaded for analysis.
        task_id (Optional[str]): Optional custom task ID. If not provided, a unique ID is generated.
        rag_service (Optional[Any]): Injectable/mockable RAG search client or callable.
        ai_service (Optional[Any]): Injectable/mockable AI reasoning client or callable.
        report_service (Optional[Any]): Injectable/mockable report generator client or callable.
        verifier (Optional[Any]): Injectable/mockable verification engine client or callable.
        findings_generator (Optional[Callable]): Optional custom generator for AuditFinding items.
        status_callback (Optional[Callable]): Hook called whenever TaskStatus transitions.

    Returns:
        TaskStatusResponse: Section 11.4 contract response object containing task status,
                            summary answer, verification metrics, sources, findings, and report_id.
    """
    service = AgentService(
        rag_service=rag_service,
        ai_service=ai_service,
        report_service=report_service,
        verifier=verifier,
        findings_generator=findings_generator,
    )
    return service.execute(
        message=message,
        document_ids=document_ids,
        task_id=task_id,
        status_callback=status_callback,
    )
