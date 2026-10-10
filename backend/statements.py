"""Import expenses from a bank or UPI statement exported as CSV."""
import csv
import datetime as dt
import io
import re
from collections import Counter
from decimal import Decimal, InvalidOperation

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from categorizer import categorize
from db import Transaction, get_db
from expenses import DEMO_USER_ID

router = APIRouter(prefix="/statements", tags=["statements"])

MAX_BYTES = 2 * 1024 * 1024
MAX_ROWS = 5000

DATE_COLS = ["date", "txn date", "transaction date", "value date", "posting date"]
DESC_COLS = ["description", "narration", "merchant", "particulars", "details", "remarks", "transaction details"]
AMOUNT_COLS = ["amount", "amount (inr)", "amount (rs)", "txn amount", "transaction amount"]
DEBIT_COLS = ["debit", "withdrawal", "withdrawals", "withdrawal amt.", "withdrawal amount", "debit amount", "dr"]
CREDIT_COLS = ["credit", "deposit", "deposits", "deposit amt.", "deposit amount", "credit amount", "cr"]

# Day-first formats first: Indian bank statements are day/month/year.
DATE_FORMATS = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y", "%d-%m-%y",
                "%d %b %Y", "%d-%b-%Y", "%d %b %y", "%d-%b-%y", "%d %B %Y"]


def _find(headers: dict[str, str], names: list[str]):
    for n in names:
        if n in headers:
            return headers[n]
    return None


def parse_date(s: str):
    s = (s or "").strip()
    for fmt in DATE_FORMATS:
        try:
            return dt.datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    return None


def parse_amount(s):
    s = (s or "").strip()
    if not s:
        return None
    negative = s.startswith("-") or s.startswith("(") or s.lower().endswith("dr")
    cleaned = re.sub(r"[^\d.]", "", s)
    if not cleaned:
        return None
    try:
        value = Decimal(cleaned)
    except InvalidOperation:
        return None
    return -value if negative else value


@router.post("/import")
async def import_statement(file: UploadFile = File(...), db: Session = Depends(get_db)):
    raw = await file.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise HTTPException(413, "File is too large (limit 2 MB)")
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("latin-1")

    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        raise HTTPException(422, "The file is empty or has no header row")
    headers = {h.strip().lower(): h for h in reader.fieldnames if h}

    date_col = _find(headers, DATE_COLS)
    desc_col = _find(headers, DESC_COLS)
    amount_col = _find(headers, AMOUNT_COLS)
    debit_col = _find(headers, DEBIT_COLS)
    credit_col = _find(headers, CREDIT_COLS)
    if not date_col or not desc_col or not (amount_col or debit_col):
        raise HTTPException(
            422,
            "Could not find the needed columns. The header row needs a date column, a description/narration "
            f"column and an amount or debit column. Found: {list(reader.fieldnames)}",
        )

    rows = list(reader)
    if len(rows) > MAX_ROWS:
        raise HTTPException(413, f"Too many rows (limit {MAX_ROWS})")

    # With a single signed amount column, negative = money out, positive = money in.
    signed = False
    if amount_col and not debit_col:
        signed = any((parse_amount(r.get(amount_col)) or 0) < 0 for r in rows)

    existing = Counter(
        (t.txn_date, t.amount, t.merchant)
        for t in db.scalars(select(Transaction).where(Transaction.user_id == DEMO_USER_ID))
    )

    imported, duplicates, skipped_credits, invalid = 0, 0, 0, []
    for i, r in enumerate(rows, start=2):  # row 1 is the header
        d = parse_date(r.get(date_col))
        merchant = (r.get(desc_col) or "").strip()[:255] or None

        if debit_col:
            amt = parse_amount(r.get(debit_col))
            if amt is None or amt == 0:
                if credit_col and (parse_amount(r.get(credit_col)) or 0) > 0:
                    skipped_credits += 1
                    continue
                invalid.append(f"row {i}: no debit amount")
                continue
        else:
            amt = parse_amount(r.get(amount_col))
            if amt is None or amt == 0:
                invalid.append(f"row {i}: missing amount")
                continue
            if signed:
                if amt > 0:
                    skipped_credits += 1
                    continue
                amt = -amt
        amt = abs(amt).quantize(Decimal("0.01"))

        if d is None:
            invalid.append(f"row {i}: unreadable date {r.get(date_col)!r}")
            continue

        key = (d, amt, merchant)
        if existing[key] > 0:  # already saved earlier: skip, but keep genuine same-day repeats in one file
            existing[key] -= 1
            duplicates += 1
            continue

        category, source = categorize(merchant, None)
        db.add(Transaction(
            user_id=DEMO_USER_ID, txn_date=d, amount=amt, currency="INR", merchant=merchant,
            category=category, category_source=source, source="csv",
        ))
        imported += 1

    db.commit()
    return {
        "imported": imported,
        "skipped_duplicates": duplicates,
        "skipped_credits": skipped_credits,
        "invalid_rows": len(invalid),
        "invalid_examples": invalid[:10],
    }
