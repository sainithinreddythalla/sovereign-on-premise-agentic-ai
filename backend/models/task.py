"""SQLAlchemy model for audit task lifecycle and results."""

from datetime import datetime, timezone
from enum import Enum
import uuid

from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from backend.database import Base


class TaskStatus(str, Enum):
    QUEUED = "queued"
    PLANNING = "planning"
    RETRIEVING = "retrieving"
    ANALYZING = "analyzing"
    VERIFYING = "verifying"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


def generate_task_id() -> str:
    return f"task_{uuid.uuid4().hex[:12]}"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Task(Base):
    """Persistent task metadata and result state."""

    __tablename__ = "tasks"

    task_id = Column(
        String(64),
        primary_key=True,
        index=True,
        default=generate_task_id,
    )
    message = Column(Text, nullable=False)
    status = Column(
        String(32),
        nullable=False,
        default=TaskStatus.QUEUED.value,
    )
    document_ids = Column(Text, nullable=False, default="[]")

    answer = Column(Text, nullable=True)
    verification_status = Column(String(64), nullable=True)
    evidence_coverage = Column(Float, nullable=True)
    requires_human_review = Column(Integer, nullable=True)
    report_id = Column(String(64), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )