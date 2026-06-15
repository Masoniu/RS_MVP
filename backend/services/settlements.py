"""
File: services/settlements.py

Service for calculating balances and minimal debt settlements between room members.
 
Logic:
1. get_room_balances() — aggregates who paid how much and who owes how much,
   returning the net balance of each participant (positive = others owe them,
   negative = they owe others).
2. calculate_settlements() — greedy algorithm that minimises the number of
   transfers: the largest creditor and the largest debtor meet and settle debts
   until all balances are zeroed out.
"""
from sqlalchemy.orm import Session
from collections import defaultdict
import models


def get_room_balances(room_id: int, db: Session) -> dict[int, float]:
    """
    Compute the net financial balance of every participant in a room.
 
    For each expense:
      - the payer's balance is credited by the full expense amount (+)
      - each debtor listed in splits has their share deducted (-)
 
    Args:
        room_id (int): identifier of the room.
        db (Session): active SQLAlchemy session.
 
    Returns:
        dict[int, float]: mapping of {user_id: balance}.
            A positive value means that user is owed money.
            A negative value means that user owes money to others.
    """
    # defaultdict avoids manual key initialisation
    balances = defaultdict(float)

    expenses = db.query(models.Expense).filter(models.Expense.room_id == room_id).all()

    for exp in expenses:
        # Credit the payer with the full amount they covered
        balances[exp.payer_id] += exp.amount
        # Deduct each participant's share
        for split in exp.splits:
            balances[split.user_id] -= split.amount_owed

    return dict(balances)


def calculate_settlements(balances: dict[int, float]) -> list[dict]:
    """
    Compute the minimal set of money transfers needed to settle all debts.
 
    Uses a greedy algorithm:
      - sorts creditors (balance > 0) and debtors (balance < 0) in descending order
      - at each iteration the largest debtor pays the largest creditor
      - any remaining amount (if one side is not fully settled) is put back in the queue
 
    Threshold for ignoring amounts: 0.01 (prevents floating-point noise).
 
    Args:
        balances (dict[int, float]): net balances produced by get_room_balances().
 
    Returns:
        list[dict]: list of transfers in the format
            [{"from_user": int, "to_user": int, "amount": float}, ...]
            ordered from the largest transfer to the smallest.
    """
    # Creditors: (amount, user_id) sorted descending
    creditors = sorted([(v, k) for k, v in balances.items() if v > 0.01], reverse=True)
    # Debtors: (absolute debt amount, user_id) sorted descending
    debtors = sorted([(abs(v), k) for k, v in balances.items() if v < -0.01], reverse=True)

    result = []

    while creditors and debtors:
        c_amt, c_id = creditors.pop(0)  # largest creditor
        d_amt, d_id = debtors.pop(0)    # largest debtor

        # Transfer the minimum of the two amounts
        amt = min(c_amt, d_amt)
        result.append({'from_user': d_id, 'to_user': c_id, 'amount': round(amt, 2)})

        # If the creditor is not fully paid — return the remainder to the queue
        if c_amt - amt > 0.01:
            creditors.insert(0, (c_amt - amt, c_id))
        # If the debtor still owes money — return the remainder to the queue
        elif d_amt - amt > 0.01:
            debtors.insert(0, (d_amt - amt, d_id))

    return result