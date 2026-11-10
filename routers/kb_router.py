import os
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlmodel import Session
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_redis import RedisVectorStore
from langchain_core.runnables import RunnablePassthrough
from langchain_community.document_loaders import PyPDFLoader,TextLoader

from db.session import get_db
from models.user import User
from models.kb import KB
from schemas.kb_schemas import KBCreate, KBPublic
from dependencies.auth import get_current_user
from crud.kb_crud import kb_crud
from schemas.chat_schemas import ChatRequest
from core.ai_config import get_llm, get_embeddings, prompt


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

        llm = Depends(get_llm),  # 自动注入
        embeddings = Depends(get_embeddings)
):
    # 验证知识库是否属于当前用户
    kb = db.get(KB, kb_id)
    if not kb or kb.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="知识库不存在或无权限")

    # 读取上传的文件内容
    # 1. 先把用户传的文件，保存到本地的临时文件夹
    temp_path = f"./uploads/{file.filename}"
    content = await file.read() # 读取文件二进制内容
    with open(temp_path, "wb") as f:
        f.write(content)

    # 2. 根据后缀名选择不同的加载器
    if file.filename.endswith(".pdf"):
        loader = PyPDFLoader(temp_path)
        documents = loader.load()
    elif file.filename.endswith(".txt"):
        loader = TextLoader(temp_path, encoding="utf-8")
        documents = loader.load()
    else:
        raise HTTPException(status_code=400, detail="不支持的文件格式")

    # 文本切分
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50, length_function=len)
    texts = text_splitter.split_documents(documents)

    # 🚨 存入 Redis：利用 kb_id 作为索引名，实现数据隔离
    index_name = f"kb_index_{kb_id}"
    # 注意：如果你用的是 langchain_community 的 Redis
    RedisVectorStore.from_documents(
        documents=texts,
        embedding=embeddings,
        redis_url="redis://localhost:6379",
        index_name=index_name
    )

    return {"msg": "上传并向量化成功", "filename": file.filename, "chunks": len(texts)}


# ==========================================
# 3. 进行 RAG 提问
# ==========================================
@kb_router.post("/{kb_id}/chat")
def chat_kb(
        kb_id: int,
        req: ChatRequest,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        llm = Depends(get_llm),  # 自动注入
        embeddings = Depends(get_embeddings)
):
    kb = db.get(KB, kb_id)
    if not kb or kb.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="知识库不存在或无权限")

    # 连接对应的 Redis 索引
    index_name = f"kb_index_{kb_id}"
    vector_store = RedisVectorStore(
        redis_url="redis://localhost:6379",
        index_name=index_name,
        embeddings=embeddings
    )

    retriever = vector_store.as_retriever(search_kwargs={"k": 2})

    # 组装 LCEL 链
    rag_chain = {"context": retriever, "question": RunnablePassthrough()} | prompt | llm

    # 执行
    result = rag_chain.invoke(req.question)

    return {"answer": result.content}