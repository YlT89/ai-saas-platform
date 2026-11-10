from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select, func, text
from db.session import get_db
from models.order import Order
from core.response import success_resp

order_router = APIRouter(prefix="/orders", tags=["订单管理"])


@order_router.get("/list")
def get_order_page(
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=50),
        db: Session = Depends(get_db)  # 🚨 正确使用依赖注入
):
    offset = (page - 1) * page_size
    items = db.exec(select(Order).offset(offset).limit(page_size)).all()
    total = db.exec(select(func.count(Order.id))).one()

    return success_resp(data={
        "page": page,
        "page_size": page_size,
        "total": total,
        "items": items
    })