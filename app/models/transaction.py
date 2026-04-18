from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime
from datetime import datetime
from app.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)

    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)

    amount = Column(Numeric(12, 2), nullable=False)

    # FUND, RELEASE, REFUND (future)
    type = Column(String, nullable=False)

    status = Column(String, default="SUCCESS")

    created_at = Column(DateTime, default=datetime.utcnow)