# 注意这个文件需要双开终端
from core.RAG.celery_app import celery_app
from core.config import settings

from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_redis import RedisVectorStore
import os

@celery_app.task
def process_document_task(file_path: str, kb_id: int):
    """后台默默处理文档的苦力任务"""
    print(f'让我瞅瞅都是啥文件： {file_path}, 属于知识库 {kb_id}')

    try:
        # 1、苦力负责判断文件类型并加载
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.pdf':
            loader = PyPDFLoader(file_path)
        elif ext == '.txt':
            loader = TextLoader(file_path, encoding='utf-8')
        else:
            print(f'不太支持哦~: {file_path}')
            return

        docs = loader.load()

        # 2、切分
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50, length_function=len)
        texts = text_splitter.split_documents(docs)

        # 3、向量化入库
        embeddings = DashScopeEmbeddings(model='text-embedding-v3', dashscope_api_key=settings.dashscope_api_key)
        index_name = f"kb_index_{kb_id}"

        RedisVectorStore.from_documents(
            documents=texts,
            embedding=embeddings,
            index_name=index_name,
            redis_url="redis://localhost:6379",
        )

        texts = text_splitter.split_documents(docs)
        print(f"【DEBUG】切分出的文档块数：{len(texts)}")
        print(f'你的知识库 {kb_id} 的文档 {file_path} 处理好了')
    except Exception as err:
        print(f'哎呀~处理文件 {file_path} 的时候走神了: {str(err)}')
    finally:
        # 处理完文件就直接清理本地临时文件
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f'好了我干完活了 {file_path} 该下班了')
