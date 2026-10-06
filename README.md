# Finance Agent

An AI-powered personal finance assistant that extracts transaction data from payment screenshots (UPI/GPay/PhonePe/Paytm) using Google Gemini, with a FastAPI backend and Next.js frontend.

## Current Progress

| Milestone | Status |
|---|---|
| Repo scaffold & project structure | ✅ Done |
| FastAPI backend with CORS & health endpoint | ✅ Done |
| Gemini integration (`gemini-3.8-flash`) | ✅ Done |
| `POST /extract` — image → structured JSON | ✅ Done |
| API key verification script (`check_keys.py`) | ✅ Done |
| `.env` / `.env.example` setup | ✅ Done |
| Test screenshot collection (`data/screenshots/`) | ✅ Done (15 screenshots) |
| Ground-truth CSV (`data/expected.csv`) | ✅ Done (15 labelled rows) |
| Extraction accuracy script (`backend/evaluate.py`) | ✅ Done |
| Extraction accuracy measurement (run results) | 🔲 In progress (Week 1) |
| Rule-based categorisation | 🔲 Planned (Week 1) |
| Database, auth & UI | 🔲 Planned (Week 2) |
| Cloud deployment | 🔲 Planned (Week 2) |

## Project Structure

```
finance-agent/
├── .env.example              # Template — copy to .env and add your Gemini key
├── .gitignore
├── README.md
├── Roadmap.md                # Week-by-week plan
├── backend/
│   ├── .venv/                # Python virtual environment (git-ignored)
│   ├── main.py               # FastAPI app with /health and /extract endpoints
│   ├── evaluate.py           # Accuracy evaluation script (runs against expected.csv)
│   ├── check_keys.py         # Verifies Gemini API key & lists available models
│   ├── requirements.txt      # Frozen pip dependencies
│   └── app/
│       ├── __init__.py
│       └── main.py           # Original scaffold (to be merged later)
├── data/
│   ├── screenshots/          # 15 mock/redacted payment screenshots (ss01–ss15.jpeg)
│   ├── expected.csv          # Ground-truth labels for all 15 screenshots
│   └── sample_transactions.csv
├── docs/
│   ├── architecture.md       # System overview & data-flow diagram
│   ├── blog.md               # Blog post draft
│   └── ppt_notes.md          # Slide-by-slide presentation notes
└── frontend/
    ├── package.json          # Next.js 14 + Tailwind 3
    ├── next.config.js
    ├── tailwind.config.js
    ├── postcss.config.js
    └── app/
        ├── globals.css
        ├── layout.js
        └── page.js
```

## Getting Started

### 1. Clone & configure

```bash
git clone <your-repo-url>
cd finance-agent
cp .env.example .env
# Open .env and paste your Gemini API key from https://aistudio.google.com
```

### 2. Backend setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Verify your API key

```bash
python check_keys.py
```

This prints all models your key can access. Confirm `gemini-3.8-flash` is in the list.

### 4. Run the backend

```bash
uvicorn main:app --reload
```

Open http://localhost:8000/docs to test the API interactively.

### 5. Test the `/extract` endpoint

Upload a payment screenshot via the Swagger UI at `/docs`. The API returns structured JSON:

### 6. Run the accuracy evaluation

```bash
# Make sure the backend is running (uvicorn main:app --reload)
python evaluate.py
```

This sends each of the 15 screenshots in `data/screenshots/` to `/extract`, compares the
result against `data/expected.csv`, and prints per-field accuracy (date, amount, merchant, category).

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

### 7. Frontend (coming in Week 2)

```bash
cd frontend
npm install
npm run dev
```

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.13, FastAPI, Uvicorn |
| AI/Vision | Google Gemini API (`gemini-3.8-flash`) |
| Image processing | Pillow |
| Frontend | Next.js 14, Tailwind CSS |
| Deployment | Vercel (frontend), Railway/Render (backend) — planned |

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/extract` | Upload payment screenshot → structured JSON |

## License

MIT
