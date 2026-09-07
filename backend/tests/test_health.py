"""Focused backend foundation tests for SIH26117 Sovereign Industrial AI Workbench.

Verifies:
1. Application imports successfully
2. Database and configuration foundation setup
3. GET /api/health returns HTTP 200 with valid JSON response
4. Configurable CORS handling
5. Standardized API error handling foundation
"""

import pytest
from fastapi.testclient import TestClient

from backend.main import app, APIError
from backend.config import get_settings
from backend.database import engine, SessionLocal, Base, get_db


@pytest.fixture
def client():
    """TestClient fixture with application lifespan triggered."""
    with TestClient(app) as test_client:
        yield test_client


def test_application_imports_successfully():
    """Verify that backend application and core components import without error."""
    assert app is not None
    settings = get_settings()
    assert settings.APP_NAME == "SIH26117 — Sovereign Industrial AI Workbench"
    assert settings.API_PREFIX == "/api"
    assert app.title == settings.APP_NAME


def test_database_foundation_setup():
    """Verify that SQLAlchemy engine, SessionLocal, and Base are initialized."""
    assert engine is not None
    assert SessionLocal is not None
    assert Base is not None

    # Verify session generator yields a valid session
    session_gen = get_db()
    session = next(session_gen)
    assert session is not None
    # Close session via generator cleanup
    with pytest.raises(StopIteration):
        next(session_gen)


def test_health_endpoint_returns_http_200_and_valid_json(client):
    """Verify GET /api/health returns HTTP 200 and expected JSON payload."""
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")

    data = response.json()
    assert isinstance(data, dict)
    assert data["status"] == "healthy"
    assert data["service"] == "sovereign-backend"
    assert "version" in data
    assert data["database"] == "connected"


def test_root_health_alias_endpoint(client):
    """Verify GET /health convenience alias returns identical valid status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_cors_preflight_for_frontend_origin(client):
    """Verify CORS preflight request from configured frontend origin is allowed."""
    response = client.options(
        "/api/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"


def test_standardized_api_error_handling(client):
    """Verify that raising APIError returns structured JSON with expected status."""
    # Temporarily register a test route raising APIError
    @app.get("/api/test-error", include_in_schema=False)
    def trigger_error():
        raise APIError(
            status_code=400,
            code="INVALID_PARAMETER",
            message="Test error message",
            details={"field": "test_param"},
        )

    response = client.get("/api/test-error")
    assert response.status_code == 400
    data = response.json()

    assert "error" in data
    assert data["error"]["code"] == "INVALID_PARAMETER"
    assert data["error"]["message"] == "Test error message"
    assert data["error"]["details"] == {"field": "test_param"}
