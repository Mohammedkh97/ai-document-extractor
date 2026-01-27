import asyncio
import os
import sys
from pathlib import Path

# Add project root to python path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.frappe_client import FrappeClient
from app.config import get_settings

async def check_connection():
    settings = get_settings()
    
    print(f"Checking connection to Frappe...")
    print(f"URL: {settings.frappe_url}")
    
    if not settings.frappe_api_key or settings.frappe_api_key == "your_frappe_api_key":
        print("\n[WARNING] Frappe API Key is not set in .env!")
        print("Please set FRAPPE_API_KEY and FRAPPE_API_SECRET in your .env file.")
        return

    client = FrappeClient()
    
    try:
        # Try to fetch current user info - a simple reliable test
        # 'User' doctype is standard
        print("Attempting to fetch current user info...")
        user_info = await client.call_method("frappe.auth.get_logged_user")
        
        if user_info:
            print("\n[SUCCESS] Connection Successful!")
            print(f"Connected as user: {user_info.get('message')}")
        else:
            print("\n[ERROR] Connection failed. No user info returned.")
            
    except Exception as e:
        print(f"\n[ERROR] Connection failed: {str(e)}")
        print("Please check your URL and API Keys.")

if __name__ == "__main__":
    asyncio.run(check_connection())
