"""Endpoints for saving and reading expenses."""
import datetime as dt
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from categorizer import CATEGORIES
from db import Transaction, get_db

router = APIRouter(prefix="/expenses", tags=["expenses"])

DEMO_USER_ID = 1  # replaced by the logged-in user once auth is added


class ExpenseIn(BaseModel):
    """Matches what /extract returns, so the frontend can post it straight back after the user reviews it."""
    model_config = ConfigDict(populate_by_name=True)

    txn_date: Optional[dt.date] = Field(default=None, alias="date")
    amount: Optional[Decimal] = None
    currency: str = "INR"
    merchant: Optional[str] = None
    payment_app: Optional[str] = None
    category: str = "Other"
    category_source: Optional[str] = None
    confidence: Optional[str] = None
    source: str = "screenshot"

    @field_validator("category")
    @classmethod
    def valid_category(cls, v):
        if v not in CATEGORIES:
            raise ValueError(f"category must be one of {CATEGORIES}")
        return v


class ExpenseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    txn_date: dt.date
    amount: Decimal
    currency: str
    merchant: Optional[str]
    payment_app: Optional[str]
    category: str
    category_source: Optional[str]
    confidence: Optional[str]
    source: str


@router.post("", response_model=ExpenseOut, status_code=201)
def create_expense(
    item: ExpenseIn,
    force: bool = Query(False, description="Save even if an identical expense already exists"),
    db: Session = Depends(get_db),
):
    # An unreadable screenshot comes back with nulls; make the user fill them in first.
    if item.amount is None or item.txn_date is None:
        raise HTTPException(422, "amount and date are required - please fill in the missing values")
    if item.amount <= 0:
        raise HTTPException(422, "amount must be greater than zero")

    if not force:
        dup = db.scalar(
            select(Transaction).where(
                Transaction.user_id == DEMO_USER_ID,
                Transaction.txn_date == item.txn_date,
                Transaction.amount == item.amount,
                Transaction.merchant == item.merchant,
            )
        )
        if dup:
            raise HTTPException(409, f"Looks like a duplicate of expense #{dup.id}. Use ?force=true to save anyway.")

    row = Transaction(user_id=DEMO_USER_ID, **item.model_dump(exclude_none=False))
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("", response_model=list[ExpenseOut])
def list_expenses(
    category: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    stmt = select(Transaction).where(Transaction.user_id == DEMO_USER_ID)
    if category:
        stmt = stmt.where(Transaction.category == category)
    stmt = stmt.order_by(Transaction.txn_date.desc(), Transaction.id.desc()).limit(limit)
    return db.scalars(stmt).all()


@router.delete("/{expense_id}", status_code=204)
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    row = db.get(Transaction, expense_id)
    if not row or row.user_id != DEMO_USER_ID:
        raise HTTPException(404, "Expense not found")
    db.delete(row)
    db.commit()