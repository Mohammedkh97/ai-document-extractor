"""
Health check endpoints.
"""

from datetime import datetime
from fastapi import APIRouter

from app.config import get_settings
from app.schemas.responses import HealthResponse


router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.
    Returns service status, version, and configuration info.
    """
    settings = get_settings()
    
    return HealthResponse(
        status="healthy",
        version="2.0.0",
        timestamp=datetime.utcnow(),
        ocr_provider=settings.ocr_provider
    )


@router.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "AI Document Schema Extractor",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health"
    }
