from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.transaction import Transaction
from app.database import SessionLocal

from app.schemas.contract import ContractCreate, ContractStatusUpdate

from app.services.contract_service import (
    create_contract,
    update_contract_status,
    get_contract_by_number,
    list_contracts
)

from app.services.escrow_service import (
    fund_escrow,
    release_funds
)

router = APIRouter()


# =========================
# DB SESSION
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# CREATE CONTRACT
# =========================
@router.post("/create")
def create(contract: ContractCreate, db: Session = Depends(get_db)):

    try:
        new_contract = create_contract(
            db=db,
            title=contract.title,
            description=contract.description,
            amount=contract.amount,
            client_id=contract.client_id,
            worker_id=contract.worker_id
        )

        return {
            "message": "Contract created successfully",
            "contract_number": new_contract.contract_number,
            "status": new_contract.status
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# =========================
# FUND ESCROW
# =========================
@router.post("/fund/{contract_number}")
def fund_contract(
    contract_number: str,
    amount: float,
    db: Session = Depends(get_db)
):

    try:
        contract = fund_escrow(db, contract_number, amount)

        return {
            "message": "Escrow funded successfully",
            "contract_number": contract.contract_number,
            "status": contract.status,
            "funded_amount": float(contract.escrow.funded_amount),
            "is_fully_funded": contract.escrow.is_fully_funded
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# =========================
# UPDATE STATUS (STATE MACHINE)
# =========================
@router.put("/status/{contract_number}")
def update_status(
    contract_number: str,
    update: ContractStatusUpdate,
    db: Session = Depends(get_db)
):

    try:
        contract = update_contract_status(
            db=db,
            contract_number=contract_number,
            new_status=update.status
        )

        return {
            "message": "Status updated successfully",
            "contract_number": contract.contract_number,
            "status": contract.status
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# =========================
# RELEASE FUNDS
# =========================
@router.post("/release/{contract_number}")
def release_contract(
    contract_number: str,
    db: Session = Depends(get_db)
):

    try:
        contract = release_funds(db, contract_number)

        return {
            "message": "Funds released successfully",
            "contract_number": contract.contract_number,
            "status": contract.status
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# =========================
# GET SINGLE CONTRACT
# =========================
@router.get("/{contract_number}")
def get_contract(contract_number: str, db: Session = Depends(get_db)):

    try:
        contract = get_contract_by_number(db, contract_number)

        return {
            "contract_number": contract.contract_number,
            "title": contract.title,
            "description": contract.description,
            "amount": float(contract.amount),
            "status": contract.status,
            "client_id": contract.client_id,
            "worker_id": contract.worker_id,
            "funded_amount": float(contract.escrow.funded_amount) if contract.escrow else 0,
            "is_fully_funded": contract.escrow.is_fully_funded if contract.escrow else False,
            "is_released": contract.escrow.is_released if contract.escrow else False
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# =========================
# LIST ALL CONTRACTS
# =========================
@router.get("/")
def get_all_contracts(db: Session = Depends(get_db)):

    contracts = list_contracts(db)

    return [
        {
            "contract_number": c.contract_number,
            "title": c.title,
            "amount": float(c.amount),
            "status": c.status,
            "funded_amount": float(c.escrow.funded_amount) if c.escrow else 0,
            "is_fully_funded": c.escrow.is_fully_funded if c.escrow else False,
            "is_released": c.escrow.is_released if c.escrow else False
        }
        for c in contracts
    ]

@router.get("/transactions/{contract_number}")
def get_transaction_history(contract_number: str, db: Session = Depends(get_db)):

    contract = get_contract_by_number(db, contract_number)

    transactions = db.query(Transaction).filter(
        Transaction.contract_id == contract.id
    ).order_by(Transaction.created_at.desc()).all()

    return {
        "contract_number": contract.contract_number,
        "transaction_count": len(transactions),
        "transactions": [
            {
                "id": t.id,
                "type": t.type,          # FUND | RELEASE
                "amount": float(t.amount),
                "status": t.status,
                "created_at": t.created_at
            }
            for t in transactions
        ]
    }