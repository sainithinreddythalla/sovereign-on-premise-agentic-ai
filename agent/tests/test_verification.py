"""
agent/tests/test_verification.py
Focused unit tests for Phase 3 Finding Verification & Evidence Handling.

Tests strictly cover:
1. Finding with sufficient evidence -> verified_with_evidence (requires_human_review = False)
2. Insufficient evidence -> requires_review (requires_human_review = True)
   - document identifier not in source references
   - page number mismatch
   - evidence text ungrounded in source reference
   - explicit uncertainty indicators
3. Missing/invalid evidence -> verification_incomplete (requires_human_review = True)
   - missing/whitespace requirement_evidence
   - missing/whitespace observed_evidence
   - missing/whitespace source or observed_source
   - empty source_references list
4. requires_human_review behavior across findings and aggregated report
5. Source references and evidence preserved exactly (no mutation, no invented evidence)
6. Deterministic repeated verification produces identical results
7. End-to-end integration with AgentService / execute_task
"""

import copy
import pytest

from agent.schemas import (
    AuditFinding,
    SourceReference,
    TaskStatus,
    TaskStatusResponse,
    VerificationReport,
    VerificationStatus,
)
from agent.service import AgentService, execute_task
from agent.verification import (
    EvidenceVerifier,
    is_evidence_grounded,
    verify_finding,
    verify_findings,
)


# ============================================================================
# FIXTURES & HELPERS
# ============================================================================

def make_valid_sources() -> list[SourceReference]:
    return [
        SourceReference(
            document_id="doc_std_api650",
            filename="API_650_Tank_Design.pdf",
            page=14,
            reference="Minimum nominal shell thickness tm for tanks of this diameter shall be 6.00 mm.",
        ),
        SourceReference(
            document_id="doc_insp_tk101",
            filename="Inspection_Report_TK101.pdf",
            page=3,
            reference="Ultrasonic thickness measurement at Course 1 shell plate recorded 5.20 mm.",
        ),
    ]


def make_valid_finding() -> AuditFinding:
    return AuditFinding(
        finding="Tank shell thickness below minimum design requirement",
        source="API_650_Tank_Design.pdf",
        page=14,
        requirement_evidence="Minimum nominal shell thickness tm for tanks of this diameter shall be 6.00 mm.",
        observed_source="Inspection_Report_TK101.pdf",
        observed_page=3,
        observed_evidence="Ultrasonic thickness measurement at Course 1 shell plate recorded 5.20 mm.",
        verification_status=VerificationStatus.REQUIRES_REVIEW,
        requires_human_review=True,
        severity="critical",
        recommendations="Derate maximum operating liquid level or perform immediate repair.",
    )


# ============================================================================
# 1. SUFFICIENT EVIDENCE TESTS
# ============================================================================

class TestSufficientEvidence:
    """Rule 3: Sufficient evidence -> verified_with_evidence, requires_human_review = False."""

    def test_sufficient_evidence_verified(self):
        sources = make_valid_sources()
        finding = make_valid_finding()

        verified = verify_finding(finding, sources)

        assert verified.verification_status == VerificationStatus.VERIFIED_WITH_EVIDENCE
        assert verified.requires_human_review is False

    def test_sufficient_evidence_matched_by_document_id(self):
        """Verify matching succeeds using document_id instead of filename."""
        sources = make_valid_sources()
        finding = AuditFinding(
            finding="Shell thickness non-conformance",
            source="doc_std_api650",
            page=14,
            requirement_evidence="Minimum nominal shell thickness tm for tanks of this diameter shall be 6.00 mm.",
            observed_source="doc_insp_tk101",
            observed_page=3,
            observed_evidence="Ultrasonic thickness measurement at Course 1 shell plate recorded 5.20 mm.",
        )

        verified = verify_finding(finding, sources)

        assert verified.verification_status == VerificationStatus.VERIFIED_WITH_EVIDENCE
        assert verified.requires_human_review is False

    def test_sufficient_evidence_unpaged_documents(self):
        """Unpaged documents (page=None) are treated as compatible."""
        sources = [
            SourceReference(
                document_id="doc_std",
                filename="Standard_Spec.pdf",
                page=None,
                reference="Relief valve set pressure must not exceed 10.0 bar.",
            ),
            SourceReference(
                document_id="doc_pnd",
                filename="PID_Diagram.pdf",
                page=None,
                reference="PSV-101 set pressure indicates 11.5 bar.",
            ),
        ]
        finding = AuditFinding(
            finding="Overpressure protection mismatch",
            source="Standard_Spec.pdf",
            page=None,
            requirement_evidence="Relief valve set pressure must not exceed 10.0 bar.",
            observed_source="PID_Diagram.pdf",
            observed_page=None,
            observed_evidence="PSV-101 set pressure indicates 11.5 bar.",
        )

        verified = verify_finding(finding, sources)

        assert verified.verification_status == VerificationStatus.VERIFIED_WITH_EVIDENCE
        assert verified.requires_human_review is False


# ============================================================================
# 2. INSUFFICIENT EVIDENCE TESTS
# ============================================================================

class TestInsufficientEvidence:
    """Rule 2: Insufficient evidence -> requires_review, requires_human_review = True."""

    def test_insufficient_evidence_unknown_source_document(self):
        sources = make_valid_sources()
        finding = make_valid_finding()
        finding.source = "Unknown_Unreferenced_Standard.pdf"

        verified = verify_finding(finding, sources)

        assert verified.verification_status == VerificationStatus.REQUIRES_REVIEW
        assert verified.requires_human_review is True

    def test_insufficient_evidence_unknown_observed_source(self):
        sources = make_valid_sources()
        finding = make_valid_finding()
        finding.observed_source = "Missing_Field_Report.pdf"

        verified = verify_finding(finding, sources)

        assert verified.verification_status == VerificationStatus.REQUIRES_REVIEW
        assert verified.requires_human_review is True

    def test_insufficient_evidence_page_mismatch(self):
        sources = make_valid_sources()
        finding = make_valid_finding()
        finding.page = 99  # Standard source is on page 14

        verified = verify_finding(finding, sources)

        assert verified.verification_status == VerificationStatus.REQUIRES_REVIEW
        assert verified.requires_human_review is True

    def test_insufficient_evidence_observed_page_mismatch(self):
        sources = make_valid_sources()
        finding = make_valid_finding()
        finding.observed_page = 88  # Inspection source is on page 3

        verified = verify_finding(finding, sources)

        assert verified.verification_status == VerificationStatus.REQUIRES_REVIEW
        assert verified.requires_human_review is True

    def test_insufficient_evidence_ungrounded_requirement_text(self):
        """Text exists, but is completely unrelated to the source reference excerpt."""
        sources = make_valid_sources()
        finding = make_valid_finding()
        # Fabricated requirement having zero overlap with API 650 tank shell thickness
        finding.requirement_evidence = "Electrical grounding resistance must not exceed 5 ohms in substation."

        verified = verify_finding(finding, sources)

        assert verified.verification_status == VerificationStatus.REQUIRES_REVIEW
        assert verified.requires_human_review is True

    def test_insufficient_evidence_uncertainty_indicators(self):
        """Explicit uncertainty language must prevent claiming result as confirmed fact."""
        sources = make_valid_sources()

        uncertain_titles = [
            "Potential unconfirmed tank shell thickness deviation",
            "Suspected flange misalignment (requires verification)",
            "Alleged valve rating mismatch (unverified)",
            "Uncertain nozzle weld flaw",
        ]

        for title in uncertain_titles:
            finding = make_valid_finding()
            finding.finding = title
            verified = verify_finding(finding, sources)

            assert verified.verification_status == VerificationStatus.REQUIRES_REVIEW
            assert verified.requires_human_review is True


# ============================================================================
# 3. MISSING / INVALID EVIDENCE TESTS
# ============================================================================

class TestMissingInvalidEvidence:
    """Rule 1: Missing/invalid evidence -> verification_incomplete, requires_human_review = True."""

    def test_missing_requirement_evidence(self):
        sources = make_valid_sources()
        finding = make_valid_finding()
        finding.requirement_evidence = ""

        verified = verify_finding(finding, sources)

        assert verified.verification_status == VerificationStatus.VERIFICATION_INCOMPLETE
        assert verified.requires_human_review is True

    def test_whitespace_requirement_evidence(self):
        sources = make_valid_sources()
        finding = make_valid_finding()
        finding.requirement_evidence = "    \n   "

        verified = verify_finding(finding, sources)

        assert verified.verification_status == VerificationStatus.VERIFICATION_INCOMPLETE
        assert verified.requires_human_review is True

    def test_missing_observed_evidence(self):
        sources = make_valid_sources()
        finding = make_valid_finding()
        finding.observed_evidence = ""

        verified = verify_finding(finding, sources)

        assert verified.verification_status == VerificationStatus.VERIFICATION_INCOMPLETE
        assert verified.requires_human_review is True

    def test_missing_source(self):
        sources = make_valid_sources()
        finding = make_valid_finding()
        finding.source = ""

        verified = verify_finding(finding, sources)

        assert verified.verification_status == VerificationStatus.VERIFICATION_INCOMPLETE
        assert verified.requires_human_review is True

    def test_missing_observed_source(self):
        sources = make_valid_sources()
        finding = make_valid_finding()
        finding.observed_source = ""

        verified = verify_finding(finding, sources)

        assert verified.verification_status == VerificationStatus.VERIFICATION_INCOMPLETE
        assert verified.requires_human_review is True

    def test_empty_source_references_list(self):
        finding = make_valid_finding()

        verified = verify_finding(finding, [])

        assert verified.verification_status == VerificationStatus.VERIFICATION_INCOMPLETE
        assert verified.requires_human_review is True

    def test_invalid_types_raise_typeerror(self):
        with pytest.raises(TypeError, match="finding must be an instance of AuditFinding"):
            verify_finding("not_a_finding", make_valid_sources())  # type: ignore

        with pytest.raises(TypeError, match="source_references must be a list of SourceReference"):
            verify_finding(make_valid_finding(), "not_a_list")  # type: ignore


# ============================================================================
# 4. REQUIRES_HUMAN_REVIEW BEHAVIOR TESTS
# ============================================================================

class TestRequiresHumanReviewBehavior:
    """Verifies requires_human_review flag semantics at finding and report level."""

    def test_finding_requires_human_review_false_when_sufficient(self):
        sources = make_valid_sources()
        finding = make_valid_finding()

        verified = verify_finding(finding, sources)
        assert verified.requires_human_review is False

    def test_finding_requires_human_review_true_when_insufficient(self):
        sources = make_valid_sources()
        finding = make_valid_finding()
        finding.source = "Nonexistent_Spec.pdf"

        verified = verify_finding(finding, sources)
        assert verified.requires_human_review is True

    def test_finding_requires_human_review_true_when_incomplete(self):
        sources = make_valid_sources()
        finding = make_valid_finding()
        finding.requirement_evidence = ""

        verified = verify_finding(finding, sources)
        assert verified.requires_human_review is True

    def test_report_requires_human_review_true_if_any_finding_unverified(self):
        sources = make_valid_sources()
        f_good = make_valid_finding()
        f_bad = make_valid_finding()
        f_bad.finding = "Unverified finding"
        f_bad.source = "Wrong_File.pdf"

        report = verify_findings(
            task_id="task_report_test",
            findings=[f_good, f_bad],
            source_references=sources,
            enforce_human_review=False,
        )

        assert report.total_findings == 2
        assert report.verified_findings_count == 1
        assert report.evidence_coverage == 0.5
        assert report.requires_human_review is True
        assert report.verification_status == VerificationStatus.REQUIRES_REVIEW

    def test_report_requires_human_review_false_when_all_sufficient_and_not_enforced(self):
        sources = make_valid_sources()
        f_good1 = make_valid_finding()
        f_good2 = make_valid_finding()

        report = verify_findings(
            task_id="task_report_good",
            findings=[f_good1, f_good2],
            source_references=sources,
            enforce_human_review=False,
        )

        assert report.total_findings == 2
        assert report.verified_findings_count == 2
        assert report.evidence_coverage == 1.0
        assert report.requires_human_review is False
        assert report.verification_status == VerificationStatus.VERIFIED_WITH_EVIDENCE


# ============================================================================
# 5. SOURCE REFERENCES PRESERVATION TESTS
# ============================================================================

class TestSourceReferencesPreservation:
    """Verifies that source references and finding evidence fields are NEVER mutated."""

    def test_source_references_exact_preservation(self):
        sources = make_valid_sources()
        original_sources = copy.deepcopy(sources)

        finding = make_valid_finding()
        original_finding = copy.deepcopy(finding)

        verify_finding(finding, sources)

        # 1. SourceReference list untouched
        assert len(sources) == len(original_sources)
        for actual, expected in zip(sources, original_sources):
            assert actual.document_id == expected.document_id
            assert actual.filename == expected.filename
            assert actual.page == expected.page
            assert actual.reference == expected.reference

        # 2. Finding content fields untouched (only verification status & human review modified)
        assert finding.finding == original_finding.finding
        assert finding.source == original_finding.source
        assert finding.page == original_finding.page
        assert finding.requirement_evidence == original_finding.requirement_evidence
        assert finding.observed_source == original_finding.observed_source
        assert finding.observed_page == original_finding.observed_page
        assert finding.observed_evidence == original_finding.observed_evidence
        assert finding.severity == original_finding.severity
        assert finding.recommendations == original_finding.recommendations

    def test_verify_findings_preserves_sources(self):
        sources = make_valid_sources()
        original_sources = copy.deepcopy(sources)
        findings = [make_valid_finding(), make_valid_finding()]

        verify_findings("task_preserve", findings, sources)

        assert sources == original_sources


# ============================================================================
# 6. DETERMINISTIC REPEATED VERIFICATION TESTS
# ============================================================================

class TestDeterministicVerification:
    """Verifies that verification is 100% deterministic over multiple invocations."""

    def test_verify_finding_deterministic_repetition(self):
        sources = make_valid_sources()

        test_cases = [
            make_valid_finding(),  # Sufficient
            AuditFinding(  # Insufficient
                finding="Unknown standard",
                source="Unknown.pdf",
                page=1,
                requirement_evidence="Requirement text",
                observed_source="API_650_Tank_Design.pdf",
                observed_page=14,
                observed_evidence="Observed text",
            ),
            AuditFinding(  # Missing
                finding="Empty requirement",
                source="API_650_Tank_Design.pdf",
                page=14,
                requirement_evidence="",
                observed_source="Inspection_Report_TK101.pdf",
                observed_page=3,
                observed_evidence="Observed text",
            ),
        ]

        for finding in test_cases:
            first_status = None
            first_review = None

            for _ in range(10):
                f_copy = copy.deepcopy(finding)
                result = verify_finding(f_copy, sources)

                if first_status is None:
                    first_status = result.verification_status
                    first_review = result.requires_human_review
                else:
                    assert result.verification_status == first_status
                    assert result.requires_human_review == first_review

    def test_verify_findings_deterministic_repetition(self):
        sources = make_valid_sources()
        findings = [make_valid_finding()]

        first_report = None
        for _ in range(5):
            findings_copy = copy.deepcopy(findings)
            report = verify_findings("task_repeat", findings_copy, sources)

            if first_report is None:
                first_report = report
            else:
                assert report.total_findings == first_report.total_findings
                assert report.verified_findings_count == first_report.verified_findings_count
                assert report.evidence_coverage == first_report.evidence_coverage
                assert report.requires_human_review == first_report.requires_human_review
                assert report.verification_status == first_report.verification_status
                assert report.notes == first_report.notes


# ============================================================================
# 7. INTEGRATION WITH AGENT SERVICE & EXECUTE_TASK
# ============================================================================

class TestAgentServiceIntegration:
    """Verifies that AgentService and execute_task seamlessly use Phase 3 verification."""

    def test_execute_task_integrates_phase3_verification(self):
        def findings_gen(message, sources, ai_res):
            return [
                # Finding 1: Grounded in sources
                AuditFinding(
                    finding="Grounded deviation",
                    source=sources[0].filename,
                    page=sources[0].page,
                    requirement_evidence=sources[0].reference,
                    observed_source=sources[0].filename,
                    observed_page=sources[0].page,
                    observed_evidence=f"Observed measurement for {message}",
                ),
                # Finding 2: Missing requirement evidence
                AuditFinding(
                    finding="Incomplete deviation",
                    source=sources[0].filename,
                    page=sources[0].page,
                    requirement_evidence="",
                    observed_source=sources[0].filename,
                    observed_page=sources[0].page,
                    observed_evidence="Some observation",
                ),
            ]

        response = execute_task(
            message="Check nozzle reinforcement",
            document_ids=["doc_api650"],
            findings_generator=findings_gen,
        )

        assert response.status == TaskStatus.COMPLETED
        assert len(response.findings) == 2
        # Finding 1 is verified with evidence
        assert response.findings[0].verification_status == VerificationStatus.VERIFIED_WITH_EVIDENCE
        assert response.findings[0].requires_human_review is False
        # Finding 2 is verification incomplete
        assert response.findings[1].verification_status == VerificationStatus.VERIFICATION_INCOMPLETE
        assert response.findings[1].requires_human_review is True
        # Overall metrics
        assert response.evidence_coverage == 0.5
        assert response.requires_human_review is True

    def test_custom_verifier_injection_respected(self):
        """Phase 2 verifier injection remains 100% backward compatible."""
        class CustomMockVerifier:
            def verify(self, task_id, findings, sources):
                return VerificationReport(
                    task_id=task_id,
                    total_findings=len(findings),
                    verified_findings_count=len(findings),
                    evidence_coverage=0.99,
                    requires_human_review=False,
                    verification_status=VerificationStatus.VERIFIED_WITH_EVIDENCE,
                    notes=["Custom verifier executed"],
                )

        service = AgentService(verifier=CustomMockVerifier())
        response = service.execute(
            message="Audit heat exchanger tubes",
            document_ids=["doc_1"],
        )

        assert response.evidence_coverage == 0.99
        assert response.verification_status == VerificationStatus.VERIFIED_WITH_EVIDENCE
        assert response.requires_human_review is False
