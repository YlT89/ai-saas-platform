from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from models.user import User


class Address(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    province: str
    city: str
    detail: str


    user_id: Optional[int] = Field(default=None, foreign_key='user.id', ondelete='CASCADE')

    user: Optional["User"] = Relationship(back_populates="addresses")



