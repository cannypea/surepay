from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
import os


# =========================
# CONFIG (USE ENV IN PRODUCTION)
# =========================
SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_THIS_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


# =========================
# PASSWORD HASHING
# =========================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a plain password using bcrypt.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)


# =========================
# JWT TOKEN CREATION
# =========================
def create_access_token(data: dict, expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES):
    """
    Create a JWT access token with expiration.
    """

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})

    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return token


# =========================
# DECODE TOKEN
# =========================
def decode_access_token(token: str):
    """
    Decode JWT token and return payload.
    Raises exception if invalid or expired.
    """

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload

    except JWTError:
        return None


# =========================
# EXTRACT USER INFO FROM TOKEN
# =========================
def get_token_data(token: str):
    """
    Helper to extract user_id and role from token safely.
    """

    payload = decode_access_token(token)

    if not payload:
        return None

    return {
        "user_id": payload.get("user_id"),
        "role": payload.get("role")
    }