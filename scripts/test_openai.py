import os
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
import sys

# Add project root to python path
sys.path.append(str(Path(__file__).parent.parent))

def test_openai():
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        print("[ERROR] OPENAI_API_KEY not found in .env")
        return

    print(f"Testing OpenAI API Key: {api_key[:10]}...{api_key[-5:]}")
    
    client = OpenAI(api_key=api_key)
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello, is this API key working?"}],
            max_tokens=10
        )
        print("[SUCCESS] OpenAI API is working!")
        print(f"Response: {response.choices[0].message.content}")
    except Exception as e:
        print(f"[ERROR] OpenAI API call failed: {e}")

if __name__ == "__main__":
    test_openai()
