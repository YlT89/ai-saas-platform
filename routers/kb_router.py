import os
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlmodel import Session, select
from langchain_redis import RedisVectorStore
import shutil

from db.session import get_db
from models.user import User
from models.kb import KB
from schemas.kb_schemas import KBCreate, KBPublic
from dependencies.auth import get_current_user
from crud.kb_crud import kb_crud
from schemas.chat_schemas import ChatRequest
from core.RAG.ai_config import get_llm, get_embeddings, prompt, prompt_template
from core.RAG.tasks import process_document_task
from celery.result import AsyncResult
from core.RAG.celery_app import celery_app
from models.chat import ChatMessage
from fastapi.responses import StreamingResponse



kb_router = APIRouter(prefix="/kb", tags=["知识库管理"])

os.makedirs("./uploads", exist_ok=True) # 自动创建文件夹（如果不存在的话）


# ==========================================
# 1. 创建知识库
# ==========================================
@kb_router.post("/create", response_model=KBPublic, status_code=status.HTTP_201_CREATED)
def create_kb(
        kb_in: KBCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    # 查重
    existing_kb = kb_crud.get_by_name_and_user(db, kb_in.name, current_user.id)
    if existing_kb:
        raise HTTPException(status_code=400, detail="您已经创建过同名的知识库了")

    db_kb = KB(name=kb_in.name, user_id=current_user.id)
    db.add(db_kb)
    db.commit()
    db.refresh(db_kb)
    return db_kb


# ==========================================
# 2. 上传文件并存入向量库
# ==========================================
@kb_router.post("/{kb_id}/upload")
async def upload_kb(
        kb_id: int,
        file: UploadFile = File(...),  # 接收用户上传的文件
        # File(...)、Field(...)、Query(...)、Body(...)，加上 ... 都代表“必填”。

        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),

):
    # 验证知识库是否属于当前用户
    kb = db.get(KB, kb_id)
    if not kb or kb.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="知识库不存在或无权限")

    # 读取上传的文件内容
    # 1. 把文件存到本地临时目录
    os.makedirs("uploads", exist_ok=True)
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 2. 派发给 Celery 后台处理（注意这里加了 .delay）
    task = process_document_task.delay(file_path, kb_id)

    # 3. 直接返回，不用等它处理完！
    return {"msg": "文件已上传，正在后台排队处理，请稍后刷新查看进度", 'task_id': task.id}  # 把这个任务的唯一 ID 给前端

# 进度接口
@kb_router.get("/{kb_id}/task/{task_id}/status")
async def get_task_status(
        kb_id: int,
        task_id: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    # 🚨 核心：先查库，确保这个知识库是当前用户的！
    kb = db.get(KB, kb_id)
    if not kb or kb.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问此知识库")

    # 校验通过后，再去查 Celery 状态
    task_result = AsyncResult(task_id, app=celery_app)

    # 状态可能是：PENDING(排队中), STARTED(执行中), SUCCESS(成功), FAILURE(失败)
    if task_result.state == 'SUCCESS':
        return {"status": "SUCCESS", "result": task_result.result}
    elif task_result.state == 'FAILURE':
        return {"status": "FAILURE", "error": str(task_result.info)}
    else:
        return {"status": task_result.state}

# ==========================================
# 3. 进行 RAG 提问
# ==========================================
@kb_router.post("/{kb_id}/chat")
async def chat_kb(
        kb_id: int,
        req: ChatRequest,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        llm=Depends(get_llm),  # 用依赖注入拿实例
        embeddings=Depends(get_embeddings)  # 用依赖注入拿实例
):
    kb = db.get(KB, kb_id)
    if not kb or kb.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="知识库不存在或无权限")

    history_records = db.exec(
        select(ChatMessage)
        .where(ChatMessage.user_id == current_user.id)
        .order_by(ChatMessage.create_time.desc())
        .limit(4)
    ).all()
    history_records.reverse()

    index_name = f"kb_index_{kb_id}"

    vector_store = RedisVectorStore(
        redis_url=os.getenv("REDIS_URL", "redis://localhost:6379"),
        index_name=index_name,
        embeddings=embeddings
    )
    # 如果没报错，再去检索
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    docs = retriever.invoke(req.question)



    # 拼接上下文（用从配置文件导入的模板）
    context_text = "\n\n".join([doc.page_content for doc in docs])


    # 1. 系统提示词：只放背景规则和检索到的资料，不要把用户问题混进去
    system_prompt = prompt_template.format(context=context_text, question="")

    # 2. 开始组装消息列表
    messages = [
        {"role": "system", "content": system_prompt}
    ]

    # 3. 加入历史记录 (排在过去)
    for msg in history_records:
        messages.append({"role": msg.role_type, "content": msg.content})

    # 4. 最后，在末尾加上用户刚刚提的这一个问题
    messages.append({"role": "user", "content": req.question})


    async def stream_generator():
        full_ai_response = ""
        try:
            async for chunk in llm.astream(messages):
                content = chunk.content
                if content:
                    full_ai_response += content
                    yield f"data: {content}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"
        finally:
            if full_ai_response:
                ai_msg = ChatMessage(
                    user_id=current_user.id,
                    role_type="assistant",
                    content=full_ai_response
                )
                db.add(ai_msg)
                db.commit()

    return StreamingResponse(stream_generator(), media_type="text/event-stream")