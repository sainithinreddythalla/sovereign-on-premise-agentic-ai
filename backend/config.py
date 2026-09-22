"""Configuration settings for SIH26117 Sovereign Industrial AI Workbench.

Values are environment-driven with sensible defaults for local development.
"""

import os
from functools import lru_cache
from typing import List


class Settings:
    """Application settings loaded from environment variables with local defaults."""

    APP_NAME: str = os.getenv("APP_NAME", "SIH26117 — Sovereign Industrial AI Workbench")
    APP_VERSION: str = os.getenv("APP_VERSION", "0.1.0")
    API_PREFIX: str = os.getenv("API_PREFIX", "/api")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")

    # Relational Database Configuration (SQLite default for sovereign local execution)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./sovereign_workbench.db")

    # CORS configuration for frontend integration
    # Accepts comma-separated URLs via CORS_ORIGINS env var
    _DEFAULT_CORS_ORIGINS = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", ",".join(_DEFAULT_CORS_ORIGINS))

    # Controlled local file storage paths (Section 12.2 of PROJECT_SPEC.md)
    DATA_DIR: str = os.getenv("DATA_DIR", "./data")
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./data/uploads")
    DELIVERABLES_DIR: str = os.getenv("DELIVERABLES_DIR", "./data/deliverables")

    @property
    def cors_origins_list(self) -> List[str]:
        """Return CORS origins as a list of trimmed strings."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache()
def get_settings() -> Settings:
    """Return a cached Settings singleton instance."""
    return Settings()
