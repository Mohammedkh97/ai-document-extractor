"""
API response schemas.
"""

from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from datetime import datetime

from app.schemas.documents import DocumentSchema


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    ocr_provider: str = Field(..., description="Active OCR provider")


class ExtractionResponse(BaseModel):
    """Response schema for document extraction."""
    success: bool = Field(..., description="Whether extraction was successful")
    document_id: Optional[str] = Field(None, description="Document identifier")
    data: Optional[DocumentSchema] = Field(None, description="Extracted document data")
    raw_text: Optional[str] = Field(None, description="Raw OCR text (if requested)")
    error: Optional[str] = Field(None, description="Error message if extraction failed")
    processing_time_ms: Optional[float] = Field(
        None, description="Processing time in milliseconds"
    )


class FrappeUpdateResponse(BaseModel):
    """Response for Frappe update operations."""
    success: bool = Field(..., description="Whether the update was successful")
    doctype: str = Field(..., description="Updated DocType")
    docname: str = Field(..., description="Updated document name")
    updated_fields: Optional[Dict[str, Any]] = Field(
        None, description="Fields that were updated"
    )
    error: Optional[str] = Field(None, description="Error message if update failed")


class WebhookResponse(BaseModel):
    """Response for webhook processing."""
    success: bool = Field(..., description="Whether webhook was processed successfully")
    message: str = Field(..., description="Processing result message")
    extraction_result: Optional[ExtractionResponse] = Field(
        None, description="Extraction result if document was processed"
    )
    frappe_update: Optional[FrappeUpdateResponse] = Field(
        None, description="Frappe update result if applicable"
    )


class ErrorResponse(BaseModel):
    """Standard error response."""
    success: bool = Field(default=False)
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
