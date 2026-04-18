from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from jose import jwt

from app.services.auth_service import SECRET_KEY, ALGORITHM

security = HTTPBearer()


def get_current_user(token=Depends(security)):

    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload

    except:
        raise HTTPException(status_code=401, detail="Invalid token")
    
def require_admin(user=Depends(get_current_user)):

    if user.get("role") != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")

    return user