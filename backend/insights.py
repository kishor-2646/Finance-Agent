"""Spending summary (for the dashboard) and rule-based financial advice.

Advice is educational: it applies well-known budgeting principles to the user's
own spending. It is not investment advice.
"""
import datetime as dt
import re
from collections import defaultdict
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from db import Transaction, get_db
from expenses import DEMO_USER_ID

router = APIRouter(prefix="/insights", tags=["insights"])

# 50/30/20 buckets. Transfer and Other are counted in total spend but not classified.
NEEDS = {"Groceries", "Bills", "Transport", "Health", "Education"}
WANTS = {"Food", "Shopping", "Entertainment", "Personal Care"}

DISCLAIMER = (
    "This is general educational guidance based on your tracked spending, "
    "not personal investment or tax advice."
)


def _month_of(d: dt.date) -> str:
    return f"{d.year:04d}-{d.month:02d}"


def _load(db: Session):
    return db.execute(
        select(Transaction.txn_date, Transaction.amount, Transaction.category, Transaction.merchant)
        .where(Transaction.user_id == DEMO_USER_ID)
    ).all()


def _resolve_month(rows, month: Optional[str]) -> Optional[str]:
    if month:
        if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", month):
            raise HTTPException(422, "month must look like 2026-09")
        return month
    months = sorted({_month_of(r.txn_date) for r in rows})
    return months[-1] if months else None  # default: the latest month with data


def _f(x: Decimal) -> float:
    return round(float(x), 2)


@router.get("/summary")
def summary(month: Optional[str] = None, db: Session = Depends(get_db)):
    rows = _load(db)
    chosen = _resolve_month(rows, month)
    months = sorted({_month_of(r.txn_date) for r in rows})

    in_month = [r for r in rows if chosen and _month_of(r.txn_date) == chosen]
    total = sum((r.amount for r in in_month), Decimal(0))

    by_cat: dict[str, Decimal] = defaultdict(Decimal)
    for r in in_month:
        by_cat[r.category] += r.amount

    by_month: dict[str, Decimal] = defaultdict(Decimal)
    for r in rows:
        by_month[_month_of(r.txn_date)] += r.amount

    return {
        "month": chosen,
        "available_months": months,
        "total": _f(total),
        "count": len(in_month),
        "by_category": [
            {"category": c, "total": _f(v), "share": round(float(v / total * 100), 1) if total else 0}
            for c, v in sorted(by_cat.items(), key=lambda kv: kv[1], reverse=True)
        ],
        "by_month": [{"month": m, "total": _f(by_month[m])} for m in months],
    }


@router.get("/advice")
def advice(
    month: Optional[str] = None,
    income: Optional[float] = Query(None, gt=0, description="Monthly income in rupees (optional)"),
    db: Session = Depends(get_db),
):
    rows = _load(db)
    chosen = _resolve_month(rows, month)
    in_month = [r for r in rows if chosen and _month_of(r.txn_date) == chosen]

    if not in_month:
        return {
            "month": chosen,
            "tips": [{
                "id": "start",
                "principle": "Track first",
                "title": "Add some expenses",
                "message": "Upload a few payment screenshots or import a bank statement, and advice will appear here.",
            }],
            "disclaimer": DISCLAIMER,
        }

    total = sum((r.amount for r in in_month), Decimal(0))
    needs = sum((r.amount for r in in_month if r.category in NEEDS), Decimal(0))
    wants = sum((r.amount for r in in_month if r.category in WANTS), Decimal(0))
    by_cat: dict[str, Decimal] = defaultdict(Decimal)
    for r in in_month:
        by_cat[r.category] += r.amount
    top_cat, top_val = max(by_cat.items(), key=lambda kv: kv[1])
    biggest = max(in_month, key=lambda r: r.amount)

    tips = []

    if income:
        inc = Decimal(str(income))
        needs_pct = float(needs / inc * 100)
        wants_pct = float(wants / inc * 100)
        saved = inc - total
        save_pct = float(saved / inc * 100)

        if saved < 0:
            tips.append({
                "id": "overspend", "principle": "Spend less than you earn",
                "title": "Spending is above income",
                "message": f"Tracked spending (₹{_f(total):,.0f}) is more than your income (₹{income:,.0f}) this month. "
                           "Review the largest categories first for anything that can be reduced or delayed.",
            })
        elif save_pct < 20:
            tips.append({
                "id": "save_more", "principle": "Pay yourself first",
                "title": f"Savings rate is {save_pct:.0f}%",
                "message": "A common target is to save about 20% of income. Setting up an automatic transfer "
                           "on payday, before spending, makes this easier than saving what is left over.",
            })
        else:
            tips.append({
                "id": "saving_ok", "principle": "Pay yourself first",
                "title": f"Savings rate is {save_pct:.0f}%",
                "message": "You are at or above the common 20% target for this month. Keep it going.",
            })

        if wants_pct > 30:
            tips.append({
                "id": "wants_high", "principle": "50/30/20 budgeting rule",
                "title": f"Wants are {wants_pct:.0f}% of income",
                "message": "The 50/30/20 rule suggests keeping wants (eating out, shopping, entertainment, "
                           "personal care) to about 30%. Pick one category here to trim.",
            })
        if needs_pct > 50:
            tips.append({
                "id": "needs_high", "principle": "50/30/20 budgeting rule",
                "title": f"Needs are {needs_pct:.0f}% of income",
                "message": "Needs (groceries, bills, transport, health, education) are above the usual 50% guide. "
                           "Look for recurring bills you can renegotiate or switch.",
            })
    else:
        classified = needs + wants
        if classified > 0:
            wants_share = float(wants / classified * 100)
            if wants_share > 40:
                tips.append({
                    "id": "wants_share", "principle": "50/30/20 budgeting rule",
                    "title": f"Wants are {wants_share:.0f}% of classified spending",
                    "message": "Wants (eating out, shopping, entertainment, personal care) outweigh needs this month. "
                               "Check whether that matches your priorities.",
                })
        tips.append({
            "id": "add_income", "principle": "Know your numbers",
            "title": "Add your monthly income",
            "message": "Enter income above to see your savings rate and how you compare with the 50/30/20 guide.",
        })

    top_share = float(top_val / total * 100)
    if top_share >= 40 and len(by_cat) > 1:
        tips.append({
            "id": "top_category", "principle": "Look at your biggest category first",
            "title": f"{top_cat} is {top_share:.0f}% of spending",
            "message": f"One category dominates this month (₹{_f(top_val):,.0f}). Check whether it is a one-off "
                       "or a recurring cost, since recurring costs have the biggest long-term effect.",
        })

    big_share = float(biggest.amount / total * 100)
    if len(in_month) >= 3 and big_share >= 40:
        tips.append({
            "id": "big_payment", "principle": "Separate one-offs from habits",
            "title": "One payment is a large part of the month",
            "message": f"₹{_f(biggest.amount):,.0f} to {biggest.merchant or 'one payee'} is {big_share:.0f}% of this month's spending. "
                       "Treat large one-off payments separately when judging your regular budget.",
        })

    if needs > 0:
        tips.append({
            "id": "emergency_fund", "principle": "Emergency fund",
            "title": "Build an emergency fund",
            "message": f"A common guide is 3 to 6 months of essential expenses set aside. Based on this month's needs, "
                       f"that would be roughly ₹{_f(needs * 3):,.0f} to ₹{_f(needs * 6):,.0f}.",
        })

    return {
        "month": chosen,
        "total_spent": _f(total),
        "needs": _f(needs),
        "wants": _f(wants),
        "income": income,
        "tips": tips,
        "disclaimer": DISCLAIMER,
    }
