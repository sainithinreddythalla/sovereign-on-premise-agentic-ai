"""
agent/tests/test_service.py
Focused unit tests for Phase 2 Agent Service Integration.

Tests cover:
1. Task input (valid/invalid parameters, custom task ID, empty docs)
2. Plan creation (TaskPlan structure, step actions, completed states)
3. Lifecycle progression (QUEUED -> PLANNING -> RETRIEVING -> ANALYZING -> VERIFYING -> GENERATING -> COMPLETED, failure)
4. Injectable dependencies (RAG, AI, Report, Verifier, callables/protocols)
5. Verification and findings representation (AuditFinding, VerificationReport, evidence coverage, human review)

These tests are 100% self-contained: no GPU, Ollama, external APIs, or vector stores required.
"""

from typing import Any, Dict, List
import pytest

from agent.schemas import (
    AgentActionType,
    AIGenerateRequest,
    AIGenerateResponse,
    AuditFinding,
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
from agent.service import (
    AgentService,
    DefaultAIClient,
    DefaultRAGClient,
    DefaultReportClient,
    DefaultVerifier,
    execute_task,
)


# ============================================================================
# 1. TASK INPUT TESTS
# ============================================================================

class TestTaskInput:
    """Tests covering task input handling and response generation."""

    def test_task_input_success_default(self):
        message = "Audit heat exchanger E-101 against API 660 standard."
        document_ids = ["doc_api_660", "doc_inspection_e101"]

        response = execute_task(message=message, document_ids=document_ids)

        assert isinstance(response, TaskStatusResponse)
        assert response.task_id.startswith("task_")
        assert response.status == TaskStatus.COMPLETED
        assert response.answer is not None
        assert len(response.sources) == 2
        assert len(response.findings) == 2
        assert response.report_id is not None
        assert response.requires_human_review is True

    def test_task_input_custom_task_id(self):
        custom_id = "task_custom_audit_999"
        response = execute_task(
            message="Check pressure vessel safety compliance",
            document_ids=["doc_asme_sec_viii"],
            task_id=custom_id,
        )

        assert response.task_id == custom_id
        assert response.report_id == f"report_{custom_id}"

    def test_task_input_empty_document_ids(self):
        response = execute_task(
            message="General safety query without documents",
            document_ids=[],
        )

        assert response.status == TaskStatus.COMPLETED
        assert len(response.sources) == 0
        assert len(response.findings) == 0

    def test_task_input_invalid_message_type(self):
        with pytest.raises(TypeError, match="message must be a string"):
            execute_task(message=12345, document_ids=["doc_1"])  # type: ignore

    def test_task_input_invalid_document_ids_type(self):
        with pytest.raises(TypeError, match="document_ids must be a list of strings"):
            execute_task(message="Valid query", document_ids="not_a_list")  # type: ignore

        with pytest.raises(TypeError, match="document_ids must be a list of strings"):
            execute_task(message="Valid query", document_ids=["doc_1", 123])  # type: ignore


# ============================================================================
# 2. PLAN CREATION TESTS
# ============================================================================

class TestPlanCreation:
    """Tests covering TaskPlan representation and PlanStep execution tracking."""

    def test_task_plan_creation_structure(self):
        service = AgentService()
        message = "Inspect pump P-201 alignment against API 610"
        doc_ids = ["doc_api610", "doc_p201_report"]

        service.execute(message=message, document_ids=doc_ids)

        plan = service.plan
        assert isinstance(plan, TaskPlan)
        assert plan.task_id == service.task_id
        assert plan.goal == message
        assert len(plan.steps) == 4

    def test_task_plan_step_actions(self):
        service = AgentService()
        service.execute(
            message="Check flange ratings against ASME B16.5",
            document_ids=["doc_asme_b16_5"],
        )

        plan = service.plan
        expected_actions = [
            AgentActionType.RAG_SEARCH,
            AgentActionType.AI_MODEL,
            AgentActionType.DOCUMENT_READING,
            AgentActionType.REPORT_GENERATION,
        ]

        assert [step.action for step in plan.steps] == expected_actions
        assert [step.step_number for step in plan.steps] == [1, 2, 3, 4]

    def test_task_plan_steps_completion(self):
        service = AgentService()
        service.execute(
            message="Perform boiler inspection review",
            document_ids=["doc_boiler_01"],
        )

        for step in service.plan.steps:
            assert step.completed is True
            assert step.result is not None


# ============================================================================
# 3. LIFECYCLE PROGRESSION TESTS
# ============================================================================

class TestLifecycleProgression:
    """Tests covering TaskStatus lifecycle progression."""

    def test_lifecycle_progression_full_sequence(self):
        service = AgentService()
        observed_statuses: List[TaskStatus] = []

        def callback(status: TaskStatus, plan: Any):
            observed_statuses.append(status)

        response = service.execute(
            message="Audit pipeline thickness against ASME B31.3",
            document_ids=["doc_pipeline_b31_3"],
            status_callback=callback,
        )

        expected_sequence = [
            TaskStatus.QUEUED,
            TaskStatus.PLANNING,
            TaskStatus.RETRIEVING,
            TaskStatus.ANALYZING,
            TaskStatus.VERIFYING,
            TaskStatus.GENERATING,
            TaskStatus.COMPLETED,
        ]

        assert service.status_history == expected_sequence
        assert observed_statuses == expected_sequence
        assert response.status == TaskStatus.COMPLETED

    def test_lifecycle_failure_progression(self):
        class FailingRAGClient:
            def search(self, request: RAGSearchRequest):
                raise RuntimeError("Simulated retrieval failure")

        service = AgentService(rag_service=FailingRAGClient())
        observed_statuses: List[TaskStatus] = []

        def callback(status: TaskStatus, plan: Any):
            observed_statuses.append(status)

        response = service.execute(
            message="Audit tank T-101",
            document_ids=["doc_tank_101"],
            status_callback=callback,
        )

        assert response.status == TaskStatus.FAILED
        assert "Simulated retrieval failure" in (response.answer or "")
        assert TaskStatus.FAILED in service.status_history
        assert observed_statuses[-1] == TaskStatus.FAILED


# ============================================================================
# 4. INJECTABLE DEPENDENCIES TESTS
# ============================================================================

class TestInjectableDependencies:
    """Tests verifying that all external dependencies are injectable and mockable."""

    def test_injectable_rag_dependency(self):
        calls: List[RAGSearchRequest] = []

        class MockRAG:
            def search(self, request: RAGSearchRequest) -> RAGSearchResponse:
                calls.append(request)
                return RAGSearchResponse(
                    results=[
                        RAGSearchResult(
                            document_id="custom_std_doc",
                            filename="ISO_13709.pdf",
                            page=42,
                            text="Shaft runout must not exceed 0.025 mm.",
                            score=0.98,
                        )
                    ]
                )

        response = execute_task(
            message="Verify shaft runout tolerance",
            document_ids=["custom_std_doc"],
            rag_service=MockRAG(),
        )

        assert len(calls) == 1
        assert calls[0].query == "Verify shaft runout tolerance"
        assert calls[0].document_ids == ["custom_std_doc"]
        assert len(response.sources) == 1
        assert response.sources[0].filename == "ISO_13709.pdf"
        assert response.sources[0].page == 42
        assert response.sources[0].reference == "Shaft runout must not exceed 0.025 mm."

    def test_injectable_ai_dependency(self):
        calls: List[AIGenerateRequest] = []

        class MockAI:
            def generate(self, request: AIGenerateRequest) -> AIGenerateResponse:
                calls.append(request)
                return AIGenerateResponse(
                    model="custom-industrial-llm",
                    answer="Identified 1 tolerance deviation based on ISO 13709.",
                    verification_status="verified_with_evidence",
                )

        response = execute_task(
            message="Analyze tolerance limits",
            document_ids=["doc_1"],
            ai_service=MockAI(),
        )

        assert len(calls) == 1
        assert calls[0].task_type == "reasoning"
        assert calls[0].prompt == "Analyze tolerance limits"
        assert response.answer == "Identified 1 tolerance deviation based on ISO 13709."

    def test_injectable_report_dependency(self):
        class MockReportClient:
            def generate(self, request: ReportGenerateRequest) -> ReportGenerateResponse:
                return ReportGenerateResponse(
                    report_id="rep_special_audit_001",
                    status="generated",
                    filename="special_audit_deliverable.docx",
                )

        response = execute_task(
            message="Prepare audit report",
            document_ids=["doc_1"],
            report_service=MockReportClient(),
        )

        assert response.report_id == "rep_special_audit_001"

    def test_injectable_verifier_dependency(self):
        class MockVerifier:
            def verify(
                self,
                task_id: str,
                findings: List[AuditFinding],
                sources: List[SourceReference],
            ) -> VerificationReport:
                return VerificationReport(
                    task_id=task_id,
                    total_findings=len(findings),
                    verified_findings_count=len(findings),
                    evidence_coverage=0.95,
                    requires_human_review=True,
                    verification_status=VerificationStatus.VERIFIED_WITH_EVIDENCE,
                    notes=["All findings cross-referenced with ISO standards."],
                )

        service = AgentService(verifier=MockVerifier())
        response = service.execute(
            message="Verify welding inspection records",
            document_ids=["doc_weld_01"],
        )

        assert service.verification_report is not None
        assert service.verification_report.evidence_coverage == 0.95
        assert service.verification_report.verification_status == VerificationStatus.VERIFIED_WITH_EVIDENCE
        assert response.verification_status == VerificationStatus.VERIFIED_WITH_EVIDENCE
        assert response.evidence_coverage == 0.95

    def test_callable_functional_dependencies(self):
        """Verify that simple callables/lambdas can be injected without class wrappers."""
        def custom_rag(req: RAGSearchRequest) -> RAGSearchResponse:
            return RAGSearchResponse(
                results=[
                    RAGSearchResult(
                        document_id="doc_lambda",
                        filename="lambda_doc.pdf",
                        page=10,
                        text="Lambda retrieved requirement text",
                        score=0.88,
                    )
                ]
            )

        def custom_ai(req: AIGenerateRequest) -> AIGenerateResponse:
            return AIGenerateResponse(
                model="lambda-model",
                answer="Lambda analysis result",
                verification_status="requires_review",
            )

        response = execute_task(
            message="Test callable injection",
            document_ids=["doc_lambda"],
            rag_service=custom_rag,
            ai_service=custom_ai,
        )

        assert response.status == TaskStatus.COMPLETED
        assert response.answer == "Lambda analysis result"
        assert len(response.sources) == 1
        assert response.sources[0].filename == "lambda_doc.pdf"


# ============================================================================
# 5. VERIFICATION AND FINDINGS REPRESENTATION TESTS
# ============================================================================

class TestVerificationAndFindings:
    """Tests covering AuditFinding and VerificationReport representation."""

    def test_audit_finding_schema_representation(self):
        finding = AuditFinding(
            finding="Potential wall thickness below minimum allowable limit",
            source="ASME_B31.3.pdf",
            page=45,
            requirement_evidence="Minimum wall thickness tm shall be 6.35 mm.",
            observed_source="UT_Inspection_Report.pdf",
            observed_page=3,
            observed_evidence="Observed thickness measured at elbow: 5.80 mm.",
            verification_status=VerificationStatus.REQUIRES_REVIEW,
            requires_human_review=True,
            severity="high",
            recommendations="Conduct immediate non-destructive re-examination.",
        )

        assert finding.finding == "Potential wall thickness below minimum allowable limit"
        assert finding.source == "ASME_B31.3.pdf"
        assert finding.page == 45
        assert finding.requirement_evidence == "Minimum wall thickness tm shall be 6.35 mm."
        assert finding.observed_source == "UT_Inspection_Report.pdf"
        assert finding.observed_page == 3
        assert finding.observed_evidence == "Observed thickness measured at elbow: 5.80 mm."
        assert finding.verification_status == VerificationStatus.REQUIRES_REVIEW
        assert finding.requires_human_review is True
        assert finding.severity == "high"

    def test_custom_findings_generator_integration(self):
        custom_finding = AuditFinding(
            finding="Safety relief valve set pressure mismatch",
            source="API_520.pdf",
            page=12,
            requirement_evidence="Relief valve set pressure must not exceed 10.5 bar.",
            observed_source="P_and_ID_104.pdf",
            observed_page=2,
            observed_evidence="PSV-104 set pressure shown as 11.2 bar.",
            verification_status=VerificationStatus.REQUIRES_REVIEW,
            requires_human_review=True,
            severity="critical",
            recommendations="Recalibrate PSV-104 set pressure to <= 10.5 bar.",
        )

        def mock_findings_gen(message, sources, ai_res):
            return [custom_finding]

        response = execute_task(
            message="Audit PSV-104 against API 520",
            document_ids=["API_520.pdf", "P_and_ID_104.pdf"],
            findings_generator=mock_findings_gen,
        )

        assert len(response.findings) == 1
        finding = response.findings[0]
        assert finding.finding == "Safety relief valve set pressure mismatch"
        assert finding.severity == "critical"
        assert finding.observed_evidence == "PSV-104 set pressure shown as 11.2 bar."

    def test_default_verifier_evidence_coverage_calculation(self):
        verifier = DefaultVerifier()
        sources = [
            SourceReference(
                document_id="std_doc",
                filename="Standard.pdf",
                page=1,
                reference="Requirement text",
            )
        ]

        # 2 findings: 1 fully grounded, 1 missing requirement evidence
        f1 = AuditFinding(
            finding="Grounded finding",
            source="Standard.pdf",
            page=1,
            requirement_evidence="Clear requirement text",
            observed_source="Standard.pdf",
            observed_page=1,
            observed_evidence="Clear observed evidence",
        )
        f2 = AuditFinding(
            finding="Ungrounded finding",
            source="Standard.pdf",
            page=1,
            requirement_evidence="",  # Missing requirement
            observed_source="Standard.pdf",
            observed_page=1,
            observed_evidence="Some observed evidence",
        )

        report = verifier.verify(
            task_id="test_task_metrics",
            findings=[f1, f2],
            sources=sources,
        )

        assert report.total_findings == 2
        assert report.verified_findings_count == 1
        assert report.evidence_coverage == 0.5
        assert report.requires_human_review is True
        assert report.verification_status == VerificationStatus.REQUIRES_REVIEW
        assert len(report.notes) == 1
        assert "Ungrounded finding" in report.notes[0]

    def test_default_verifier_zero_findings(self):
        verifier = DefaultVerifier()
        report = verifier.verify(
            task_id="task_zero",
            findings=[],
            sources=[],
        )

        assert report.total_findings == 0
        assert report.verified_findings_count == 0
        assert report.evidence_coverage == 0.0
        assert report.requires_human_review is True
