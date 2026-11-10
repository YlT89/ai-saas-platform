from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone

if TYPE_CHECKING:
    from models.user import User

class ChatMessage(SQLModel, table=True):
    __tablename__ = 'chat_message'

    id: Optional[int] = Field(default=None, primary_key=True)

    user_id: int = Field(foreign_key='user.id', index=True)

    role_type: str   # 改成role_type 或者 msg_role（聊天接口的除了发给大模型的其它都改），然后删库（dev1.db）重建，因为容易和SQL起冲突
    content: str

    create_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    kb_id: Optional[int] = Field(default=None, foreign_key="kb.id")

    user: Optional['User'] = Relationship(back_populates='chat')

