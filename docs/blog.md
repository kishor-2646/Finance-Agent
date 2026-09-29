# Blog Draft

## Building an AI Finance Agent: Extracting Expenses from Payment Screenshots with Gemini

_Draft — updated after Week 1 implementation_

### Introduction

- **Problem:** Tracking personal expenses is tedious. Most people pay via UPI apps (GPay, PhonePe, Paytm) and forget the details within hours. Manually entering every transaction into a spreadsheet doesn't scale.
- **Solution:** An AI agent that reads payment screenshots and automatically extracts structured transaction data — date, amount, merchant, and category — in seconds.

### Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.13, FastAPI, Uvicorn |
| AI/Vision | Google Gemini API (`gemini-3.8-flash`) |
| Image handling | Pillow (PIL) |
| Frontend | Next.js 14 + Tailwind CSS (coming Week 2) |

### What We Built in Week 1

1. **`POST /extract` endpoint** — upload a payment screenshot, get back structured JSON with `date`, `amount`, `currency`, `merchant`, `payment_app`, and `category`.
2. **Gemini Vision integration** — used `gemini-3.8-flash` with `response_mime_type: "application/json"` to force clean JSON output.
3. **Prompt engineering** — crafted a prompt that tells the model exactly what fields to extract and what categories to use, with `null` for anything not visible.

### How the Extraction Works

```python
PROMPT = """You are reading a screenshot of a payment (UPI/GPay/PhonePe/Paytm) or a receipt.
Return ONLY JSON with these keys:
date (YYYY-MM-DD or null), amount (number, no currency symbol), currency,
merchant (string or null), payment_app (string or null),
category (one of: Food, Transport, Shopping, Bills, Entertainment, Health,
Education, Transfer, Other).
If a field is not visible, use null. Do not guess."""

resp = client.models.generate_content(
    model="gemini-3.8-flash",
    contents=[PROMPT, img],
    config={"response_mime_type": "application/json"},
)
```

The key insight: setting `response_mime_type` to `"application/json"` forces Gemini to return parseable JSON instead of wrapping it in markdown code blocks.

### Sample Output

Uploading a Google Pay screenshot returns:

```json
{
  "date": "2026-09-15",
  "amount": 249.0,
  "currency": "INR",
  "merchant": "Swiggy",
  "payment_app": "Google Pay",
  "category": "Food"
}
```

### Challenges & Lessons

- **Model selection matters:** `gemini-3.8-flash-tts` (TTS variant) doesn't support image input. You need the base `gemini-3.8-flash` model.
- **Model deprecation:** `gemini-2.5-flash` was deprecated during development — always check model availability with `check_keys.py` before coding against a specific model.
- **Prompt precision:** Being explicit about "no currency symbol" and "YYYY-MM-DD or null" dramatically improved output consistency.

### What's Next

- Measure extraction accuracy across 15-20 test screenshots
- Add rule-based categorisation fallback (Swiggy → Food, Uber → Transport)
- Build the frontend upload UI and expense table
- Deploy to Vercel + Railway

### Coming Soon

- Full blog post with accuracy benchmarks and architecture deep-dive
