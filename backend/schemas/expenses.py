from pydantic import BaseModel
from typing import List
from datetime import datetime

class ExpenseCreate(BaseModel):
    room_id: int
    payer_id: int
    amount: float
    description: str
    split_between: List[int]

class ExpenseSplitResponse(BaseModel):
    user_id: int
    amount_owed: float

    class Config:
        from_attributes = True

class ExpenseResponse(BaseModel):
    id: int
    room_id: int
    payer_id: int
    amount: float
    description: str
    created_at: datetime
    splits: List[ExpenseSplitResponse]

    class Config:
        from_attributes = True