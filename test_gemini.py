
from dotenv import load_dotenv
from google import genai
import os

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
model = os.getenv("GEMINI_MODEL")

if not api_key:
    print("ERROR: API key not found")
    raise SystemExit(1)

print("Testing Gemini connection...")

client = genai.Client(api_key=api_key)

try:
    response = client.models.generate_content(
        model=model,
        contents="Reply with exactly: GEMINI WORKING"
    )
    print("SUCCESS:", response.text)

except Exception as e:
    print("FAILED:", type(e).__name__)
    print("ERROR:", str(e))
