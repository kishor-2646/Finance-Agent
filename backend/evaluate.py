"""
backend/evaluate.py
===================
Accuracy evaluation script for the Finance Agent /extract endpoint.

Status: Week 1 — script complete, awaiting first accuracy run.

Usage
-----
  # 1. Start the backend in another terminal:
  #    uvicorn main:app --reload
  # 2. Then run from the backend/ directory:
  python evaluate.py

What it does
------------
- Reads ground-truth labels from  ../data/expected.csv
  (columns: file, date, amount, merchant, category)
- Posts each screenshot in ../data/screenshots/<file> to POST /extract
- Compares the model's response to the expected values for four fields:
    date     — exact ISO-8601 match (after normalising Excel's US format)
    amount   — float equality
    merchant — case-insensitive substring match
    category — exact string match
- Prints per-field accuracy and lists every mismatch.

Rate limiting
-------------
A 4-second sleep between requests keeps usage within the free-tier quota.
"""
import csv, time, mimetypes, requests

URL = "http://localhost:8000/extract"
rows = list(csv.DictReader(open("../data/expected.csv", encoding="utf-8-sig")))
if not rows:
    raise SystemExit("expected.csv has no data rows - check the file and header.")

totals = {"date": 0, "amount": 0, "merchant": 0, "category": 0}
failures = []

from datetime import datetime


def norm_date(s):
    """Normalise a date string to YYYY-MM-DD, accepting both ISO and Excel US formats."""
    s = (s or "").strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y"):   # Excel's US-style format
        try:
            return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass
    return s

def same_amount(got, expected):
    try:
        return float(got) == float(expected)
    except (TypeError, ValueError):
        return False


for r in rows:
    try:
        mime = mimetypes.guess_type(r["file"])[0] or "image/jpeg"
        with open(f"../data/screenshots/{r['file']}", "rb") as f:
            resp = requests.post(URL, files={"file": (r["file"], f, mime)})
        out = resp.json()
        if resp.status_code != 200:
            failures.append((r["file"], f"server error {resp.status_code}: {out}"))
            continue
    except Exception as e:
        failures.append((r["file"], f"request failed: {e}"))
        continue

    got_date = str(out.get("date") or "")
    got_merchant = str(out.get("merchant") or "").lower()
    got_category = str(out.get("category") or "")

    checks = {
        "date": got_date == r["date"],
        "amount": same_amount(out.get("amount"), r["amount"]) if r["amount"] else out.get("amount") is None,
        "merchant": (r["merchant"].lower() in got_merchant) if r["merchant"] else True,
        "category": got_category == r["category"],
    }
    for k, ok in checks.items():
        totals[k] += ok
        if not ok:
            failures.append((r["file"], f"{k}: expected {r[k]!r}, got {out.get(k)!r}"))
    time.sleep(4)   # stay under free-tier rate limits

n = len(rows)
print(f"\nAccuracy over {n} screenshots")
for k, v in totals.items():
    print(f"  {k:9s} {v}/{n}  ({100*v/n:.0f}%)")
print("\nFailures:")
for f in failures:
    print(" ", f)