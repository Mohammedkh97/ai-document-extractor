"""
Frappe ERP API Client.
Handles communication with Frappe/ERPNext for document operations.
"""

from typing import Optional, Dict, Any, List
import httpx

from app.config import get_settings


class FrappeClient:
    """
    Client for interacting with Frappe ERP API.
    Supports fetching documents, updating DocTypes, and handling file attachments.
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None
    ):
        """
        Initialize Frappe client.
        
        Args:
            base_url: Frappe instance URL
            api_key: Frappe API key
            api_secret: Frappe API secret
        """
        settings = get_settings()
        self.base_url = (base_url or settings.frappe_url).rstrip("/")
        self.api_key = api_key or settings.frappe_api_key
        self.api_secret = api_secret or settings.frappe_api_secret
        
        self.headers = {
            "Authorization": f"token {self.api_key}:{self.api_secret}",
            "Content-Type": "application/json"
        }
    
    async def get_document(
        self, 
        doctype: str, 
        docname: str,
        fields: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch a document from Frappe.
        
        Args:
            doctype: Frappe DocType name
            docname: Document name
            fields: Optional list of fields to fetch
            
        Returns:
            Document data or None if not found
        """
        url = f"{self.base_url}/api/resource/{doctype}/{docname}"
        
        params = {}
        if fields:
            params["fields"] = json.dumps(fields)
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    url, 
                    headers=self.headers,
                    params=params
                )
                response.raise_for_status()
                return response.json().get("data")
        except httpx.HTTPError as e:
            print(f"[ERROR] Failed to fetch document: {e}")
            return None
    
    async def update_document(
        self,
        doctype: str,
        docname: str,
        data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update a document in Frappe.
        
        Args:
            doctype: Frappe DocType name
            docname: Document name
            data: Fields to update
            
        Returns:
            Updated document data or None if failed
        """
        url = f"{self.base_url}/api/resource/{doctype}/{docname}"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.put(
                    url,
                    headers=self.headers,
                    json=data
                )
                response.raise_for_status()
                return response.json().get("data")
        except httpx.HTTPError as e:
            print(f"[ERROR] Failed to update document: {e}")
            return None
    
    async def create_document(
        self,
        doctype: str,
        data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new document in Frappe.
        
        Args:
            doctype: Frappe DocType name
            data: Document fields
            
        Returns:
            Created document data or None if failed
        """
        url = f"{self.base_url}/api/resource/{doctype}"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=data
                )
                response.raise_for_status()
                return response.json().get("data")
        except httpx.HTTPError as e:
            print(f"[ERROR] Failed to create document: {e}")
            return None
    
    async def get_file_url(
        self,
        doctype: str,
        docname: str,
        field_name: str = "attachment"
    ) -> Optional[str]:
        """
        Get the URL of a file attachment from a Frappe document.
        
        Args:
            doctype: Frappe DocType name
            docname: Document name
            field_name: Field containing the file attachment
            
        Returns:
            Full URL to the file or None
        """
        doc = await self.get_document(doctype, docname, fields=[field_name])
        if not doc:
            return None
        
        file_path = doc.get(field_name)
        if not file_path:
            return None
        
        # Handle both public and private files
        if file_path.startswith("/"):
            return f"{self.base_url}{file_path}"
        elif file_path.startswith("http"):
            return file_path
        else:
            return f"{self.base_url}/files/{file_path}"
    
    async def call_method(
        self,
        method: str,
        args: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Call a whitelisted Frappe method.
        
        Args:
            method: Full method path (e.g., "frappe.client.get")
            args: Method arguments
            
        Returns:
            Method response or None if failed
        """
        url = f"{self.base_url}/api/method/{method}"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=args or {}
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            print(f"[ERROR] Failed to call method: {e}")
            return None
    
    async def search_documents(
        self,
        doctype: str,
        filters: Optional[Dict[str, Any]] = None,
        fields: Optional[List[str]] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for documents in Frappe.
        
        Args:
            doctype: Frappe DocType name
            filters: Search filters
            fields: Fields to return
            limit: Maximum number of results
            
        Returns:
            List of matching documents
        """
        url = f"{self.base_url}/api/resource/{doctype}"
        
        params = {
            "limit_page_length": limit
        }
        
        if filters:
            params["filters"] = json.dumps(filters)
        if fields:
            params["fields"] = json.dumps(fields)
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params
                )
                response.raise_for_status()
                return response.json().get("data", [])
        except httpx.HTTPError as e:
            print(f"[ERROR] Failed to search documents: {e}")
            return []


# Import json at module level
import json
