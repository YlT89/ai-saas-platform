from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone

if TYPE_CHECKING:
    from models.user import User


class KB(SQLModel, table=True):
    # 1. 标准主键（自增ID）
    id: Optional[int] = Field(default=None, primary_key=True)

    # 2. 库的名称（普通字段）
    name: str = Field(index=True, description="知识库名称")

    # 3. 关联外键（必须有）
    user_id: int = Field(foreign_key="user.id")

    create_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # 4. 关联关系
    user: Optional["User"] = Relationship(back_populates="kb")