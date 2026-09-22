"""Standardized API Error definitions for SIH26117 Sovereign Industrial AI Workbench."""

from typing import Any, Optional
from pydantic import BaseModel


class APIErrorDetail(BaseModel):
    """Standardized error payload structure."""
    code: str
    message: str
    details: Optional[Any] = None


class APIErrorResponse(BaseModel):
    """Standardized error envelope."""
    error: APIErrorDetail


class APIError(Exception):
    """Base exception for application-level API errors."""

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: Optional[Any] = None,
    ):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details
        super().__init__(message)
