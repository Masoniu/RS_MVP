"""
File: schemas/expenses.py

Pydantic schemas for tracking shared expenses and split distributions.
"""

from pydantic import BaseModel
from typing import List
from datetime import datetime

class ExpenseCreate(BaseModel):
    """Input schema for recording a new transaction shared among members."""

    room_id: int
    payer_id: int
    amount: float
    description: str
    split_between: List[int]

class ExpenseSplitResponse(BaseModel):
    """Calculated split balance breakdown for a specific room participant."""

    user_id: int
    amount_owed: float

    class Config:
        from_attributes = True

class ExpenseResponse(BaseModel):
    """Complete itemized representation of an expense row with member breakdowns."""

    id: int
    room_id: int
    payer_id: int
    amount: float
    description: str
    created_at: datetime
    splits: List[ExpenseSplitResponse]

    class Config:
        from_attributes = True

class SettlementResponse(BaseModel):
    """Optimized transfer record representing a single peer debt clearance transaction."""

    from_user: int
    to_user: int
    amount: float