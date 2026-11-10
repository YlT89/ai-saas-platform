from datetime import timedelta, datetime, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from typing import Annotated
from core.config import settings
from core.logger import logger

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_cred_exception():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="未登录或登录已过期",
        headers={"WWW-Authenticate": "Bearer"},
    )

def create_token(data: dict):
    expire = timedelta(minutes=settings.token_expire_min)
    to_encode = data.copy()
    to_encode.update({"exp": datetime.now(timezone.utc) + expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm="HS256")


async def parse_token(token: Annotated[str, Depends(oauth2_scheme)]) -> str:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        username = payload.get("sub")
        if not username:
            raise get_cred_exception()
        return username
    except JWTError:
        raise get_cred_exception()