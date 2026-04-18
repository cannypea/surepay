from sqlalchemy.orm import Session

from app.models.contract import Contract
from app.models.escrow import Escrow
from app.services.transaction_service import create_transaction


# =========================
# FORCE STATUS UPDATE
# =========================
def admin_force_status(db: Session, contract_number: str, new_status: str):

    contract = db.query(Contract).filter(
        Contract.contract_number == contract_number
    ).first()

    if not contract:
        raise ValueError("Contract not found")

    old_status = contract.status
    contract.status = new_status

    db.commit()
    db.refresh(contract)

    return {
        "message": "Admin status override applied",
        "contract_number": contract.contract_number,
        "old_status": old_status,
        "new_status": contract.status
    }


# =========================
# FORCE RELEASE ESCROW
# =========================
def admin_force_release(db: Session, contract_number: str):

    contract = db.query(Contract).filter(
        Contract.contract_number == contract_number
    ).first()

    if not contract:
        raise ValueError("Contract not found")

    escrow = contract.escrow

    if not escrow:
        raise ValueError("Escrow not found")

    if escrow.is_released:
        raise ValueError("Already released")

    escrow.is_released = True
    contract.status = "RELEASED"

    # 🔥 ledger entry
    create_transaction(
        db=db,
        contract_id=contract.id,
        amount=escrow.total_amount,
        txn_type="ADMIN_RELEASE"
    )

    db.commit()
    db.refresh(contract)

    return {
        "message": "Admin forced release executed",
        "contract_number": contract.contract_number,
        "status": contract.status
    }


# =========================
# REFUND ESCROW (LOGICAL ONLY FOR NOW)
# =========================
def admin_refund(db: Session, contract_number: str, amount: float):

    contract = db.query(Contract).filter(
        Contract.contract_number == contract_number
    ).first()

    if not contract:
        raise ValueError("Contract not found")

    escrow = contract.escrow

    if not escrow:
        raise ValueError("Escrow not found")

    if escrow.funded_amount < amount:
        raise ValueError("Insufficient escrow balance")

    escrow.funded_amount -= amount

    create_transaction(
        db=db,
        contract_id=contract.id,
        amount=amount,
        txn_type="ADMIN_REFUND"
    )

    db.commit()
    db.refresh(escrow)

    return {
        "message": "Refund processed",
        "contract_number": contract.contract_number,
        "refunded_amount": amount,
        "remaining_funded": float(escrow.funded_amount)
    }


# =========================
# FREEZE CONTRACT
# =========================
def admin_freeze_contract(db: Session, contract_number: str):

    contract = db.query(Contract).filter(
        Contract.contract_number == contract_number
    ).first()

    if not contract:
        raise ValueError("Contract not found")

    contract.status = "FROZEN"

    db.commit()
    db.refresh(contract)

    return {
        "message": "Contract frozen",
        "contract_number": contract.contract_number,
        "status": contract.status
    }