"""
Document Extractor Service.
Uses LLM to extract structured data from OCR text based on document schemas.
"""

import json
from typing import Optional, Dict, Any

from openai import AsyncOpenAI
import google.generativeai as genai

from app.config import get_settings
from app.schemas.documents import (
    DocumentSchema, 
    DocumentType,
    DOCUMENT_TYPE_FIELD_MAP
)


# Schema extraction prompt template
EXTRACTION_PROMPT = """You are an expert document data extraction system. 
Your task is to extract structured data from the provided OCR text and return it as valid JSON.

The document type could be one of the following:
- EMPLOYMENT CONTRACT FULL WORK
- eVisa - Tourism
- eVisa - Employment
- Residence
- Change Status
- Passport
- Healthcare Professional Registration Certificate
- Tenancy Contract

Based on the document type detected, extract the relevant fields:

**For Passport:**
- passport_number, name, date_of_birth, date_of_issue, date_of_expiry, profession, nationality, place_of_birth

**For Visa (Tourism or Employment):**
- issue_date, place_of_issue, valid_until, uid_number, full_name, nationality, place_of_birth, date_of_birth, passport_number, profession

**For Change Status:**
- uid_number, name, nationality, profession, passport_number, employer_name, residence_stamping_deadline

**For Employment Contract:**
- work_style, transaction_number, name, nationality, passport_number, date_of_birth, academic_qualification, contract_start, contract_end

**For Residence:**
- id_number, passport_number, name, profession, issue_date, expiry_date

**For Healthcare Professional Registration Certificate:**
- professional_name, dha_unique_id

**For Tenancy Contract:**
- tenant_name, property_no, start_date, end_date, license_no, registration_date, expiry_date

IMPORTANT:
- All dates should be in DD/MM/YYYY format
- Extract only the fields that are clearly visible in the document
- Use null for fields that cannot be found
- Return ONLY valid JSON, no additional text or explanation

Here is the OCR text from the document:

{ocr_text}

Return the extracted data as JSON with this structure:
{{
    "document_type": "<detected document type>",
    "<details_field>": {{
        // relevant fields based on document type
    }}
}}
"""


class DocumentExtractor:
    """
    Extracts structured data from OCR text using LLM.
    """
    
    def __init__(self, provider: Optional[str] = None):
        """
        Initialize document extractor.
        
        Args:
            provider: LLM provider ("openai" or "gemini")
        """
        settings = get_settings()
        self.provider = provider or settings.ocr_provider
        
        if self.provider == "openai":
            self.api_key = settings.openai_api_key
            self.client = AsyncOpenAI(api_key=self.api_key)
            self.model = settings.llm_model if "gpt" in settings.llm_model else "gpt-4o"
        else:
            self.api_key = settings.gemini_api_key
            genai.configure(api_key=self.api_key)
            self.model = settings.llm_model if "gemini" in settings.llm_model else "gemini-1.5-flash"
    
    async def extract(self, ocr_text: str) -> Dict[str, Any]:
        """
        Extract structured data from OCR text.
        
        Args:
            ocr_text: Text extracted from document via OCR
            
        Returns:
            Dictionary with document_type and extracted data
        """
        prompt = EXTRACTION_PROMPT.format(ocr_text=ocr_text)
        
        if self.provider == "openai":
            return await self._openai_extract(prompt)
        else:
            return await self._gemini_extract(prompt)
    
    async def _openai_extract(self, prompt: str) -> Dict[str, Any]:
        """
        Use OpenAI to extract structured data.
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a document data extraction assistant. Always respond with valid JSON only."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2048,
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            return json.loads(content) if content else {}
            
        except Exception as e:
            print(f"[ERROR] OpenAI extraction error: {e}")
            raise
    
    async def _gemini_extract(self, prompt: str) -> Dict[str, Any]:
        """
        Use Gemini to extract structured data.
        """
        try:
            model = genai.GenerativeModel(self.model)
            
            response = await model.generate_content_async(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.0,
                    max_output_tokens=2048
                )
            )
            
            # Parse JSON from response
            text = response.text or ""
            # Clean up response if wrapped in code blocks
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            
            return json.loads(text.strip())
            
        except Exception as e:
            print(f"[ERROR] Gemini extraction error: {e}")
            raise
    
    def get_clean_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean extraction output to only include document_type and relevant details.
        
        Args:
            data: Raw extraction output
            
        Returns:
            Cleaned output with only relevant fields
        """
        doc_type_str = data.get("document_type") or ""
        
        # Find matching document type
        doc_type = None
        for dtype in DocumentType:
            if dtype.value.lower() in doc_type_str.lower():
                doc_type = dtype
                break
        
        if not doc_type:
            return {
                "document_type": "Unknown",
                "message": f"Unsupported or unknown document type: {doc_type_str}"
            }
        
        # Get the relevant field name
        field_name = DOCUMENT_TYPE_FIELD_MAP.get(doc_type)
        if not field_name:
            return {
                "document_type": doc_type.value,
                "message": "No field mapping for document type"
            }
        
        # Try to find the details in various possible key names
        possible_keys = [
            field_name,
            field_name.replace("_", ""),
            field_name.replace("_details", "Details"),
            "details"
        ]
        
        details = None
        for key in possible_keys:
            if key in data:
                details = data[key]
                break
        
        if not details:
            # Try to extract from nested structure
            for key, value in data.items():
                if isinstance(value, dict) and key != "document_type":
                    details = value
                    break
        
        return {
            "document_type": doc_type.value,
            field_name: details
        }
