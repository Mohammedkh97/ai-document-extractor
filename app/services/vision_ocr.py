"""
Vision OCR Service.
Supports OpenAI GPT-4o Vision and Google Gemini Vision for text extraction from images.
"""

import base64
from typing import Optional, Literal
from PIL import Image
import io

from openai import AsyncOpenAI
import google.generativeai as genai

from app.config import get_settings


class VisionOCRService:
    """
    Vision-based OCR service using cloud AI providers.
    Supports OpenAI GPT-4o and Google Gemini Vision APIs.
    """
    
    def __init__(
        self, 
        provider: Optional[Literal["openai", "gemini"]] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize Vision OCR service.
        
        Args:
            provider: OCR provider ("openai" or "gemini")
            api_key: API key (uses environment variable if not provided)
        """
        settings = get_settings()
        self.provider = provider or settings.ocr_provider
        
        if self.provider == "openai":
            self.api_key = api_key or settings.openai_api_key
            self.client = AsyncOpenAI(api_key=self.api_key)
            self.model = settings.llm_model if "gpt" in settings.llm_model else "gpt-4o"
        else:
            self.api_key = api_key or settings.gemini_api_key
            genai.configure(api_key=self.api_key)
            self.model = settings.llm_model if "gemini" in settings.llm_model else "gemini-1.5-flash"
    
    async def extract_text(self, image_base64: str) -> str:
        """
        Extract text from an image using Vision API.
        
        Args:
            image_base64: Base64 encoded image string
            
        Returns:
            Extracted text from the image
        """
        if self.provider == "openai":
            return await self._openai_vision(image_base64)
        else:
            return await self._gemini_vision(image_base64)
    
    async def extract_text_from_pil(self, image: Image.Image) -> str:
        """
        Extract text from a PIL Image.
        
        Args:
            image: PIL Image object
            
        Returns:
            Extracted text from the image
        """
        # Convert PIL Image to base64
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        
        return await self.extract_text(image_base64)
    
    async def _openai_vision(self, image_base64: str) -> str:
        """
        Use OpenAI GPT-4o Vision to extract text from image.
        
        Args:
            image_base64: Base64 encoded image
            
        Returns:
            Extracted text
        """
        prompt = """You are an expert OCR system. Extract ALL text from this document image.
        
Instructions:
- Extract every piece of text visible in the image
- Preserve the structure and layout as much as possible
- Include all headers, labels, values, dates, numbers, and names
- Do not miss any text, no matter how small
- Return the extracted text in a clean, readable format

Extract the text now:"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_base64}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=4096,
                temperature=0.0
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            print(f"[ERROR] OpenAI Vision API error: {e}")
            raise
    
    async def _gemini_vision(self, image_base64: str) -> str:
        """
        Use Google Gemini Vision to extract text from image.
        
        Args:
            image_base64: Base64 encoded image
            
        Returns:
            Extracted text
        """
        prompt = """You are an expert OCR system. Extract ALL text from this document image.
        
Instructions:
- Extract every piece of text visible in the image
- Preserve the structure and layout as much as possible
- Include all headers, labels, values, dates, numbers, and names
- Do not miss any text, no matter how small
- Return the extracted text in a clean, readable format

Extract the text now:"""

        try:
            # Decode base64 to bytes for Gemini
            image_bytes = base64.b64decode(image_base64)
            
            model = genai.GenerativeModel(self.model)
            
            response = await model.generate_content_async(
                [
                    prompt,
                    {
                        "mime_type": "image/png",
                        "data": image_bytes
                    }
                ],
                generation_config=genai.types.GenerationConfig(
                    temperature=0.0,
                    max_output_tokens=4096
                )
            )
            
            return response.text or ""
        except Exception as e:
            print(f"[ERROR] Gemini Vision API error: {e}")
            raise


async def extract_text_from_image(
    image_base64: str, 
    provider: Optional[str] = None
) -> str:
    """
    Convenience function to extract text from an image.
    
    Args:
        image_base64: Base64 encoded image
        provider: OCR provider (optional, uses config default)
        
    Returns:
        Extracted text
    """
    service = VisionOCRService(provider=provider)
    return await service.extract_text(image_base64)
