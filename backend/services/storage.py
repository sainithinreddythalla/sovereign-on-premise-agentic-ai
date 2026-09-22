"""Controlled local file storage service for confidential industrial documents.

Conforms to Section 12.2 of PROJECT_SPEC.md.
"""

import os
from pathlib import Path
from typing import BinaryIO, Optional, Tuple
import uuid

from backend.config import get_settings
from backend.errors import APIError


class StorageService:
    """Manages secure, air-gapped local file storage separate from DB metadata."""

    def __init__(self, upload_dir: Optional[str] = None):
        settings = get_settings()
        self.upload_dir = Path(upload_dir or settings.UPLOAD_DIR).resolve()
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def _sanitize_extension(self, original_filename: str) -> str:
        """Extract and sanitize file extension, rejecting path traversal tokens."""
        base_name = Path(original_filename).name
        suffix = Path(base_name).suffix.lower()
        # Keep only alphanumeric characters and leading dot
        clean_ext = "".join(c for c in suffix if c.isalnum() or c == ".")
        if not clean_ext or len(clean_ext) > 10:
            return ".bin"
        if not clean_ext.startswith("."):
            return f".{clean_ext}"
        return clean_ext

    def save_file(
        self,
        file_obj: BinaryIO,
        original_filename: str,
        document_id: Optional[str] = None,
        chunk_size: int = 1024 * 1024,
    ) -> Tuple[str, int]:
        """
        Securely stream and save uploaded file into the controlled upload directory.

        Guarantees:
        - The stored filename is generated server-side and cannot be dictated by the client.
        - Path traversal sequences in original_filename are stripped and ignored.
        - Files are written in chunks to conserve memory for large engineering documents.

        Returns:
            Tuple[str, int]: (storage_key, bytes_written)
        """
        ext = self._sanitize_extension(original_filename)
        doc_prefix = document_id or f"doc_{uuid.uuid4().hex[:8]}"
        unique_token = uuid.uuid4().hex[:12]
        storage_key = f"{doc_prefix}_{unique_token}{ext}"

        # Resolve destination path and verify it stays strictly within upload_dir
        dest_path = (self.upload_dir / storage_key).resolve()
        if not str(dest_path).startswith(str(self.upload_dir)):
            raise APIError(
                status_code=400,
                code="SECURITY_VIOLATION",
                message="Path traversal attempt detected",
            )

        bytes_written = 0
        file_obj.seek(0)
        with open(dest_path, "wb") as buffer:
            while True:
                chunk = file_obj.read(chunk_size)
                if not chunk:
                    break
                buffer.write(chunk)
                bytes_written += len(chunk)

        return storage_key, bytes_written

    def get_file_path(self, storage_key: str) -> Path:
        """
        Resolve and validate the path for a stored file by storage key.
        Guarantees path traversal cannot escape the configured upload directory.
        """
        clean_key = Path(storage_key).name
        resolved_path = (self.upload_dir / clean_key).resolve()

        if not str(resolved_path).startswith(str(self.upload_dir)):
            raise APIError(
                status_code=400,
                code="SECURITY_VIOLATION",
                message="Access to path outside upload directory is forbidden",
            )

        if not resolved_path.exists() or not resolved_path.is_file():
            raise APIError(
                status_code=404,
                code="FILE_NOT_FOUND",
                message=f"Stored file '{clean_key}' not found",
            )

        return resolved_path

    def delete_file(self, storage_key: str) -> bool:
        """Delete a stored file safely if it exists."""
        try:
            path = self.get_file_path(storage_key)
            if path.exists():
                path.unlink()
                return True
        except APIError:
            pass
        return False


_storage_service: Optional[StorageService] = None


def get_storage_service() -> StorageService:
    """Dependency helper returning a StorageService instance."""
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service
