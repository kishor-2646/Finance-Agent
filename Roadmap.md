Here is a single sequential flow for Track B. Each phase builds on the last, and each ends with a Sunday submission.

## Phase 0: Setup (before Week 1) ✅
1. ~~Attend the intro class and register your team with official email IDs.~~  ✅
2. ~~Read the project doc once and note the Track B grading: architecture 45, UI/UX 25, cloud deployment 20, code quality 15, presentation 15, bonus up to 15.~~ ✅
3. ~~Create one GitHub monorepo:~~ ✅
```
finance-agent/
  backend/    (FastAPI)
  frontend/   (Next.js + Tailwind)
  data/       (mock screenshots, sample CSVs)
  docs/       (architecture, blog, PPT notes)
  README.md
```
4. ~~Get API keys (LLM, Google Vision or Gemini, Splitwise) and keep them in `.env`, never in git.~~ ✅ Gemini API key configured
5. Collect 15-20 mock or redacted screenshots (GPay, PhonePe, Paytm) and 2-3 sample bank statement CSVs. This is your test set for the whole project. 🔲 In progress

## Week 1: Screenshot → structured expense (IN PROGRESS)
1. ~~Set up FastAPI with a health endpoint and CORS.~~ ✅
2. ~~Build `POST /extract`: image in, JSON out (`date, amount, merchant, category, payment_app`). Use a vision LLM first, with Tesseract + regex as a fallback.~~ ✅ Using Gemini 3.8 Flash
3. Measure extraction accuracy on your test set and log the failures. 🔲
4. Add rule-based categorization (Swiggy/Zomato → Food, Uber/Ola → Transport, and so on). 🔲
5. Add error handling for blurry images and unsupported formats. ✅ Basic validation done

**Sunday submission 1:** extraction working from the API, with a short demo clip.

## Week 2: Database, UI, first deploy
1. Design the PostgreSQL schema: `users`, `transactions`, `budgets`, `goals`.
2. Add basic auth and user management.
3. Build the Next.js pages: login, upload, expense table.
4. Add CSV and bank statement upload (SBI, HDFC, ICICI formats) through the same pipeline.
5. Add ML-based categorization for merchants your rules miss.
6. Deploy the frontend to Vercel and the backend to Railway or Render.
7. Add a basic advice endpoint with hardcoded principles (50/30/20, emergency fund).

**Sunday submission 2:** live deployment and the 2-minute demo the doc requires.

## Week 3: Financial advice from books (RAG)
1. Collect 3-5 finance sources (PDFs and articles) and extract text with PyPDF2.
2. Chunk the text, embed it, and store it in a vector store (pgvector keeps it in the same database).
3. Build the retrieval tool: question in, relevant passages plus source out.
4. Build the advice tool: user's spending summary plus retrieved passages goes to the LLM, which returns advice that cites the source.
5. Add a book/article upload feature in the UI.

**Sunday submission 3:** advice that references uploaded finance content.

## Week 4: Analysis, budgets, Splitwise
1. Build the spending analysis tool (category totals, monthly trends, top merchants) with pandas.
2. Build the budget recommendation tool and a goal-tracking tool (savings targets, progress).
3. Add Splitwise integration to pull group expenses and merge them into transactions.
4. Wire all three tools into the LangChain agent so it chooses which to call.
5. Build the dashboard: category chart, monthly trend, budget vs actual, using Chart.js.
6. Add the chat advisor UI.

**Sunday submission 4:** an agent that gives personalized advice from real spending data, with a dashboard.

## Week 5: Advanced analysis
1. Add anomaly detection (unusually large or unexpected transactions).
2. Add custom category learning, so the system learns from user corrections.
3. Build the financial health score (savings rate, budget adherence, spending stability) and explain how it is calculated.
4. Add Indian context: ELSS, PPF, SIP guidance, tax slabs, and deductions in the advice knowledge.

**Sunday submission 5:** anomaly alerts and the health score in the UI.

## Week 6: Advanced feature and reliability
1. Build the multi-guru comparison feature: the same user situation is analyzed through Buffett, Kiyosaki, Ramit Sethi and others, with differences shown side by side.
2. Add retries, timeouts, and fallbacks across all external APIs (OCR provider fallback, Splitwise failures).
3. Build the analytics dashboard with trends and insights, and add basic predictive modeling for next month's spending.

**Sunday submission 6:** guru comparison and a robust, error-tolerant system.

## Week 7: Quality and security
1. Write tests for extraction, categorization, and the agent tools.
2. Apply basic security: input validation, hashed passwords, per-user data isolation, secrets in environment variables only, HTTPS.
3. Optimize for larger datasets (pagination, indexes, caching).
4. Polish the UX: loading states, empty states, clear error messages, mobile responsiveness.
5. Add export (financial reports, budget plans, expense summaries).

**Sunday submission 7:** stable, tested, secure build.

## Week 8: Documentation and demo
1. Write the README (setup, API configuration, usage examples).
2. Write the architecture doc explaining the data flow and advisory pipeline.
3. Write the user documentation and financial planning guide.
4. Publish the technical blog post (Medium or LinkedIn), which is required for Track B.
5. Record the 8-10 minute demo using mock data only.
6. Rehearse the viva: OCR strategy, handling sensitive data, categorization and advice logic, contributions, future improvements.

**Sunday submission 8:** everything final.

## After the 2 months
1. Build a concise PPT from the guideline document that Capabl shares.
2. Submit it through the Final Submission Form before the deadline.
3. Prepare a 5-7 minute presentation on what you built, how it works, and real-world applicability.
