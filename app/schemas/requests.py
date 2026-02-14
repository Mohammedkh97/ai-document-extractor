"""
API request schemas.
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional


class ExtractFromUrlRequest(BaseModel):
    """Request schema for extracting data from a document URL."""
    document_url: str = Field(
        ...,
        description="URL of the document (PDF) to extract data from",
        examples=["https://example.com/document.pdf"]
    )
    document_id: Optional[str] = Field(
        None,
        description="Optional document identifier for tracking"
    )
    frappe_doctype: Optional[str] = Field(
        None,
        description="Frappe DocType to update with extracted data"
    )
    frappe_docname: Optional[str] = Field(
        None,
        description="Frappe document name to update"
    )


class FrappeWebhookRequest(BaseModel):
    """Request schema for Frappe webhook events."""
    event: Optional[str] = Field(
        "on_change",
        description="Webhook event type (e.g., 'after_insert', 'on_update')"
    )
    doctype: str = Field(
        ...,
        description="Frappe DocType that triggered the webhook"
    )
    docname: str = Field(
        ...,
        validation_alias="name",
        description="Document name in Frappe"
    )
    document_url: Optional[str] = Field(
        None,
        description="URL of the attached document"
    )
    attachment_field: Optional[str] = Field(
        "document_file",
        description="Field name containing the attachment"
    )
