from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from db.session import get_db
from schemas.user_schemas import UserCreate
from crud.user_crud import user_crud
from dependencies.auth import create_token
from passlib.context import CryptContext
from core.response import ApiResp, success_resp


pwd_ctx = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


auth_router = APIRouter(prefix='/auth', tags=['登录注册'])


@auth_router.post('/register', response_model=ApiResp, summary="用户注册")
def register(user_in: UserCreate, db: Session = Depends(get_db)):

    if user_crud.get_by_username(db, user_in.username):
        raise HTTPException(status_code=400, detail='用户已存在')


    hash_pwd = pwd_ctx.hash(user_in.password)


    user_data = user_in.model_dump(exclude={"password"})
    user_data["hashed_password"] = hash_pwd


    db_user = user_crud.create(db, user_data)

    return success_resp(msg="注册成功", data={"username": db_user.username})


@auth_router.post('/login', summary="登录获取Token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = user_crud.get_by_username(db, form_data.username)

    if not user:

        pwd_ctx.verify("dummy_password", "$pbkdf2-sha256$29000$wpjzHmPM.d87h1AKgZAyhg$5Mn0MSPpR5IeYKeju.yN3iQccMFjpjFNUKtTal99tW8")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not pwd_ctx.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='用户名或密码错误',
            headers={"WWW-Authenticate": "Bearer"}
        )


    token = create_token({'sub': user.username})


    return {'access_token': token, 'token_type': 'bearer'}