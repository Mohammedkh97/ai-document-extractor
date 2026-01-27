"""
PDF handling service.
Downloads PDFs from URLs and converts them to images for OCR processing.
"""

import io
import base64
from typing import Optional, List, Tuple
import httpx
import fitz  # PyMuPDF
from PIL import Image


class PDFHandler:
    """Handles PDF download and image conversion."""
    
    def __init__(self, timeout: float = 30.0):
        """
        Initialize PDF handler.
        
        Args:
            timeout: HTTP request timeout in seconds
        """
        self.timeout = timeout
    
    async def download_pdf(self, url: str) -> Optional[bytes]:
        """
        Download a PDF from a URL.
        
        Args:
            url: URL of the PDF document
            
        Returns:
            PDF bytes or None if download fails
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout, verify=False) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.content
        except httpx.HTTPError as e:
            print(f"[ERROR] Failed to download PDF: {e}")
            return None
    
    def pdf_to_images(
        self, 
        pdf_bytes: bytes, 
        dpi: int = 300,
        max_pages: Optional[int] = None
    ) -> List[Image.Image]:
        """
        Convert PDF pages to PIL Images.
        
        Args:
            pdf_bytes: PDF file as bytes
            dpi: Resolution for image conversion
            max_pages: Maximum number of pages to convert (None for all)
            
        Returns:
            List of PIL Images
        """
        images = []
        try:
            pdf_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            
            num_pages = len(pdf_doc)
            if max_pages:
                num_pages = min(num_pages, max_pages)
            
            for page_num in range(num_pages):
                page = pdf_doc[page_num]
                pix = page.get_pixmap(dpi=dpi)
                img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
                images.append(img)
            
            pdf_doc.close()
            return images
            
        except Exception as e:
            print(f"[ERROR] Failed to convert PDF to images: {e}")
            return []
    
    def image_to_base64(self, image: Image.Image, format: str = "PNG") -> str:
        """
        Convert PIL Image to base64 string.
        
        Args:
            image: PIL Image
            format: Image format (PNG, JPEG, etc.)
            
        Returns:
            Base64 encoded string
        """
        buffer = io.BytesIO()
        image.save(buffer, format=format)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
    
    async def process_document(
        self, 
        url: str, 
        dpi: int = 300,
        max_pages: int = 1
    ) -> Tuple[List[Image.Image], List[str]]:
        """
        Download PDF and convert to images with base64 encoding.
        
        Args:
            url: URL of the PDF document
            dpi: Resolution for image conversion
            max_pages: Maximum pages to process
            
        Returns:
            Tuple of (PIL Images, base64 encoded strings)
        """
        pdf_bytes = await self.download_pdf(url)
        if not pdf_bytes:
            return [], []
        
        images = self.pdf_to_images(pdf_bytes, dpi=dpi, max_pages=max_pages)
        base64_images = [self.image_to_base64(img) for img in images]
        
        return images, base64_images
