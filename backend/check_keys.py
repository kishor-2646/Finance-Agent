import os
from dotenv import load_dotenv
from google import genai

load_dotenv("../.env")

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Lists models your key can use, so you can pick a current one
for m in client.models.list():
    if "generateContent" in (m.supported_actions or []):
        print(m.name)
