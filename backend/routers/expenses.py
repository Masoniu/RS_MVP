"""
File: routers/expenses.py

Router for group expense tracking, balance division, and expense history records.

Responsible for:
- registering group expenses and enforcing status validation on parent room instances
- dividing expense amounts equally among selected group members using static rounding thresholds
- retrieving full lists of expense records filtered by specific room identifiers
- managing cascaded deletion of individual expenses and their sub-split items inside active lifecycles
"""

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
def create_room_expense(
        expense: ExpenseCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    """
    Creates a room expense entry and generates distinct split records for specified participants.

    Args:
        expense (ExpenseCreate): Input schema holding financial metrics, descriptions, and user mappings.
        db (Session): Database engine session context manager.
        current_user (models.User): Authenticated user instance asserting access rights.

    Returns:
        models.Expense: The initialized database expense record populated with nested child arrays.

    Raises:
        HTTPException(404): If the parent room row identifier cannot be matched.
        HTTPException(400): If the target room instance parameter has already shifted to finished.
        HTTPException(422): If the target debtor participant sequence array contains zero records.
    """
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
    
    #Flush assigns a unique identity primary key to the model instance prior to final collection commits
    db.flush()

    if not expense.split_between:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Список боржників не може бути порожнім")

    #Enforce basic monetary rounding constraints across calculated subset values to guard precision scales
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
    """
    Fetches full lists of expenses recorded inside a room, restricted to authenticated participants.

    Args:
        room_id (int): Primary key mapping to the monitored parent room entity.
        db (Session): Database engine session operational line.
        current_user (models.User): Authenticated user session structure asserting read permissions.

    Returns:
        List[models.Expense]: Arrays of expense records matching targeted integer room keys.

    Raises:
        HTTPException(403): If the authenticated user profile fails group membership lookups.
    """
    #Database relationship query to assert group participant permissions before exposing financial scopes
    room_member = db.query(models.RoomMember).filter(
        models.RoomMember.room_id == room_id,
        models.RoomMember.user_id == current_user.id
    ).first()

    if not room_member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Ви не є учасником цієї кімнати")

    expenses = db.query(models.Expense).filter(models.Expense.room_id == room_id).all()
    return expenses


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
        expense_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    """
    Removes a target expense record and handles cascading deletion across mapped sub-split data tables.

    Args:
        expense_id (int): Primary database key reference identifying the candidate expense model.
        db (Session): Database connector transaction interface executor.
        current_user (models.User): Authenticated user instance conducting administrative edits.

    Returns:
        None: Returns an explicit empty structural confirmation indicator.

    Raises:
        HTTPException(404): If the selected entry cannot be resolved using unique primary index parameters.
        HTTPException(400): If structural mutations are blocked because the room is locked.
    """
    expense = db.query(models.Expense).filter(models.Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Витрату не знайдено")

    room = db.query(models.Room).filter(models.Room.id == expense.room_id).first()
    if room and room.status == "finished":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Кімната архівована. Видалення витрат заборонено."
        )

    #Explicit cleanup script sequence executing child record wipeouts before processing parent nodes
    db.query(models.ExpenseSplit).filter(models.ExpenseSplit.expense_id == expense_id).delete()

    db.delete(expense)
    db.commit()

    return None