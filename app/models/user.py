from sqlalchemy import Column, Integer, String
from app.database import Base
from sqlalchemy import Column, Integer, String

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(String, unique=True, index=True)
    password = Column(String)

    # NEW
    role = Column(String, default="USER")  # USER | ADMIN