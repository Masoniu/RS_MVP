"""
File: models/expenses.py

ORM models for tracking expenses and their split distributions among room members.

Expense — Actual recorded transaction (who paid, how much, and for what).
ExpenseSplit — A specific member's share of that distinct expense.

Relationship: Expense 1 → N ExpenseSplit.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Expense(Base):
    """
    An expense entry recorded within a room.

    Attributes:
        id (int): Primary key.
        room_id (int): FK → rooms.id; the room associated with this expense.
        payer_id (int): FK → users.id; the user who physically paid the bill.
        amount (float): Total transaction cost in UAH.
        description (str): Short description (e.g., "Starbucks coffee").
        created_at (datetime): Timestamp when the entry was created (UTC).
        splits (list[ExpenseSplit]): ORM relationship linking to individual splits.
    """

    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    payer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Automatically drops child splits if the parent expense row is removed
    splits = relationship("ExpenseSplit", back_populates="expense", cascade="all, delete-orphan")


class ExpenseSplit(Base):
    """
    An individual member's shared portion of a single expense.

    Attributes:
        id (int): Primary key.
        expense_id (int): FK → expenses.id; the parent expense entity.
        user_id (int): FK → users.id; the debtor user who owes money.
        amount_owed (float): Owed portion in UAH (usually total amount / total split members).
        expense (Expense): Inverse ORM relationship linking back to the parent expense.
    """

    __tablename__ = "expense_splits"

    id = Column(Integer, primary_key=True, index=True)
    expense_id = Column(Integer, ForeignKey("expenses.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    amount_owed = Column(Float, nullable=False)

    expense = relationship("Expense", back_populates="splits")