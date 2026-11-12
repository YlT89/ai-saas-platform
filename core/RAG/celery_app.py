# pip install celery redis
from celery import Celery
import os

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

# 这里的 redis://localhost:6379/1 代表用 Redis 的第 1 个数据库存任务队列（和向量库 0 分开）
celery_app = Celery(
    'sass_worker',
    broker=f"{redis_url}/1",
    backend=f"{redis_url}/1",
    include=["core.RAG.tasks"]  # 告诉它去哪个文件找任务
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

