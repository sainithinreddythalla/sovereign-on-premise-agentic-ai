from enum import Enum

import pytest
from pydantic import ValidationError

from agent.schemas import (
    AIGenerateRequest,
    AIGenerateResponse,
    AgentActionType,
    AuditFinding,
    PlanStep,
    RAGSearchRequest,
    RAGSearchResponse,
    RAGSearchResult,
    ReportGenerateRequest,
    ReportGenerateResponse,
    SourceReference,
    TaskCreateRequest,
    TaskCreateResponse,
    TaskPlan,
    TaskStatus,
    TaskStatusResponse,
    VerificationReport,
    VerificationStatus,
)


SOURCE_DATA = {
    "document_id": "doc-001",
    "filename": "safety-manual.pdf",
    "page": 17,
    "reference": "Relevant safety requirement",
}

FINDING_DATA = {
    "finding": "Potential safety requirement mismatch",
    "source": "safety-manual.pdf",
    "page": 17,
    "requirement_evidence": "Relevant requirement text",
    "observed_source": "inspection-report.pdf",
    "observed_page": 4,
    "observed_evidence": "Observed condition text",
}


def build_model_instances():
    source = SourceReference(**SOURCE_DATA)
    finding = AuditFinding(**FINDING_DATA)
    step = PlanStep(
        step_number=1,
        description="Retrieve supporting evidence",
        action=AgentActionType.RAG_SEARCH,
        parameters={"query": "safety requirement"},
        result={"matches": 1},
    )

    return [
        TaskCreateRequest(message="Audit the equipment.", document_ids=["doc-001"]),
        TaskCreateResponse(task_id="task-001"),
        source,
        finding,
        TaskStatusResponse(
            task_id="task-001",
            status=TaskStatus.COMPLETED,
            answer="One potential deviation was identified.",
            verification_status=VerificationStatus.REQUIRES_REVIEW,
            evidence_coverage=0.92,
            requires_human_review=True,
            sources=[source],
            findings=[finding],
            report_id="report-001",
        ),
        RAGSearchRequest(query="Applicable requirements", document_ids=["doc-001"]),
        RAGSearchResult(
            document_id="doc-001",
            filename="safety-manual.pdf",
            page=17,
            text="Relevant document content",
            score=0.91,
        ),
        RAGSearchResponse(results=[]),
        AIGenerateRequest(prompt="Analyze the retrieved evidence.", context=[source.model_dump()]),
        AIGenerateResponse(
            model="selected-model",
            answer="Potential deviation identified.",
            verification_status="requires_review",
        ),
        ReportGenerateRequest(task_id="task-001"),
        ReportGenerateResponse(
            report_id="report-001",
            filename="industrial_audit_report.docx",
        ),
        step,
        TaskPlan(task_id="task-001", goal="Audit the equipment.", steps=[step]),
        VerificationReport(
            task_id="task-001",
            total_findings=1,
            verified_findings_count=0,
            evidence_coverage=0.0,
            notes=["Human review required"],
        ),
    ]


@pytest.mark.parametrize(
    ("enum_type", "values"),
    [
        (TaskStatus, [member.value for member in TaskStatus]),
        (VerificationStatus, [member.value for member in VerificationStatus]),
        (AgentActionType, [member.value for member in AgentActionType]),
    ],
)
def test_enums_accept_every_declared_value(enum_type, values):
    assert all(enum_type(value).value == value for value in values)
    assert all(isinstance(member, Enum) for member in enum_type)


@pytest.mark.parametrize(
    ("enum_type", "invalid_value"),
    [
        (TaskStatus, "not-a-task-status"),
        (VerificationStatus, "not-a-verification-status"),
        (AgentActionType, "not-an-agent-action"),
    ],
)
def test_enums_reject_undeclared_values(enum_type, invalid_value):
    with pytest.raises(ValueError):
        enum_type(invalid_value)


def test_all_fifteen_models_construct_valid_instances():
    instances = build_model_instances()

    assert len(instances) == 15
    assert all(instance.__class__.__name__ for instance in instances)


@pytest.mark.parametrize(
    ("model_type", "payload", "missing_field"),
    [
        (TaskCreateRequest, {"message": "Audit", "document_ids": ["doc-001"]}, "message"),
        (TaskCreateRequest, {"message": "Audit", "document_ids": ["doc-001"]}, "document_ids"),
        (TaskCreateResponse, {"task_id": "task-001"}, "task_id"),
        (SourceReference, SOURCE_DATA, "document_id"),
        (SourceReference, SOURCE_DATA, "filename"),
        (SourceReference, SOURCE_DATA, "reference"),
        (AuditFinding, FINDING_DATA, "finding"),
        (AuditFinding, FINDING_DATA, "source"),
        (AuditFinding, FINDING_DATA, "requirement_evidence"),
        (AuditFinding, FINDING_DATA, "observed_source"),
        (AuditFinding, FINDING_DATA, "observed_evidence"),
        (TaskStatusResponse, {"task_id": "task-001", "status": "queued"}, "task_id"),
        (TaskStatusResponse, {"task_id": "task-001", "status": "queued"}, "status"),
        (RAGSearchRequest, {"query": "requirements", "document_ids": ["doc-001"]}, "query"),
        (RAGSearchRequest, {"query": "requirements", "document_ids": ["doc-001"]}, "document_ids"),
        (
            RAGSearchResult,
            {
                "document_id": "doc-001",
                "filename": "manual.pdf",
                "page": 1,
                "text": "text",
                "score": 0.5,
            },
            "document_id",
        ),
        (
            RAGSearchResult,
            {
                "document_id": "doc-001",
                "filename": "manual.pdf",
                "page": 1,
                "text": "text",
                "score": 0.5,
            },
            "filename",
        ),
        (
            RAGSearchResult,
            {
                "document_id": "doc-001",
                "filename": "manual.pdf",
                "page": 1,
                "text": "text",
                "score": 0.5,
            },
            "text",
        ),
        (
            RAGSearchResult,
            {
                "document_id": "doc-001",
                "filename": "manual.pdf",
                "page": 1,
                "text": "text",
                "score": 0.5,
            },
            "score",
        ),
        (AIGenerateRequest, {"prompt": "Analyze"}, "prompt"),
        (AIGenerateResponse, {"model": "model", "answer": "answer"}, "model"),
        (AIGenerateResponse, {"model": "model", "answer": "answer"}, "answer"),
        (ReportGenerateRequest, {"task_id": "task-001"}, "task_id"),
        (ReportGenerateResponse, {"report_id": "report-001", "filename": "report.docx"}, "report_id"),
        (ReportGenerateResponse, {"report_id": "report-001", "filename": "report.docx"}, "filename"),
        (
            PlanStep,
            {"step_number": 1, "description": "Plan", "action": "rag_search"},
            "step_number",
        ),
        (
            PlanStep,
            {"step_number": 1, "description": "Plan", "action": "rag_search"},
            "description",
        ),
        (
            PlanStep,
            {"step_number": 1, "description": "Plan", "action": "rag_search"},
            "action",
        ),
        (TaskPlan, {"task_id": "task-001", "goal": "Plan"}, "task_id"),
        (TaskPlan, {"task_id": "task-001", "goal": "Plan"}, "goal"),
        (VerificationReport, {"task_id": "task-001"}, "task_id"),
    ],
)
def test_models_reject_missing_required_fields(model_type, payload, missing_field):
    incomplete_payload = dict(payload)
    incomplete_payload.pop(missing_field)

    with pytest.raises(ValidationError):
        model_type(**incomplete_payload)


@pytest.mark.parametrize(
    ("model_type", "payload", "field"),
    [
        (TaskCreateRequest, {"message": "Audit", "document_ids": [{"id": "doc-001"}]}, "document_ids"),
        (TaskStatusResponse, {"task_id": "task-001", "status": "invalid"}, "status"),
        (AuditFinding, {**FINDING_DATA, "verification_status": "invalid"}, "verification_status"),
        (PlanStep, {"step_number": 1, "description": "Plan", "action": "invalid"}, "action"),
        (VerificationReport, {"task_id": "task-001", "verification_status": "invalid"}, "verification_status"),
        (SourceReference, {**SOURCE_DATA, "page": {"page": 1}}, "page"),
        (RAGSearchResult, {
            "document_id": "doc-001",
            "filename": "manual.pdf",
            "text": "text",
            "score": {"score": 0.5},
        }, "score"),
    ],
)
def test_models_reject_incompatible_field_types(model_type, payload, field):
    with pytest.raises(ValidationError):
        model_type(**payload)


def test_declared_defaults_and_optional_fields():
    task_response = TaskCreateResponse(task_id="task-001")
    finding = AuditFinding(**FINDING_DATA)
    finding_without_optional_pages = AuditFinding(
        finding="Potential safety requirement mismatch",
        source="safety-manual.pdf",
        requirement_evidence="Relevant requirement text",
        observed_source="inspection-report.pdf",
        observed_evidence="Observed condition text",
    )
    task_status = TaskStatusResponse(task_id="task-001", status=TaskStatus.QUEUED)
    rag_request = RAGSearchRequest(query="query", document_ids=[])
    ai_request = AIGenerateRequest(prompt="prompt")
    ai_response = AIGenerateResponse(model="model", answer="answer")
    report_request = ReportGenerateRequest(task_id="task-001")
    report_response = ReportGenerateResponse(report_id="report-001", filename="report.docx")
    plan_step = PlanStep(step_number=1, description="Plan", action=AgentActionType.AI_MODEL)
    task_plan = TaskPlan(task_id="task-001", goal="Goal")
    verification = VerificationReport(task_id="task-001")

    assert task_response.status is TaskStatus.QUEUED
    assert finding.verification_status is VerificationStatus.REQUIRES_REVIEW
    assert finding.requires_human_review is True
    assert finding.page == 17
    assert finding.observed_page == 4
    assert finding_without_optional_pages.page is None
    assert finding_without_optional_pages.observed_page is None
    assert finding.severity is None
    assert finding.recommendations is None
    assert task_status.answer is None
    assert task_status.verification_status is None
    assert task_status.evidence_coverage is None
    assert task_status.requires_human_review is None
    assert task_status.sources == []
    assert task_status.findings == []
    assert task_status.report_id is None
    assert rag_request.top_k == 5
    assert ai_request.task_type == "reasoning"
    assert ai_request.context == []
    assert ai_response.verification_status is None
    assert report_request.format == "docx"
    assert report_response.status == "generated"
    assert plan_step.parameters == {}
    assert plan_step.completed is False
    assert plan_step.result is None
    assert task_plan.steps == []
    assert verification.total_findings == 0
    assert verification.verified_findings_count == 0
    assert verification.evidence_coverage == 0.0
    assert verification.requires_human_review is True
    assert verification.verification_status is VerificationStatus.REQUIRES_REVIEW
    assert verification.notes == []


def test_optional_and_nested_fields_accept_declared_values():
    source_without_page = SourceReference(
        document_id="doc-001",
        filename="unpaged.txt",
        reference="Reference text",
    )
    finding_data_with_options = {
        **FINDING_DATA,
        "page": None,
        "observed_page": None,
        "verification_status": VerificationStatus.VERIFIED_WITH_EVIDENCE,
        "requires_human_review": False,
        "severity": "critical-as-defined-by-caller",
        "recommendations": "Inspect the equipment.",
    }
    finding_with_options = AuditFinding(**finding_data_with_options)
    nested_response = TaskStatusResponse(
        task_id="task-001",
        status=TaskStatus.VERIFYING,
        sources=[source_without_page],
        findings=[finding_with_options],
    )

    assert nested_response.sources[0] == source_without_page
    assert nested_response.findings[0] == finding_with_options


def test_meaningful_declared_boundaries_are_accepted_without_invented_constraints():
    assert TaskCreateRequest(message="", document_ids=[]).message == ""
    assert RAGSearchRequest(query="", document_ids=[], top_k=0).top_k == 0
    assert RAGSearchResult(
        document_id="",
        filename="",
        page=-1,
        text="",
        score=-1.0,
    ).score == -1.0
    assert PlanStep(
        step_number=0,
        description="",
        action=AgentActionType.RAG_SEARCH,
    ).step_number == 0
    assert VerificationReport(
        task_id="",
        total_findings=-1,
        verified_findings_count=-2,
        evidence_coverage=2.0,
    ).evidence_coverage == 2.0
    assert ReportGenerateRequest(task_id="", format="any-format").format == "any-format"
    assert AIGenerateResponse(
        model="model",
        answer="answer",
        verification_status="any-verification-tag",
    ).verification_status == "any-verification-tag"


@pytest.mark.parametrize("instance", build_model_instances())
def test_dictionary_serialization_and_reconstruction(instance):
    serialized = instance.model_dump()
    reconstructed = instance.__class__(**serialized)

    assert isinstance(serialized, dict)
    assert reconstructed == instance


@pytest.mark.parametrize("instance", build_model_instances())
def test_json_serialization_and_parsing(instance):
    serialized = instance.model_dump_json()
    reconstructed = instance.__class__.model_validate_json(serialized)

    assert isinstance(serialized, str)
    assert reconstructed == instance


def test_mutable_defaults_are_independent_between_instances():
    task_status_a = TaskStatusResponse(task_id="task-a", status=TaskStatus.QUEUED)
    task_status_b = TaskStatusResponse(task_id="task-b", status=TaskStatus.QUEUED)
    rag_response_a = RAGSearchResponse()
    rag_response_b = RAGSearchResponse()
    ai_request_a = AIGenerateRequest(prompt="a")
    ai_request_b = AIGenerateRequest(prompt="b")
    plan_step_a = PlanStep(step_number=1, description="a", action=AgentActionType.AI_MODEL)
    plan_step_b = PlanStep(step_number=2, description="b", action=AgentActionType.AI_MODEL)
    task_plan_a = TaskPlan(task_id="task-a", goal="a")
    task_plan_b = TaskPlan(task_id="task-b", goal="b")
    verification_a = VerificationReport(task_id="task-a")
    verification_b = VerificationReport(task_id="task-b")

    task_status_a.sources.append(SourceReference(**SOURCE_DATA))
    task_status_a.findings.append(AuditFinding(**FINDING_DATA))
    rag_response_a.results.append(
        RAGSearchResult(
            document_id="doc-001",
            filename="manual.pdf",
            text="text",
            score=0.5,
        )
    )
    ai_request_a.context.append("context")
    plan_step_a.parameters["key"] = "value"
    task_plan_a.steps.append(plan_step_a)
    verification_a.notes.append("note")

    assert task_status_b.sources == []
    assert task_status_b.findings == []
    assert rag_response_b.results == []
    assert ai_request_b.context == []
    assert plan_step_b.parameters == {}
    assert task_plan_b.steps == []
    assert verification_b.notes == []