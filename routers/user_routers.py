from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from db.session import get_db
from dependencies.auth import get_active_user
from models.user import User
from schemas.user_schemas import UserPublic, UserUpdate
from crud.user_crud import user_crud
from core.response import ApiResp, PageData, success_resp, fail_resp
from sqlalchemy import func

user_router = APIRouter(prefix='/user', tags=['用户管理'], dependencies=[Depends(get_active_user)])

# 获取当前用户信息，不需要分页参数
@user_router.get("/me", response_model=ApiResp[UserPublic])
def get_my_info(user: User = Depends(get_active_user)):
    return success_resp(user)

# 获取用户列表，带分页参数
@user_router.get("/list", response_model=ApiResp[PageData[UserPublic]])
def list_user(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, le=50),
    db: Session = Depends(get_db)
):
    stmt = select(User).options(selectinload(User.addresses))
    offset = (page - 1) * page_size
    items =db.exec(stmt.offset(offset).limit(page_size)).all()
    total = db.exec(select(func.count(User.id))).one()
    page_data = PageData(page=page, page_size=page_size, total=total, items=items)
    return success_resp(page_data)

# 修改个人信息
@user_router.put('/update', response_model=ApiResp[UserPublic])
def update_user(
        update_in: UserUpdate,
        user: User = Depends(get_active_user),
        db: Session = Depends(get_db),
):
    update_data = update_in.model_dump(exclude_unset=True)
    new_user = user_crud.update(db, user, update_data)
    return success_resp(new_user)

# 删除账号
@user_router.delete('/del/{uid}', response_model=ApiResp)
def del_user(uid: int, db: Session = Depends(get_db)):
    obj = user_crud.delete(db,uid)
    if not obj:
        return fail_resp('用户不存在', 404)
    return success_resp(msg='恭喜去世')