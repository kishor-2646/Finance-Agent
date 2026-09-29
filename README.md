# Finance Agent

An AI-powered finance agent with a FastAPI backend and Next.js frontend.

## Project Structure

```
finance-agent/
├── backend/        # FastAPI REST API
├── frontend/       # Next.js + Tailwind UI
├── data/           # Mock screenshots & sample CSVs
├── docs/           # Architecture, blog posts, PPT notes
└── README.md
```
```
Project full tree:

finance-agent/
├── README.md
├── backend/
│   ├── requirements.txt          # fastapi, uvicorn, pydantic
│   └── app/
│       ├── __init__.py
│       └── main.py               # FastAPI app with CORS & health endpoint
├── data/
│   ├── .gitkeep
│   └── sample_transactions.csv   # 10 mock transactions
├── docs/
│   ├── architecture.md           # System overview & data-flow diagram
│   ├── blog.md                   # Blog post draft
│   └── ppt_notes.md              # Slide-by-slide notes
└── frontend/
    ├── package.json              # Next.js 14 + Tailwind 3
    ├── next.config.js
    ├── tailwind.config.js
    ├── postcss.config.js
    └── app/
        ├── globals.css
        ├── layout.js
        └── page.js

```

## Getting Started

### Backend (FastAPI)

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend (Next.js + Tailwind)

```bash
cd frontend
npm install
npm run dev
```

## License

MIT
