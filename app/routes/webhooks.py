"""
Frappe webhook endpoints.
Handles incoming webhooks from Frappe ERP for document processing.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.schemas.requests import FrappeWebhookRequest
from app.schemas.responses import WebhookResponse, ExtractionResponse, FrappeUpdateResponse
from app.services.pdf_handler import PDFHandler
from app.services.vision_ocr import VisionOCRService
from app.services.extractor import DocumentExtractor
from app.services.frappe_client import FrappeClient


router = APIRouter()


async def process_document_and_update_frappe(
    document_url: str,
    doctype: str,
    docname: str,
    field_mapping: dict = None
):
    """
    Background task to process document and update Frappe.
    
    Args:
        document_url: URL of the document to process
        doctype: Frappe DocType to update
        docname: Document name to update
        field_mapping: Optional mapping from extraction fields to Frappe fields
    """
    try:
        # Process document
        pdf_handler = PDFHandler()
        images, base64_images = await pdf_handler.process_document(document_url, max_pages=1)
        
        if not base64_images:
            print(f"[ERROR] Failed to process document from {document_url}")
            return
        
        # Extract text
        ocr_service = VisionOCRService()
        ocr_text = await ocr_service.extract_text(base64_images[0])
        
        # Extract structured data
        extractor = DocumentExtractor()
        raw_data = await extractor.extract(ocr_text)
        clean_data = extractor.get_clean_output(raw_data)
        
        # Update Frappe
        frappe = FrappeClient()
        
        # Prepare update data
        update_data = {}
        
        # Get the details from extracted data
        for key, value in clean_data.items():
            if key != "document_type" and isinstance(value, dict):
                # Map extracted fields to Frappe fields
                if field_mapping:
                    for extract_field, frappe_field in field_mapping.items():
                        if extract_field in value:
                            update_data[frappe_field] = value[extract_field]
                else:
                    # Direct mapping (use same field names)
                    update_data.update(value)
        
        # Add document type
        update_data["document_type"] = clean_data.get("document_type", "Unknown")
        
        # Update Frappe document
        await frappe.update_document(doctype, docname, update_data)
        print(f"[INFO] Updated Frappe document {doctype}/{docname}")
        
    except Exception as e:
        print(f"[ERROR] Background task failed: {e}")


@router.post("/webhooks/frappe", response_model=WebhookResponse)
async def handle_frappe_webhook(
    request: FrappeWebhookRequest,
    background_tasks: BackgroundTasks
) -> WebhookResponse:
    """
    Handle incoming webhooks from Frappe ERP.
    
    This endpoint is called when a document is uploaded or updated in Frappe.
    It processes the document in the background and updates the Frappe record.
    
    Args:
        request: Webhook payload from Frappe
        background_tasks: FastAPI background tasks
        
    Returns:
        Webhook processing status
    """
    settings = get_settings()
    
    # Validate Frappe configuration
    if not settings.frappe_url or not settings.frappe_api_key:
        return WebhookResponse(
            success=False,
            message="Frappe integration not configured"
        )
    
    # Get document URL
    document_url = request.document_url
    
    if not document_url and request.attachment_field:
        # Fetch document URL from Frappe
        frappe = FrappeClient()
        document_url = await frappe.get_file_url(
            request.doctype,
            request.docname,
            request.attachment_field
        )
    
    if not document_url:
        return WebhookResponse(
            success=False,
            message="No document URL provided or found in Frappe"
        )
    
    # Process in background
    background_tasks.add_task(
        process_document_and_update_frappe,
        document_url,
        request.doctype,
        request.docname
    )
    
    return WebhookResponse(
        success=True,
        message=f"Document processing started for {request.doctype}/{request.docname}"
    )


@router.post("/webhooks/frappe/sync", response_model=WebhookResponse)
async def handle_frappe_webhook_sync(request: FrappeWebhookRequest) -> WebhookResponse:
    """
    Handle Frappe webhook synchronously (blocking).
    
    Use this endpoint when you need the extraction result immediately.
    For better performance, use the async endpoint `/webhooks/frappe`.
    
    Args:
        request: Webhook payload from Frappe
        
    Returns:
        Webhook processing result with extraction data
    """
    settings = get_settings()
    
    # Validate Frappe configuration
    if not settings.frappe_url or not settings.frappe_api_key:
        return WebhookResponse(
            success=False,
            message="Frappe integration not configured"
        )
    
    # Get document URL
    document_url = request.document_url
    
    if not document_url and request.attachment_field:
        frappe = FrappeClient()
        document_url = await frappe.get_file_url(
            request.doctype,
            request.docname,
            request.attachment_field
        )
    
    if not document_url:
        return WebhookResponse(
            success=False,
            message="No document URL provided or found"
        )
    
    try:
        # Process document
        pdf_handler = PDFHandler()
        images, base64_images = await pdf_handler.process_document(document_url, max_pages=1)
        
        if not base64_images:
            return WebhookResponse(
                success=False,
                message="Failed to process document"
            )
        
        # Extract text
        ocr_service = VisionOCRService()
        ocr_text = await ocr_service.extract_text(base64_images[0])
        
        # Extract structured data
        extractor = DocumentExtractor()
        raw_data = await extractor.extract(ocr_text)
        clean_data = extractor.get_clean_output(raw_data)
        
        # Update Frappe
        frappe = FrappeClient()
        
        # Prepare update data from extracted fields
        update_data = {"document_type": clean_data.get("document_type", "Unknown")}
        for key, value in clean_data.items():
            if key != "document_type" and isinstance(value, dict):
                update_data.update(value)
        
        await frappe.update_document(request.doctype, request.docname, update_data)
        
        return WebhookResponse(
            success=True,
            message="Document processed and Frappe updated",
            extraction_result=ExtractionResponse(
                success=True,
                data=clean_data
            ),
            frappe_update=FrappeUpdateResponse(
                success=True,
                doctype=request.doctype,
                docname=request.docname,
                updated_fields=update_data
            )
        )
        
    except Exception as e:
        return WebhookResponse(
            success=False,
            message=f"Processing failed: {str(e)}"
        )
