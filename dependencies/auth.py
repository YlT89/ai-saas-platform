from datetime import timedelta, datetime, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlmodel import Session
from db.session import get_db
from models.user import User
from crud.user_crud import user_crud
from core.config import settings
from typing import Annotated

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_cred_exception():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="登录失败，请重新登录",
        headers={"WWW-Authenticate": "Bearer"},
    )


def create_token(data: dict):
    expire = timedelta(minutes=settings.token_expire_min)
    to_encode = data.copy()
    to_encode.update({"exp": datetime.now(timezone.utc) + expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm='HS256')


async def parse_token(token: Annotated[str, Depends(oauth2_scheme)]):
    try:

        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    except JWTError:

        raise get_cred_exception()


    username = payload.get("sub")
    if not username:
        raise get_cred_exception()

    return username


async def get_current_user(
    db: Session = Depends(get_db),
    username: str = Depends(parse_token)
):
    user = user_crud.get_by_username(db, username)
    if not user:

        raise HTTPException(status_code=404, detail="用户不存在或已被注销")
    return user


async def get_active_user(user: Annotated[User, Depends(get_current_user)]):
    if user.disabled:
        raise HTTPException(status_code=403, detail='账号没了')
    return user