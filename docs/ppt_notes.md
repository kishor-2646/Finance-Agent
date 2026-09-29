# PPT Notes

## Slide 1 — Title
- **Finance Agent: Your AI-Powered Money Manager**
- Team members & date
- Track B — AI Agent for Personal Finance

## Slide 2 — Problem
- Manual expense tracking is error-prone and tedious
- UPI payments (GPay, PhonePe, Paytm) generate screenshots but no structured data
- Users lack actionable spending insights from their payment history

## Slide 3 — Solution
- Upload a payment screenshot → get structured expense data instantly
- AI-powered extraction using Google Gemini Vision
- Automatic categorisation into Food, Transport, Shopping, Bills, etc.

## Slide 4 — Architecture (Current)
- **Backend:** FastAPI (Python 3.13) with Uvicorn
- **AI:** Google Gemini `gemini-3.8-flash` — multimodal vision model
- **Image handling:** Pillow for validation & decoding
- **Flow:** Screenshot → `POST /extract` → Gemini Vision → Structured JSON

## Slide 5 — Demo
- Show Swagger UI at `localhost:8000/docs`
- Upload a GPay/PhonePe screenshot via the `/extract` endpoint
- Show the JSON response: `date`, `amount`, `merchant`, `category`, `payment_app`
- Highlight that it handles multiple UPI apps and receipt formats

## Slide 6 — Technical Highlights
- **Prompt engineering:** Strict JSON-only output with predefined keys and categories
- **`response_mime_type: "application/json"`** forces clean parseable output from Gemini
- **Error handling:** Validates image type, catches unreadable images, handles API failures
- **Model selection:** Verified with `check_keys.py`; base `gemini-3.8-flash` (not TTS variant)

## Slide 7 — Week 1 Progress
- ✅ Project scaffold with monorepo structure
- ✅ FastAPI backend with CORS, health check
- ✅ `POST /extract` endpoint — image in, JSON out
- ✅ Gemini 3.8 Flash integration working
- ✅ `.env` workflow with `.env.example` for team collaboration
- 🔲 Accuracy measurement on test set (next)
- 🔲 Rule-based categorisation fallback (next)

## Slide 8 — Roadmap
- **Week 2:** PostgreSQL database, auth, Next.js UI, first deployment
- **Week 3:** RAG-based financial advice from books
- **Week 4:** Spending analysis, budgets, Splitwise, dashboard
- **Week 5:** Anomaly detection, financial health score
- **Week 6:** Multi-guru comparison, predictive modelling
- **Week 7:** Testing, security, UX polish
- **Week 8:** Documentation, blog, demo recording
