# Architecture

## Overview

Finance Agent is a full-stack AI-powered personal finance assistant. It extracts structured transaction data from payment screenshots using Google Gemini's vision capabilities and returns categorised expense records.

## Current Architecture (Week 1)

```
                         ┌──────────────────────┐
                         │   Payment Screenshot  │
                         │  (GPay/PhonePe/Paytm) │
                         └──────────┬───────────┘
                                    │ image upload
                                    ▼
┌───────────┐   POST /extract   ┌──────────────────┐   generate_content   ┌─────────────────┐
│  Frontend  │ ───────────────► │  FastAPI Backend   │ ──────────────────► │  Gemini 3.8 Flash│
│ (Next.js)  │ ◄─────────────── │  (main.py)         │ ◄────────────────── │  (Vision LLM)    │
└───────────┘   structured JSON └──────────────────┘   JSON response      └─────────────────┘
                                        │
                                        ▼
                                ┌──────────────┐
                                │  Pillow (PIL) │
                                │ Image parsing │
                                └──────────────┘
```

## Components

### Backend — FastAPI (`backend/main.py`)

- **`GET /health`** — Returns `{"status": "ok"}` for uptime monitoring
- **`POST /extract`** — Accepts an image upload, sends it to Gemini with a structured prompt, returns categorised transaction JSON

### AI Layer — Google Gemini

- **Model:** `gemini-3.8-flash` (multimodal, supports image + text input)
- **Prompt strategy:** The model is given a strict prompt that forces JSON-only output with predefined keys: `date`, `amount`, `currency`, `merchant`, `payment_app`, `category`
- **Response format:** `response_mime_type: "application/json"` ensures the model returns parseable JSON
- **Categories:** Food, Transport, Shopping, Bills, Entertainment, Health, Education, Transfer, Other

### Image Processing — Pillow

- Validates uploaded files are actual images
- Opens and decodes the image bytes before passing to Gemini

### Configuration

- API keys stored in `.env` at the project root (git-ignored)
- `python-dotenv` loads the key at startup via `load_dotenv("../.env")`

## Extraction Output Schema

```json
{
  "date": "YYYY-MM-DD or null",
  "amount": 0.0,
  "currency": "INR",
  "merchant": "string or null",
  "payment_app": "string or null",
  "category": "Food | Transport | Shopping | Bills | Entertainment | Health | Education | Transfer | Other"
}
```

## Planned Architecture (Week 2+)

```
User ──► Next.js Frontend ──► FastAPI Backend ──► Gemini Vision LLM
                                    │
                                    ├──► PostgreSQL (users, transactions, budgets, goals)
                                    ├──► Vector Store / pgvector (RAG for financial advice)
                                    └──► Splitwise API (group expenses)
```

## Error Handling

| Scenario | HTTP Code | Response |
|---|---|---|
| Non-image file uploaded | 400 | `"Please upload an image file"` |
| Corrupted/unreadable image | 400 | `"Could not read the image"` |
| Gemini returns non-JSON | 502 | `"Model returned invalid JSON"` |
| Gemini API failure | 502 | `"Extraction failed: <details>"` |
