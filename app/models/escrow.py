from sqlalchemy import Column, Integer, Numeric, Boolean, ForeignKey
from app.database import Base


class Escrow(Base):
    __tablename__ = "escrows"

    id = Column(Integer, primary_key=True, index=True)

    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)

    total_amount = Column(Numeric(12, 2), nullable=False)
    funded_amount = Column(Numeric(12, 2), default=0)

    is_fully_funded = Column(Boolean, default=False)
    is_released = Column(Boolean, default=False)