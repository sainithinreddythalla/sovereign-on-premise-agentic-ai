"""Pydantic schemas for Document API contracts.

Conforms to Section 11.1 and 11.2 of PROJECT_SPEC.md.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from backend.models.document import DocumentStatus


class DocumentUploadResponse(BaseModel):
    """Response payload for POST /api/documents/upload (Section 11.1)."""
    document_id: str = Field(..., description="Unique generated document identifier")
    filename: str = Field(..., description="Original name of the uploaded file")
    status: DocumentStatus = Field(
        default=DocumentStatus.PROCESSING,
        description="Initial document processing status",
    )


class DocumentStatusResponse(BaseModel):
    """Response payload for GET /api/documents/{document_id} (Section 11.2)."""
    document_id: str = Field(..., description="Unique document identifier")
    filename: str = Field(..., description="Original name of the document")
    status: DocumentStatus = Field(..., description="Current processing status")


class DocumentItemResponse(BaseModel):
    """Item representation for GET /api/documents list endpoint."""
    document_id: str
    filename: str
    status: str
    filesize: Optional[int] = 0
    content_type: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
