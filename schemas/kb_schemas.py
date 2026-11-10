from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# 1. 基础模型：抽取共有字段
class KBBase(BaseModel):
    # 约束：名称必填，且长度在 1 到 50 之间
    name: str = Field(..., min_length=1, max_length=50, description="知识库名称")

# 2. 创建知识库的入参（前端传这个）
class KBCreate(KBBase):
    # 绝不要在这里加 user_id！因为 user_id 应该从 Token 里拿，防止越权。
    pass

# 3. 返回给前端的出参（脱敏后的）
class KBPublic(KBBase):
    id: int
    # 出参里可以带上 user_id，让前端知道是谁建的
    user_id: int
    create_time: datetime

    # 允许从 ORM 对象读取（Pydantic V2 写法）
    model_config = {"from_attributes": True}

# 4. 更新知识库的入参（全部可选，支持局部更新）
class KBUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)