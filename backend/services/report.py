"""Local report generation service."""

import json
import re
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

from backend.models.task import Task


REPORT_DIR = Path(__file__).resolve().parent.parent / "reports"


def _safe_filename(task_id: str) -> str:
    """Create a filesystem-safe report filename."""
    safe_task_id = re.sub(r"[^A-Za-z0-9_.-]", "_", task_id)
    return f"{safe_task_id}_{uuid.uuid4().hex[:8]}.docx"


def _paragraph(text: str) -> str:
    """Create a WordprocessingML paragraph."""
    return (
        "<w:p>"
        "<w:r>"
        f"<w:t xml:space=\"preserve\">{escape(str(text))}</w:t>"
        "</w:r>"
        "</w:p>"
    )


def _document_xml(paragraphs: list[str]) -> str:
    """Build the main WordprocessingML document."""
    body = "".join(_paragraph(text) for text in paragraphs)
    body += (
        "<w:sectPr>"
        "<w:pgSz w:w=\"12240\" w:h=\"15840\"/>"
        "<w:pgMar w:top=\"1440\" w:right=\"1440\" "
        "w:bottom=\"1440\" w:left=\"1440\"/>"
        "</w:sectPr>"
    )

    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<w:document "
        "xmlns:w=\"http://schemas.openxmlformats.org/wordprocessingml/2006/main\">"
        f"<w:body>{body}</w:body>"
        "</w:document>"
    )


def _write_docx(path: Path, paragraphs: list[str]) -> None:
    """Write a minimal valid DOCX package."""
    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml"
ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""

    relationships = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1"
Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument"
Target="word/document.xml"/>
</Relationships>"""

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types)
        archive.writestr("_rels/.rels", relationships)
        archive.writestr("word/document.xml", _document_xml(paragraphs))


def _load_json(value: str | None) -> list:
    """Load persisted JSON arrays safely."""
    if not value:
        return []

    try:
        loaded = json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return []

    return loaded if isinstance(loaded, list) else []


def generate_report(db, task_id: str, report_format: str = "docx") -> tuple[str, str]:
    """Generate a local report from persisted verified task data."""
    if report_format.lower() != "docx":
        raise ValueError("Only docx report generation is currently supported.")

    task = db.query(Task).filter(Task.task_id == task_id).first()

    if task is None:
        raise LookupError("Task not found")

    sources = _load_json(task.sources)
    findings = _load_json(task.findings)

    paragraphs = [
        "Audit Report",
        f"Task ID: {task.task_id}",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "Task",
        task.message,
        "",
        "Result",
        task.answer or "",
        "",
        "Verification",
        f"Verification status: {task.verification_status or 'unknown'}",
        f"Evidence coverage: {task.evidence_coverage if task.evidence_coverage is not None else 'unknown'}",
        f"Requires human review: {bool(task.requires_human_review) if task.requires_human_review is not None else 'unknown'}",
        "",
        "Sources",
    ]

    if sources:
        for index, source in enumerate(sources, start=1):
            paragraphs.append(
                f"{index}. "
                f"Document ID: {source.get('document_id', '')}; "
                f"Filename: {source.get('filename', '')}; "
                f"Page: {source.get('page', '')}; "
                f"Reference: {source.get('reference', '')}"
            )
    else:
        paragraphs.append("No source references recorded.")

    paragraphs.extend(["", "Findings"])

    if findings:
        for index, finding in enumerate(findings, start=1):
            paragraphs.extend(
                [
                    f"Finding {index}: {finding.get('finding', '')}",
                    f"Source: {finding.get('source', '')}",
                    f"Page: {finding.get('page', '')}",
                    f"Requirement evidence: {finding.get('requirement_evidence', '')}",
                    f"Observed source: {finding.get('observed_source', '')}",
                    f"Observed page: {finding.get('observed_page', '')}",
                    f"Observed evidence: {finding.get('observed_evidence', '')}",
                    f"Verification status: {finding.get('verification_status', '')}",
                    f"Requires human review: {finding.get('requires_human_review', '')}",
                    f"Severity: {finding.get('severity', '')}",
                    f"Recommendations: {finding.get('recommendations', '')}",
                    "",
                ]
            )
    else:
        paragraphs.append("No findings recorded.")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    filename = _safe_filename(task_id)
    output_path = REPORT_DIR / filename
    _write_docx(output_path, paragraphs)

    report_id = f"report_{uuid.uuid4().hex[:12]}"

    task.report_id = report_id
    db.commit()

    return report_id, filename