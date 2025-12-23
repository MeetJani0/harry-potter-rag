from google import genai
import os

def get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("❌ GEMINI_API_KEY not found. Check .env loading.")
    return genai.Client(api_key=api_key)