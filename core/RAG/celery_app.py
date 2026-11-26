# pip install celery redis
from celery import Celery
import os

# Celery broker/backend 固定用 1 号库，与向量库（0 号库）分离
# 强制从环境变量读取，没有就用本地的 6380/1
celery_redis_url = os.getenv("CELERY_REDIS_URL", "redis://localhost:6380/1")

celery_app = Celery(
    'sass_worker',
    broker=celery_redis_url,
    backend=celery_redis_url,
    include=["core.RAG.tasks"]      # 告诉他去哪个文件找谁
)
# 增加以下配置
celery_app.conf.update(
    # 1. 在启动时无限重试连接（直到成功）
    broker_connection_retry_on_startup=True,

    # 2. 设置最大重试次数为 None（无限重试），防止耗尽
    broker_connection_max_retries=None,

    # 3. 设置结果后端也允许重试
    result_backend_always_retry=True,
    result_backend_max_retries=30,  # 或者设为 None 无限重试

    # 4. 添加健康检查，让连接保持活跃，及时发现死连接
    broker_transport_options={
        'health_check_interval': 30,
        'socket_keepalive': True,
    },
    result_backend_transport_options={
        'health_check_interval': 30,
        'socket_keepalive': True,
    },
)

