from sqlalchemy.orm import Session
from app.models.transaction import Transaction


def create_transaction(
    db: Session,
    contract_id: int,
    amount: float,
    txn_type: str
):
    txn = Transaction(
        contract_id=contract_id,
        amount=amount,
        type=txn_type,
        status="SUCCESS"
    )

    db.add(txn)
    db.commit()
    db.refresh(txn)

    return txn