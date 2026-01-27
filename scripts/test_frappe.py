import os
import asyncio
from dotenv import load_dotenv
from pathlib import Path
import sys
import httpx

# Add project root to python path
sys.path.append(str(Path(__file__).parent.parent))

async def test_frappe():
    load_dotenv()
    
    url = os.getenv("FRAPPE_URL")
    api_key = os.getenv("FRAPPE_API_KEY")
    api_secret = os.getenv("FRAPPE_API_SECRET")
    
    if not url or url == "your_frappe_url_here":
        print("[ERROR] FRAPPE_URL not found in .env")
        return
    if not api_key or api_key == "your_frappe_api_key":
        print("[ERROR] FRAPPE_API_KEY not found in .env")
        return
    if not api_secret or api_secret == "your_frappe_api_secret":
        print("[ERROR] FRAPPE_API_SECRET not found in .env")
        return

    print(f"Testing Frappe connection to {url}")
    print(f"API Key: {api_key[:10]}...")
    
    headers = {
        "Authorization": f"token {api_key}:{api_secret}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    
    async with httpx.AsyncClient() as client:
        try:
            # Try to get current user
            response = await client.get(f"{url}/api/method/frappe.auth.get_logged_user", headers=headers)
            if response.status_code == 200:
                user = response.json().get("message")
                print(f"[SUCCESS] Frappe connection works! Logged in as: {user}")
            else:
                print(f"[ERROR] Frappe request failed with status {response.status_code}")
                print(f"Response: {response.text}")
        except Exception as e:
            print(f"[ERROR] Frappe connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_frappe())
