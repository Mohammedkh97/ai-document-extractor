"""
Document extraction endpoints.
"""

import time
from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.schemas.requests import ExtractFromUrlRequest
from app.schemas.responses import ExtractionResponse
from app.services.pdf_handler import PDFHandler
from app.services.vision_ocr import VisionOCRService
from app.services.extractor import DocumentExtractor

router = APIRouter()

@router.post("/extract", response_model=ExtractionResponse)
async def extract_from_url(request: ExtractFromUrlRequest) -> ExtractionResponse:
    """
    Extract structured data from a document URL.
    
    Downloads the PDF, performs OCR using Vision AI, and extracts
    structured data using LLM.
    
    Args:
        request: Document URL and optional identifiers
        
    Returns:
        Extracted document data in structured format
    """
    start_time = time.time()
    settings = get_settings()
    
    try:
        # Step 1: Download PDF and convert to images
        pdf_handler = PDFHandler()
        images, base64_images = await pdf_handler.process_document(
            request.document_url,
            max_pages=1  # Process first page only for now
        )
        
        if not base64_images:
            return ExtractionResponse(
                success=False,
                document_id=request.document_id,
                error="Failed to download or process PDF document"
            )
        
        # Step 2: Extract text using Vision OCR
        ocr_service = VisionOCRService()
        ocr_text = await ocr_service.extract_text(base64_images[0])
        
        if not ocr_text:
            return ExtractionResponse(
                success=False,
                document_id=request.document_id,
                error="Failed to extract text from document"
            )
        
        # Step 3: Extract structured data using LLM
        extractor = DocumentExtractor()
        raw_data = await extractor.extract(ocr_text)
        clean_data = extractor.get_clean_output(raw_data)
        
        processing_time = (time.time() - start_time) * 1000
        
        return ExtractionResponse(
            success=True,
            document_id=request.document_id,
            data=clean_data,
            processing_time_ms=round(processing_time, 2)
        )
        
    except Exception as e:
        processing_time = (time.time() - start_time) * 1000
        return ExtractionResponse(
            success=False,
            document_id=request.document_id,
            error=str(e),
            processing_time_ms=round(processing_time, 2)
        )


@router.post("/extract/upload", response_model=ExtractionResponse)
async def extract_from_upload(
    file: UploadFile = File(..., description="PDF document to extract data from"),
    document_id: Optional[str] = Form(None, description="Optional document identifier")
) -> ExtractionResponse:
    """
    Extract structured data from an uploaded PDF file.
    
    Args:
        file: Uploaded PDF file
        document_id: Optional document identifier
        
    Returns:
        Extracted document data in structured format
    """
    start_time = time.time()
    
    # Validate file type
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        return ExtractionResponse(
            success=False,
            document_id=document_id,
            error="Only PDF files are supported"
        )
    
    try:
        # Read uploaded file
        pdf_bytes = await file.read()
        
        # Step 1: Convert PDF to images
        pdf_handler = PDFHandler()
        images = pdf_handler.pdf_to_images(pdf_bytes, max_pages=1)
        
        if not images:
            return ExtractionResponse(
                success=False,
                document_id=document_id,
                error="Failed to process PDF document"
            )
        
        # Step 2: Extract text using Vision OCR
        ocr_service = VisionOCRService()
        ocr_text = await ocr_service.extract_text_from_pil(images[0])
        
        if not ocr_text:
            return ExtractionResponse(
                success=False,
                document_id=document_id,
                error="Failed to extract text from document"
            )
        
        # Step 3: Extract structured data using LLM
        extractor = DocumentExtractor()
        raw_data = await extractor.extract(ocr_text)
        clean_data = extractor.get_clean_output(raw_data)
        
        processing_time = (time.time() - start_time) * 1000
        
        return ExtractionResponse(
            success=True,
            document_id=document_id,
            data=clean_data,
            processing_time_ms=round(processing_time, 2)
        )
        
    except Exception as e:
        processing_time = (time.time() - start_time) * 1000
        return ExtractionResponse(
            success=False,
            document_id=document_id,
            error=str(e),
            processing_time_ms=round(processing_time, 2)
        )


@router.post("/extract/text", response_model=ExtractionResponse)
async def extract_from_text(
    ocr_text: str = Form(..., description="Pre-extracted OCR text"),
    document_id: Optional[str] = Form(None, description="Optional document identifier")
) -> ExtractionResponse:
    """
    Extract structured data from pre-extracted OCR text.
    
    Use this endpoint if you already have OCR text and just need
    structured data extraction.
    
    Args:
        ocr_text: Pre-extracted text from document
        document_id: Optional document identifier
        
    Returns:
        Extracted document data in structured format
    """
    start_time = time.time()
    
    try:
        # Extract structured data using LLM
        extractor = DocumentExtractor()
        raw_data = await extractor.extract(ocr_text)
        clean_data = extractor.get_clean_output(raw_data)
        
        processing_time = (time.time() - start_time) * 1000
        
        return ExtractionResponse(
            success=True,
            document_id=document_id,
            data=clean_data,
            processing_time_ms=round(processing_time, 2)
        )
        
    except Exception as e:
        processing_time = (time.time() - start_time) * 1000
        return ExtractionResponse(
            success=False,
            document_id=document_id,
            error=str(e),
            processing_time_ms=round(processing_time, 2)
        )
