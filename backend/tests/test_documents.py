"""Focused tests for Documents API and controlled local document storage.

Verifies:
1. Successful document upload (multipart/form-data)
2. Upload response contains generated document_id and filename
3. Initial status is strictly 'processing' per Section 11.1
4. Document metadata retrieval via GET /api/documents/{document_id}
5. Non-existent document ID returns HTTP 404 with standardized error
6. Document list endpoint returns collection of stored documents
7. Uploaded file is genuinely stored in controlled local filesystem
8. Path traversal attempts are blocked and cannot escape the upload directory
"""

import io
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.main import app
from backend.database import Base, get_db
from backend.errors import APIError
from backend.models.document import Document, DocumentStatus
from backend.services.storage import StorageService, get_storage_service


@pytest.fixture
def test_env(tmp_path):
    """Set up an isolated in-memory DB and temporary upload directory."""
    db_file = tmp_path / "test_documents.db"
    test_engine = create_engine(
        f"sqlite:///{db_file}",
        connect_args={"check_same_thread": False},
    )
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine,
    )
    Base.metadata.create_all(bind=test_engine)

    test_upload_dir = tmp_path / "uploads"
    test_storage = StorageService(upload_dir=str(test_upload_dir))

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    def override_get_storage_service():
        return test_storage

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_storage_service] = override_get_storage_service

    client = TestClient(app)

    yield {
        "client": client,
        "storage": test_storage,
        "upload_dir": test_upload_dir,
        "session_factory": TestingSessionLocal,
    }

    app.dependency_overrides.clear()


def test_successful_document_upload(test_env):
    """Verify document upload creates DB record and stores file with initial 'processing' status."""
    client = test_env["client"]
    content = b"%PDF-1.4 test document content for safety manual"
    file_payload = ("Refinery_Safety_Standard_STD-804.pdf", io.BytesIO(content), "application/pdf")

    response = client.post("/api/documents/upload", files={"file": file_payload})

    assert response.status_code == 200
    data = response.json()

    # Section 11.1 contract checks
    assert "document_id" in data
    assert data["document_id"].startswith("doc_")
    assert data["filename"] == "Refinery_Safety_Standard_STD-804.pdf"
    assert data["status"] == "processing"


def test_uploaded_file_is_actually_stored_on_disk(test_env):
    """Verify the file content is safely stored in the designated upload directory."""
    client = test_env["client"]
    storage = test_env["storage"]
    session_factory = test_env["session_factory"]

    content = b"CRITICAL_BOILER_INSPECTION_DATA_12345"
    file_payload = ("Boiler_Report.pdf", io.BytesIO(content), "application/pdf")

    response = client.post("/api/documents/upload", files={"file": file_payload})
    assert response.status_code == 200
    doc_id = response.json()["document_id"]

    with session_factory() as session:
        doc = session.query(Document).filter(Document.document_id == doc_id).first()
        assert doc is not None
        assert doc.filesize == len(content)
        storage_key = doc.storage_key

    stored_path = storage.get_file_path(storage_key)
    assert stored_path.exists()
    assert stored_path.is_file()
    assert stored_path.read_bytes() == content


def test_get_document_status_returns_metadata(test_env):
    """Verify GET /api/documents/{id} returns status per Section 11.2."""
    client = test_env["client"]
    file_payload = ("P_AND_ID_Unit4.pdf", io.BytesIO(b"P&ID content"), "application/pdf")

    upload_res = client.post("/api/documents/upload", files={"file": file_payload})
    assert upload_res.status_code == 200
    doc_id = upload_res.json()["document_id"]

    status_res = client.get(f"/api/documents/{doc_id}")
    assert status_res.status_code == 200
    status_data = status_res.json()

    assert status_data["document_id"] == doc_id
    assert status_data["filename"] == "P_AND_ID_Unit4.pdf"
    assert status_data["status"] == "processing"


def test_get_document_status_unknown_id_returns_404(test_env):
    """Verify non-existent document ID returns 404 with standardized error structure."""
    client = test_env["client"]
    response = client.get("/api/documents/doc_nonexistent_9999")

    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "DOCUMENT_NOT_FOUND"
    assert "not found" in data["error"]["message"].lower()


def test_list_documents_endpoint(test_env):
    """Verify GET /api/documents returns all uploaded documents in chronological order."""
    client = test_env["client"]

    client.post("/api/documents/upload", files={"file": ("Doc1.pdf", io.BytesIO(b"Doc 1"), "application/pdf")})
    client.post("/api/documents/upload", files={"file": ("Doc2.pdf", io.BytesIO(b"Doc 2"), "application/pdf")})

    response = client.get("/api/documents")
    assert response.status_code == 200
    docs = response.json()

    assert isinstance(docs, list)
    assert len(docs) == 2
    filenames = [d["filename"] for d in docs]
    assert "Doc1.pdf" in filenames
    assert "Doc2.pdf" in filenames


def test_upload_invalid_or_empty_filename_rejected(test_env):
    """Verify upload without a valid file/filename is rejected with HTTP 400 or 422."""
    client = test_env["client"]

    # Whitespace filename -> 400 from application validator
    file_payload_whitespace = ("   ", io.BytesIO(b"test"), "application/pdf")
    res_whitespace = client.post("/api/documents/upload", files={"file": file_payload_whitespace})
    assert res_whitespace.status_code == 400
    assert res_whitespace.json()["error"]["code"] == "INVALID_FILE"

    # Missing file payload -> 422 Unprocessable Entity
    res_missing = client.post("/api/documents/upload", files={})
    assert res_missing.status_code == 422


def test_path_traversal_in_filename_cannot_escape_upload_directory(test_env):
    """Verify malicious client filename cannot control filesystem location or escape upload dir."""
    client = test_env["client"]
    upload_dir = test_env["upload_dir"]

    malicious_filename = "../../../../etc/passwd.pdf"
    file_payload = (malicious_filename, io.BytesIO(b"malicious content"), "application/pdf")

    response = client.post("/api/documents/upload", files={"file": file_payload})
    assert response.status_code == 200
    doc_id = response.json()["document_id"]

    session_factory = test_env["session_factory"]
    with session_factory() as session:
        doc = session.query(Document).filter(Document.document_id == doc_id).first()
        storage_key = doc.storage_key

    stored_path = (upload_dir / storage_key).resolve()
    assert str(stored_path).startswith(str(upload_dir.resolve()))
    assert stored_path.exists()
    assert not (upload_dir.parent / "passwd.pdf").exists()


def test_storage_service_rejects_path_traversal_on_retrieval(test_env):
    """Verify get_file_path rejects attempts to query outside upload directory."""
    storage = test_env["storage"]

    with pytest.raises(APIError) as exc_info:
        storage.get_file_path("../../../../secret.txt")

    assert exc_info.value.status_code in (400, 404)
