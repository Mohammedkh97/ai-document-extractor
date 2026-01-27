import os
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path
import sys

# Add project root to python path
sys.path.append(str(Path(__file__).parent.parent))

def test_gemini():
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        print("[ERROR] GEMINI_API_KEY not found or is placeholder in .env")
        return

    print(f"Testing Gemini API Key: {api_key[:10]}...{api_key[-5:]}")
    
    genai.configure(api_key=api_key)
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Hello, is this API key working?")
        print("[SUCCESS] Gemini API is working!")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"[ERROR] Gemini API call failed: {e}")

if __name__ == "__main__":
    test_gemini()
