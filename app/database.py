import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# 🔥 Load .env from project root explicitly
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# 🧠 Debug help (temporary)
print("DATABASE_URL =", DATABASE_URL)

if not DATABASE_URL:
    raise Exception(
        "DATABASE_URL not found. "
        "Check: 1) .env exists 2) correct name 3) correct folder (surepay root)"
    )

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()