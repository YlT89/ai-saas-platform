from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class OrderBase(BaseModel):
    goods_name: str = Field(..., max_length=50, description="商品名称")
    price: float = Field(..., gt=0, description="单价")
    num: int = Field(..., ge=1, description="数量")


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseModel):
    goods_name: Optional[str] = None
    price: Optional[float] = Field(default=None, gt=0)
    num: Optional[int] = Field(default=None, ge=1)


class OrderPublic(OrderBase):
    id: int
    user_id: int
    create_time: datetime


    model_config = {"from_attributes": True}