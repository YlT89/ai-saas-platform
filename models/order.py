from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timezone

class Order(SQLModel, table=True):
    __tablename__ = "sys_order"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    goods_name: str
    price: float = Field(gt=0)
    num: int = Field(ge=1)
    create_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))