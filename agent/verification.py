"""
agent/verification.py
Module 3: Agent + Industrial Workflow Verification & Evidence Handling.

Phase 3 Finding Verification strictly aligned with SIH26117 PROJECT_SPEC.md:
- Section 7: Primary Demonstration Workflow & Expected Outputs
- Section 14: Agent Flow (Verification Layer)
- Section 15: Verification Layer (Grounding, Evidence Checking, Human Review Flags)
- Section 16: Evidence and Grounding (Traceable findings with requirement & observed evidence)

Verification Decision Rules:
1. Missing/Invalid Evidence:
   - Required evidence fields (requirement_evidence, observed_evidence, source, observed_source)
     are missing, empty, or whitespace.
   - Supplied SourceReference list is empty or None.
   Result:
     verification_status = VERIFICATION_INCOMPLETE
     requires_human_review = True

2. Insufficient Evidence:
   - Referenced standard document (source) cannot be matched to supplied SourceReference records.
   - Referenced observed document (observed_source) cannot be matched to supplied SourceReference records.
   - Specified page numbers do not match source records.
   - Requirement evidence cannot be grounded in matched source reference text.
   - Finding contains explicit uncertainty indicators.
   Result:
     verification_status = REQUIRES_REVIEW
     requires_human_review = True

3. Sufficient Evidence:
   - Non-empty requirement_evidence and observed_evidence.
   - Referenced source documents and pages matched to supplied SourceReference records.
   - Requirement evidence grounded in source reference text.
   - No uncertainty indicators.
   Result:
     verification_status = VERIFIED_WITH_EVIDENCE
     requires_human_review = False
"""

from typing import Any, Dict, List, Optional, Set, Tuple
import os

from .schemas import (
    AuditFinding,
    SourceReference,
    VerificationReport,
    VerificationStatus,
)


UNCERTAINTY_INDICATORS: Tuple[str, ...] = (
    "uncertain",
    "unverified",
    "unconfirmed",
    "requires verification",
    "requires human review",
    "requires review",
    "needs review",
    "needs verification",
    "suspected",
    "alleged",
    "cannot confirm",
    "unable to confirm",
    "verification incomplete",
    "not verified",
    "unsupported",
)


def _match_document_identifier(doc_identifier: str, ref: SourceReference) -> bool:
    """
    Check if a document identifier (filename or doc_id) matches a SourceReference.
    Handles exact matches, basenames, and file extension normalization deterministically.
    """
    if not doc_identifier:
        return False

    target = doc_identifier.strip().lower()
    ref_id = (ref.document_id or "").strip().lower()
    ref_fname = (ref.filename or "").strip().lower()

    if target in (ref_id, ref_fname):
        return True

    # Basename matching
    target_base = os.path.basename(target)
    ref_fname_base = os.path.basename(ref_fname)
    if target_base in (ref_id, ref_fname_base):
        return True

    # Root name without extension (e.g. "doc_001.pdf" vs "doc_001")
    target_root, _ = os.path.splitext(target_base)
    ref_root, _ = os.path.splitext(ref_fname_base)
    if target_root in (ref_id, ref_root):
        return True

    return False


def _find_matching_sources(
    doc_identifier: str,
    page: Optional[int],
    source_references: List[SourceReference],
) -> List[SourceReference]:
    """
    Find all SourceReference entries matching document identifier and page.
    If page is specified on both sides, they must match.
    If page is None on either side, it is treated as compatible (unpaged/scanned doc).
    """
    matches: List[SourceReference] = []
    for ref in source_references:
        if _match_document_identifier(doc_identifier, ref):
            if page is None or ref.page is None or page == ref.page:
                matches.append(ref)
    return matches


def is_evidence_grounded(evidence_text: str, source_reference_text: str) -> bool:
    """
    Deterministic check whether evidence text is grounded in the source reference text.
    Prevents ungrounded claims from being verified merely because text exists.
    """
    if not evidence_text or not source_reference_text:
        return False

    ev_norm = " ".join(evidence_text.lower().split())
    ref_norm = " ".join(source_reference_text.lower().split())

    # Substring containment in either direction
    if ev_norm in ref_norm or ref_norm in ev_norm:
        return True

    # Token overlap check (ignoring common English stopwords)
    stopwords = {
        "a", "an", "the", "in", "on", "at", "to", "for", "of", "and", "or",
        "is", "are", "shall", "be", "was", "were", "by", "with", "this", "that",
    }
    ev_tokens = [
        w for w in "".join(c if c.isalnum() else " " for c in ev_norm).split()
        if w not in stopwords and len(w) > 1
    ]
    ref_tokens = [
        w for w in "".join(c if c.isalnum() else " " for c in ref_norm).split()
        if w not in stopwords and len(w) > 1
    ]

    if not ev_tokens or not ref_tokens:
        return False

    ev_set = set(ev_tokens)
    ref_set = set(ref_tokens)
    common = ev_set.intersection(ref_set)

    # Substantial token overlap ratio
    ratio_ref = len(common) / len(ref_set)
    ratio_ev = len(common) / len(ev_set)

    return ratio_ref >= 0.4 or ratio_ev >= 0.4


def _has_uncertainty_indicators(finding: AuditFinding) -> bool:
    """Check if the finding summary or evidence text contains explicit uncertainty language."""
    combined_text = (
        f"{finding.finding} {finding.requirement_evidence} {finding.observed_evidence}"
    ).lower()
    return any(indicator in combined_text for indicator in UNCERTAINTY_INDICATORS)


def verify_finding(
    finding: AuditFinding,
    source_references: List[SourceReference],
) -> AuditFinding:
    """
    Verify an individual AuditFinding against supplied SourceReference records.

    Verification decision rules:
    - Missing/invalid evidence:
      required evidence fields or source references are missing/invalid.
      Result:
        verification_status = VERIFICATION_INCOMPLETE
        requires_human_review = True

    - Insufficient evidence:
      evidence is incomplete or cannot adequately support the finding.
      Result:
        verification_status = REQUIRES_REVIEW
        requires_human_review = True

    - Sufficient evidence:
      finding has non-empty requirement_evidence, non-empty observed_evidence,
      and its referenced source documents/pages can be matched to the supplied
      SourceReference records and grounded in evidence.
      Result:
        verification_status = VERIFIED_WITH_EVIDENCE
        requires_human_review = False
    """
    if not isinstance(finding, AuditFinding):
        raise TypeError("finding must be an instance of AuditFinding")
    if not isinstance(source_references, list):
        raise TypeError("source_references must be a list of SourceReference")

    # Rule 1: Missing / invalid evidence check
    has_req = bool(finding.requirement_evidence and finding.requirement_evidence.strip())
    has_obs = bool(finding.observed_evidence and finding.observed_evidence.strip())
    has_source = bool(finding.source and finding.source.strip())
    has_obs_source = bool(finding.observed_source and finding.observed_source.strip())
    has_refs = bool(source_references and len(source_references) > 0)

    if not (has_req and has_obs and has_source and has_obs_source and has_refs):
        finding.verification_status = VerificationStatus.VERIFICATION_INCOMPLETE
        finding.requires_human_review = True
        return finding

    # Rule 2 / 3: Source matching and grounding
    std_matches = _find_matching_sources(finding.source, finding.page, source_references)
    if not std_matches:
        finding.verification_status = VerificationStatus.REQUIRES_REVIEW
        finding.requires_human_review = True
        return finding

    obs_matches = _find_matching_sources(finding.observed_source, finding.observed_page, source_references)
    if not obs_matches:
        finding.verification_status = VerificationStatus.REQUIRES_REVIEW
        finding.requires_human_review = True
        return finding

    # Check uncertainty indicators
    if _has_uncertainty_indicators(finding):
        finding.verification_status = VerificationStatus.REQUIRES_REVIEW
        finding.requires_human_review = True
        return finding

    # Grounding check: requirement evidence must be supported by matched standard source reference
    is_grounded = any(is_evidence_grounded(finding.requirement_evidence, r.reference) for r in std_matches)
    if not is_grounded:
        finding.verification_status = VerificationStatus.REQUIRES_REVIEW
        finding.requires_human_review = True
        return finding

    # Rule 3: Sufficient evidence verified
    finding.verification_status = VerificationStatus.VERIFIED_WITH_EVIDENCE
    finding.requires_human_review = False
    return finding


def verify_findings(
    task_id: str,
    findings: List[AuditFinding],
    source_references: List[SourceReference],
    *,
    enforce_human_review: bool = True,
) -> VerificationReport:
    """
    Verify a collection of AuditFinding items and generate an aggregated VerificationReport.
    Updates each finding's verification_status and requires_human_review.

    Parameters:
        task_id: Associated task identifier.
        findings: List of candidate audit findings to verify.
        source_references: Referenced sources extracted from documents.
        enforce_human_review: If True (default), the overall report requires human review
                              in accordance with industrial safety standards (Section 7 & 15).
                              If False, report requires human review only if any finding does.
    """
    total = len(findings)
    if total == 0:
        return VerificationReport(
            task_id=task_id,
            total_findings=0,
            verified_findings_count=0,
            evidence_coverage=1.0 if source_references else 0.0,
            requires_human_review=True,
            verification_status=VerificationStatus.REQUIRES_REVIEW,
            notes=["No candidate audit findings provided for verification."],
        )

    verified_count = 0
    incomplete_count = 0
    notes: List[str] = []

    for finding in findings:
        verify_finding(finding, source_references)

        if finding.verification_status == VerificationStatus.VERIFIED_WITH_EVIDENCE:
            verified_count += 1
        elif finding.verification_status == VerificationStatus.VERIFICATION_INCOMPLETE:
            incomplete_count += 1
            notes.append(
                f"Finding '{finding.finding}' lacks complete verified evidence grounding (missing or invalid evidence fields)."
            )
        else:
            notes.append(
                f"Finding '{finding.finding}' lacks complete verified evidence grounding (insufficient evidence backing or requires review)."
            )

    coverage = round(verified_count / total, 2)

    if enforce_human_review:
        requires_review = True
    else:
        requires_review = any(f.requires_human_review for f in findings)

    if coverage >= 0.8 and incomplete_count == 0:
        overall_status = VerificationStatus.VERIFIED_WITH_EVIDENCE
    elif incomplete_count == total:
        overall_status = VerificationStatus.VERIFICATION_INCOMPLETE
    else:
        overall_status = VerificationStatus.REQUIRES_REVIEW

    return VerificationReport(
        task_id=task_id,
        total_findings=total,
        verified_findings_count=verified_count,
        evidence_coverage=coverage,
        requires_human_review=requires_review,
        verification_status=overall_status,
        notes=notes,
    )


class EvidenceVerifier:
    """
    Injectable verifier component implementing Section 15 of PROJECT_SPEC.md.
    Provides verify() method compatible with AgentService and VerifierProtocol.
    """
    def __init__(self, *, enforce_human_review: bool = True):
        self.enforce_human_review = enforce_human_review

    def verify(
        self,
        task_id: str,
        findings: List[AuditFinding],
        sources: List[SourceReference],
    ) -> VerificationReport:
        return verify_findings(task_id, findings, sources, enforce_human_review=self.enforce_human_review)

    def __call__(
        self,
        task_id: str,
        findings: List[AuditFinding],
        sources: List[SourceReference],
    ) -> VerificationReport:
        return verify_findings(task_id, findings, sources, enforce_human_review=self.enforce_human_review)
