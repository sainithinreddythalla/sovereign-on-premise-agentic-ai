"""FastAPI application entry point for SIH26117 Sovereign Industrial AI Workbench."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import get_settings
from backend.database import init_db
from backend.errors import APIError, APIErrorDetail, APIErrorResponse
# Import models to register with Base.metadata before database initialization
import backend.models  # noqa: F401
from backend.routers.documents import router as documents_router

settings = get_settings()


# ============================================================================
# Application Lifespan
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown management."""
    # Ensure controlled local storage directories exist per Section 12.2
    os.makedirs(settings.DATA_DIR, exist_ok=True)
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.DELIVERABLES_DIR, exist_ok=True)

    # Initialize relational database tables
    init_db()

    yield


# ============================================================================
# FastAPI Application Factory
# ============================================================================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# CORS middleware configured for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handler for standardized APIError
@app.exception_handler(APIError)
async def handle_api_error(request: Request, exc: APIError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


# ============================================================================
# Router Registration
# ============================================================================

app.include_router(documents_router, prefix=settings.API_PREFIX)


# ============================================================================
# Health Check Endpoints
# ============================================================================

@app.get("/api/health", tags=["System"])
def api_health_check():
    """Primary health check endpoint conforming to Section 11 API layout."""
    return {
        "status": "healthy",
        "service": "sovereign-backend",
        "version": settings.APP_VERSION,
        "database": "connected",
    }


@app.get("/health", tags=["System"], include_in_schema=False)
def root_health_check():
    """Convenience alias for standard container and infrastructure probes."""
    return api_health_check()
