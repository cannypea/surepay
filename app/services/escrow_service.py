from sqlalchemy.orm import Session
from app.models.contract import Contract
from app.models.escrow import Escrow
from app.services.transaction_service import create_transaction


# =========================
# CREATE ESCROW (called on contract creation)
# =========================
def create_escrow_for_contract(db: Session, contract: Contract):

    escrow = Escrow(
        contract_id=contract.id,
        total_amount=contract.amount,
        funded_amount=0,
        is_fully_funded=False,
        is_released=False
    )

    db.add(escrow)
    db.commit()
    db.refresh(escrow)

    return escrow


# =========================
# FUND ESCROW
# =========================
def fund_escrow(db: Session, contract_number: str, amount: float):

    contract = db.query(Contract).filter(
        Contract.contract_number == contract_number
    ).first()

    if not contract:
        raise ValueError("Contract not found")

    escrow = contract.escrow

    if not escrow:
        raise ValueError("Escrow not initialized")

    # Only allow funding at CREATED stage
    if contract.status != "CREATED":
        raise ValueError("Contract not in fundable state")

    # Prevent funding after full funding
    if escrow.is_fully_funded:
        raise ValueError("Contract already fully funded")

    # Add funds
    escrow.funded_amount += amount

    # 🔒 RECORD TRANSACTION (FUND)
    create_transaction(
        db=db,
        contract_id=contract.id,
        amount=amount,
        txn_type="FUND"
    )

    # Check if fully funded
    if escrow.funded_amount >= escrow.total_amount:
        escrow.is_fully_funded = True
        contract.status = "FUNDED"

    db.commit()
    db.refresh(contract)

    return contract


# =========================
# RELEASE FUNDS
# =========================
def release_funds(db: Session, contract_number: str):

    contract = db.query(Contract).filter(
        Contract.contract_number == contract_number
    ).first()

    if not contract:
        raise ValueError("Contract not found")

    escrow = contract.escrow

    if not escrow:
        raise ValueError("Escrow not initialized")

    if not escrow.is_fully_funded:
        raise ValueError("Escrow not fully funded")

    if contract.status != "COMPLETED":
        raise ValueError("Contract must be COMPLETED before release")

    if escrow.is_released:
        raise ValueError("Funds already released")

    # Release funds
    escrow.is_released = True
    contract.status = "RELEASED"

    # 🔒 RECORD TRANSACTION (RELEASE)
    create_transaction(
        db=db,
        contract_id=contract.id,
        amount=escrow.total_amount,
        txn_type="RELEASE"
    )

    db.commit()
    db.refresh(contract)

    return contract


# =========================
# GET ESCROW DETAILS
# =========================
def get_escrow_by_contract(db: Session, contract_number: str):

    contract = db.query(Contract).filter(
        Contract.contract_number == contract_number
    ).first()

    if not contract:
        raise ValueError("Contract not found")

    escrow = contract.escrow

    if not escrow:
        raise ValueError("Escrow not initialized")

    return escrow