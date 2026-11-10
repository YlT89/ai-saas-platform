from pydantic import BaseModel,Field

class ChatRequest(BaseModel):

    question: str = Field(..., min_length=1, max_length=500)
    # 可选：如果前端告诉你当前在哪个知识库里提问
    kb_id: int | None = Field(default=None, description="当前提问关联的知识库ID")
