"""Documents API router conforming to Section 11.1 and 11.2 of PROJECT_SPEC.md."""

from typing import List
from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.errors import APIError
from backend.models.document import Document, DocumentStatus, generate_document_id
from backend.schemas.document import (
    DocumentItemResponse,
    DocumentStatusResponse,
    DocumentUploadResponse,
)
from backend.services.storage import StorageService, get_storage_service

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=200,
    summary="Upload confidential document",
)
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    storage: StorageService = Depends(get_storage_service),
) -> DocumentUploadResponse:
    """
    Accept multipart/form-data upload of confidential documents (Section 11.1).

    Stores the file in controlled local storage and registers metadata with
    initial status 'processing'.
    """
    if not file or not file.filename or not file.filename.strip():
        raise APIError(
            status_code=400,
            code="INVALID_FILE",
            message="A valid file with a non-empty filename must be provided",
        )

    # Generate a unique, server-controlled document identifier
    doc_id = generate_document_id()

    try:
        # Securely stream file into controlled storage
        storage_key, filesize = storage.save_file(
            file_obj=file.file,
            original_filename=file.filename,
            document_id=doc_id,
        )
    except APIError:
        raise
    except Exception as exc:
        raise APIError(
            status_code=500,
            code="STORAGE_ERROR",
            message=f"Failed to store file: {str(exc)}",
        )

    # Persist document metadata record
    doc = Document(
        document_id=doc_id,
        filename=file.filename,
        storage_key=storage_key,
        status=DocumentStatus.PROCESSING.value,
        filesize=filesize,
        content_type=file.content_type,
    )

    db.add(doc)
    db.commit()
    db.refresh(doc)

    return DocumentUploadResponse(
        document_id=doc.document_id,
        filename=doc.filename,
        status=DocumentStatus(doc.status),
    )


@router.get(
    "/{document_id}",
    response_model=DocumentStatusResponse,
    summary="Get document processing status",
)
def get_document_status(
    document_id: str,
    db: Session = Depends(get_db),
) -> DocumentStatusResponse:
    """
    Retrieve document status by ID (Section 11.2).
    Returns 404 if document does not exist.
    """
    doc = db.query(Document).filter(Document.document_id == document_id).first()
    if not doc:
        raise APIError(
            status_code=404,
            code="DOCUMENT_NOT_FOUND",
            message=f"Document with ID '{document_id}' not found",
        )

    return DocumentStatusResponse(
        document_id=doc.document_id,
        filename=doc.filename,
        status=DocumentStatus(doc.status),
    )


@router.get(
    "",
    response_model=List[DocumentItemResponse],
    summary="List all uploaded documents",
)
def list_documents(
    db: Session = Depends(get_db),
) -> List[DocumentItemResponse]:
    """
    Retrieve all document metadata records for frontend display.
    """
    docs = db.query(Document).order_by(Document.created_at.desc()).all()
    return [
        DocumentItemResponse(
            document_id=doc.document_id,
            filename=doc.filename,
            status=doc.status,
            filesize=doc.filesize,
            content_type=doc.content_type,
            created_at=doc.created_at,
            updated_at=doc.updated_at,
        )
        for doc in docs
    ]
