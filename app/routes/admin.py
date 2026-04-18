from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import SessionLocal

from app.models.contract import Contract
from app.models.escrow import Escrow
from app.models.transaction import Transaction

from app.services.admin_service import (
    admin_force_status,
    admin_force_release,
    admin_refund,
    admin_freeze_contract
)

from app.services.deps import require_admin


router = APIRouter(prefix="/admin", tags=["Admin"])


# =========================
# DB SESSION
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================================================
# 📊 PLATFORM METRICS (ADMIN DASHBOARD)
# =========================================================
@router.get("/metrics")
def get_metrics(
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):

    total_contracts = db.query(func.count(Contract.id)).scalar() or 0
    total_escrow_value = db.query(func.sum(Escrow.total_amount)).scalar() or 0
    total_funded = db.query(func.sum(Escrow.funded_amount)).scalar() or 0
    total_transactions = db.query(func.count(Transaction.id)).scalar() or 0

    return {
        "total_contracts": total_contracts,
        "total_escrow_value": float(total_escrow_value),
        "total_funded": float(total_funded),
        "total_transactions": total_transactions
    }


# =========================================================
# 📦 ALL CONTRACTS (ADMIN VIEW)
# =========================================================
@router.get("/contracts")
def get_all_contracts(
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):

    contracts = db.query(Contract).all()

    return [
        {
            "contract_number": c.contract_number,
            "title": c.title,
            "amount": float(c.amount),
            "status": c.status,
            "client_id": c.client_id,
            "worker_id": c.worker_id
        }
        for c in contracts
    ]


# =========================================================
# 💰 ALL ESCROWS
# =========================================================
@router.get("/escrows")
def get_all_escrows(
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):

    escrows = db.query(Escrow).all()

    return [
        {
            "contract_id": e.contract_id,
            "total_amount": float(e.total_amount),
            "funded_amount": float(e.funded_amount),
            "is_fully_funded": e.is_fully_funded,
            "is_released": e.is_released
        }
        for e in escrows
    ]


# =========================================================
# 📜 ALL TRANSACTIONS (LEDGER VIEW)
# =========================================================
@router.get("/transactions")
def get_all_transactions(
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):

    transactions = db.query(Transaction).order_by(Transaction.created_at.desc()).all()

    return [
        {
            "id": t.id,
            "contract_id": t.contract_id,
            "type": t.type,
            "amount": float(t.amount),
            "status": t.status,
            "created_at": t.created_at
        }
        for t in transactions
    ]


# =========================================================
# ⚠️ FORCE STATUS CHANGE (ADMIN OVERRIDE)
# =========================================================
@router.post("/force-status/{contract_number}")
def force_status(
    contract_number: str,
    new_status: str,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):

    try:
        return admin_force_status(db, contract_number, new_status)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# =========================================================
# 💸 FORCE ESCROW RELEASE
# =========================================================
@router.post("/force-release/{contract_number}")
def force_release(
    contract_number: str,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):

    try:
        return admin_force_release(db, contract_number)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# =========================================================
# 🔁 REFUND ESCROW
# =========================================================
@router.post("/refund/{contract_number}")
def refund(
    contract_number: str,
    amount: float,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):

    try:
        return admin_refund(db, contract_number, amount)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# =========================================================
# 🔒 FREEZE CONTRACT
# =========================================================
@router.post("/freeze/{contract_number}")
def freeze(
    contract_number: str,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):

    try:
        return admin_freeze_contract(db, contract_number)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))