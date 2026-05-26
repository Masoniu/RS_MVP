from sqlalchemy.orm import Session
from collections import defaultdict
import models


def get_room_balances(room_id: int, db: Session) -> dict[int, float]:
    balances = defaultdict(float)

    expenses = db.query(models.Expense).filter(models.Expense.room_id == room_id).all()

    for exp in expenses:
        balances[exp.payer_id] += exp.amount
        for split in exp.splits:
            balances[split.user_id] -= split.amount_owed

    return dict(balances)


def calculate_settlements(balances: dict[int, float]) -> list[dict]:
    creditors = sorted([(v, k) for k, v in balances.items() if v > 0.01], reverse=True)
    debtors = sorted([(abs(v), k) for k, v in balances.items() if v < -0.01], reverse=True)

    result = []

    while creditors and debtors:
        c_amt, c_id = creditors.pop(0)
        d_amt, d_id = debtors.pop(0)

        amt = min(c_amt, d_amt)
        result.append({'from_user': d_id, 'to_user': c_id, 'amount': round(amt, 2)})

        if c_amt - amt > 0.01:
            creditors.insert(0, (c_amt - amt, c_id))
        elif d_amt - amt > 0.01:
            debtors.insert(0, (d_amt - amt, d_id))

    return result