"""SQLAlchemy database model for confidential industrial documents.

Conforms to Section 11.1, 11.2, 12.1, and 12.2 of PROJECT_SPEC.md.
"""

from datetime import datetime, timezone
from enum import Enum
import uuid

from sqlalchemy import Column, DateTime, Integer, String
from backend.database import Base


class DocumentStatus(str, Enum):
    """Document lifecycle statuses explicitly enumerated in Section 11.2."""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


def generate_document_id() -> str:
    """Generate a safe, unique document identifier prefixed with 'doc_'."""
    return f"doc_{uuid.uuid4().hex[:12]}"


def utc_now() -> datetime:
    """Return timezone-aware current UTC datetime."""
    return datetime.now(timezone.utc)


class Document(Base):
    """Document metadata model stored in relational database (Section 12.1)."""

    __tablename__ = "documents"

    document_id = Column(
        String(64),
        primary_key=True,
        index=True,
        default=generate_document_id,
    )
    filename = Column(String(255), nullable=False)
    storage_key = Column(String(255), nullable=False, unique=True)
    status = Column(
        String(32),
        nullable=False,
        default=DocumentStatus.PROCESSING.value,
    )
    filesize = Column(Integer, nullable=True, default=0)
    content_type = Column(String(128), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    def to_dict(self):
        """Convert model to dictionary representation."""
        return {
            "document_id": self.document_id,
            "filename": self.filename,
            "status": self.status,
            "filesize": self.filesize,
            "content_type": self.content_type,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
