"""
FastAPI Application Entry Point
AI Document Schema Extractor with Frappe ERP Integration
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routes import extract, webhooks, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Runs on startup and shutdown.
    """
    # Startup
    settings = get_settings()
    print(f"🚀 Starting AI Document Extractor")
    print(f"📡 OCR Provider: {settings.ocr_provider}")
    print(f"🤖 LLM Model: {settings.llm_model}")
    if settings.frappe_url:
        print(f"🔗 Frappe URL: {settings.frappe_url}")
    
    yield
    
    # Shutdown
    print("👋 Shutting down AI Document Extractor")


def create_app() -> FastAPI:
    """
    Application factory function.
    Creates and configures the FastAPI application.
    """
    settings = get_settings()
    
    app = FastAPI(
        title="AI Document Schema Extractor",
        description="Extract structured data from documents using OCR and LLM. Integrated with Frappe ERP.",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Register routers
    app.include_router(health.router, tags=["Health"])
    app.include_router(
        extract.router,
        prefix=settings.api_prefix,
        tags=["Document Extraction"]
    )
    app.include_router(
        webhooks.router,
        prefix=settings.api_prefix,
        tags=["Webhooks"]
    )
    
    return app


# Create application instance
app = create_app()
