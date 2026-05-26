from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import models
from schemas.expenses import ExpenseCreate, ExpenseResponse
from services.security import get_current_user

router = APIRouter(
    prefix="/expenses",
    tags=["Expenses"]
)


@router.post("/", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(
        expense: ExpenseCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    room = db.query(models.Room).filter(models.Room.id == expense.room_id).first()
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Кімнату не знайдено")

    if room.status == "finished":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Кімната архівована. Додавання нових витрат заборонено."
        )

    new_expense = models.Expense(
        room_id=expense.room_id,
        payer_id=expense.payer_id,
        amount=expense.amount,
        description=expense.description
    )
    db.add(new_expense)
    db.flush()

    if not expense.split_between:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Список боржників не може бути порожнім")

    split_amount = round(expense.amount / len(expense.split_between), 2)

    for user_id in expense.split_between:
        split = models.ExpenseSplit(
            expense_id=new_expense.id,
            user_id=user_id,
            amount_owed=split_amount
        )
        db.add(split)

    db.commit()
    db.refresh(new_expense)

    return new_expense


@router.get("/{room_id}", response_model=List[ExpenseResponse])
def get_room_expenses(
        room_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    room_member = db.query(models.RoomMember).filter(
        models.RoomMember.room_id == room_id,
        models.RoomMember.user_id == current_user.id
    ).first()

    if not room_member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Ви не є учасником цієї кімнати")

    expenses = db.query(models.Expense).filter(models.Expense.room_id == room_id).all()
    return expenses