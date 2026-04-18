from sqlalchemy.orm import Session
from app.models.contract import Contract
from app.models.escrow import Escrow
import random


# =========================
# STATUS FLOW (STATE MACHINE)
# =========================
STATUS_FLOW = {
    "CREATED": ["FUNDED"],
    "FUNDED": ["IN_PROGRESS"],
    "IN_PROGRESS": ["COMPLETED"],
    "COMPLETED": ["RELEASED"],
    "RELEASED": []
}


# =========================
# CREATE CONTRACT
# =========================
def create_contract(
    db: Session,
    title: str,
    description: str,
    amount: float,
    client_id: int,
    worker_id: int
):
    contract_number = f"CTR-{random.randint(100000, 999999)}"

    new_contract = Contract(
        contract_number=contract_number,
        title=title,
        description=description,
        amount=amount,
        client_id=client_id,
        worker_id=worker_id,
        status="CREATED"
    )

    db.add(new_contract)
    db.commit()
    db.refresh(new_contract)

    # 🔒 CREATE ESCROW IMMEDIATELY
    escrow = Escrow(
        contract_id=new_contract.id,
        total_amount=new_contract.amount
    )

    db.add(escrow)
    db.commit()

    return new_contract


# =========================
# GET CONTRACT
# =========================
def get_contract_by_number(db: Session, contract_number: str):
    contract = db.query(Contract).filter(
        Contract.contract_number == contract_number
    ).first()

    if not contract:
        raise ValueError("Contract not found")

    return contract


# =========================
# UPDATE CONTRACT STATUS (STRICT FLOW)
# =========================
def update_contract_status(
    db: Session,
    contract_number: str,
    new_status: str
):
    contract = get_contract_by_number(db, contract_number)

    current_status = contract.status
    allowed_next_states = STATUS_FLOW.get(current_status, [])

    # ❌ BLOCK INVALID TRANSITIONS
    if new_status not in allowed_next_states:
        raise ValueError(f"Invalid transition {current_status} → {new_status}")

    # 🔒 EXTRA SAFETY RULE
    if new_status == "IN_PROGRESS":
        if not contract.escrow or not contract.escrow.is_fully_funded:
            raise ValueError("Contract must be fully funded before work starts")

    contract.status = new_status

    db.commit()
    db.refresh(contract)

    return contract


# =========================
# LIST CONTRACTS (OPTIONAL BUT USEFUL)
# =========================
def list_contracts(db: Session):
    return db.query(Contract).all()