from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, timezone

if TYPE_CHECKING:
    from models.address import Address
    from models.chat import ChatMessage
    from models.kb import KB

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(min_length=1, unique=True, index=True)
    email: str = Field(index=True)
    hashed_password: str = Field(exclude=True)
    user_role: str = Field(default='user')
    disabled: bool = Field(default=False)
    create_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


    addresses: List["Address"] = Relationship(back_populates='user', cascade_delete=True)
    chat: List["ChatMessage"] = Relationship(back_populates='user', cascade_delete=True)
    kb: List['KB'] = Relationship(back_populates='user', cascade_delete=True)

