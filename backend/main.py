"""
backend/main.py
===============
Finance Agent — FastAPI backend.

Status: Week 1 (IN PROGRESS)

Endpoints
---------
GET  /health   — liveness check
POST /extract  — accepts a payment screenshot (JPEG/PNG) and returns
                 structured JSON: {date, amount, currency, merchant,
                 payment_app, category, confidence}

Model
-----
Google Gemini 3.8 Flash (vision).  The prompt instructs the model to return
only JSON, handles year-missing screenshots via fix_year(), and coerces
list-wrapped responses to a single dict.

Next steps (Week 1)
-------------------
- Run evaluate.py against data/screenshots/ to measure accuracy.
- Add rule-based category overrides (Swiggy → Food, etc.).
"""
import io, json, os
from datetime import date, datetime

from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from PIL import Image
from categorizer import categorize

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
Today's date is TODAY.
Return ONLY JSON with these keys:
date (YYYY-MM-DD or null), year_visible (true or false), amount (number, no currency symbol), currency,
merchant (string or null), payment_app (string or null),
category (one of: Food, Groceries, Transport, Shopping, Bills, Entertainment,
Health, Personal Care, Education, Transfer, Other),
confidence (high, medium or low).

Rules:
- Set year_visible to false if the screenshot does not show a year (for example "02 Oct" or "May 14").
  In that case still return your best date; the server will correct the year.
- If the image is blurred or unclear, set unreadable fields to null and confidence to low. Do not guess.
- Supermarkets and kirana stores -> Groceries. Spas and salons -> Personal Care.
  Restaurants and food delivery -> Food. Payments to people -> Transfer.
- If the screen lists several transactions, extract only the main/top one."""


def fix_year(data: dict) -> dict:
    """If the screenshot shows no year, use the most recent past date with that day and month."""
    d = data.get("date")
    if d and data.get("year_visible") is False:
        try:
            parsed = datetime.strptime(d, "%Y-%m-%d").date()
            today = date.today()
            candidate = parsed.replace(year=today.year)
            if candidate > today:
                candidate = candidate.replace(year=today.year - 1)
            data["date"] = candidate.isoformat()
        except ValueError:
            pass  # e.g. Feb 29 in a non-leap year: keep the model's value
    data.pop("year_visible", None)
    return data


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

    prompt = PROMPT.replace("TODAY", date.today().isoformat())

    try:
        resp = client.models.generate_content(
            model=MODEL,
            contents=[prompt, img],
            config={"response_mime_type": "application/json"},
        )
        data = json.loads(resp.text)
        if isinstance(data, list):  # model sometimes wraps the result in a list
            data = data[0] if data else {}
        data = fix_year(data)
        data["category_model"] = data.get("category")  # keep the model's guess for comparison
        data["category"], data["category_source"] = categorize(data.get("merchant"), data.get("category"))
        return data
    except json.JSONDecodeError:
        raise HTTPException(502, "Model returned invalid JSON")
    except Exception as e:
        raise HTTPException(502, f"Extraction failed: {e}")