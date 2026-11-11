# pip install celery redis
from celery import Celery
import os

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")

# 这里的 redis://localhost:6379/1 代表用 Redis 的第 1 个数据库存任务队列（和向量库 0 分开）
celery_app = Celery(
    'sass_worker',
    broker=f"redis://{REDIS_HOST}:6379/1",
    backend=f"redis://{REDIS_HOST}:6379/1",
    include=["core.RAG.tasks"]  # 告诉它去哪个文件找任务
)

