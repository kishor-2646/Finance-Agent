import io, json, os
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from PIL import Image

load_dotenv("../.env")

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-3.8-flash"  # must support image input (generateContent)

app = FastAPI(title="Finance Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

PROMPT = """You are reading a screenshot of a payment (UPI/GPay/PhonePe/Paytm) or a receipt.
Return ONLY JSON with these keys:
date (YYYY-MM-DD or null), amount (number, no currency symbol), currency,
merchant (string or null), payment_app (string or null),
category (one of: Food, Transport, Shopping, Bills, Entertainment, Health,
Education, Transfer, Other).
If a field is not visible, use null. Do not guess."""


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/extract")
async def extract(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(400, "Please upload an image file")

    try:
        img = Image.open(io.BytesIO(await file.read()))
    except Exception:
        raise HTTPException(400, "Could not read the image")

    try:
        resp = client.models.generate_content(
            model=MODEL,
            contents=[PROMPT, img],
            config={"response_mime_type": "application/json"},
        )
        return json.loads(resp.text)
    except json.JSONDecodeError:
        raise HTTPException(502, "Model returned invalid JSON")
    except Exception as e:
        raise HTTPException(502, f"Extraction failed: {e}")
