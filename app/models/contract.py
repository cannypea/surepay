from sqlalchemy import Column, Integer, String, Text, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)

    contract_number = Column(String, unique=True, index=True, nullable=False)

    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    # IMPORTANT: money-safe type
    amount = Column(Numeric(12, 2), nullable=False)

    # lifecycle default
    status = Column(String, nullable=False, default="CREATED")

    client_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    worker_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # ORM relationships (VERY useful later)
    client = relationship("User", foreign_keys=[client_id])
    worker = relationship("User", foreign_keys=[worker_id])