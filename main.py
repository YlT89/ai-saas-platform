from core.exceptions import register_exception_handlers
from routers import api_v2
from core.middlewares import register_middlewares
import time
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
from sqlmodel import SQLModel
from db.session import engine
from fastapi import Response
from fastapi_offline import FastAPIOffline   # 下载本地Swagger页面
# python -m pip install fastapi-offline

# 这个只有运行的时候才会用到
from models import User, Address, Order, ChatMessage, KB


# 1. 定义生命周期
@asynccontextmanager
async def lifespan(app: FastAPIOffline):
    from sqlalchemy import inspect
    inspector = inspect(engine)

    if not inspector.has_table('user'):     # 检查’user‘表是否存在
        SQLModel.metadata.create_all(engine)
        print("✅ 数据库表初始化完成（仅在首次启动时提示）")
    else:
        print("⚡ 数据库表已存在，直接启动服务")

    yield
    print("服务关闭")

# 2. 把 lifespan 传给 FastAPI
app = FastAPIOffline(
    title="FastAPI + SQLModel综合项目",
    version="1.0",
    lifespan=lifespan,
)

# 文件传输国内那个CDN节点老有，BUG所以换成自己本地的

@app.get('/')
def index():
    return {"Hello": "World"}

@app.get('/stream')
def stream():
    def generate():
        for i in range(3):
            yield f"data chunk {i}\n"
            time.sleep(0.1) # 模拟一点点延迟，不能加太长免得测试卡住
    return StreamingResponse(generate(), media_type="text/plain")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204) # 返回 204 No Content

app.include_router(api_v2)


register_exception_handlers(app)


register_middlewares(app)


# uvicorn main:app --reload

# 如果注册账户出现问题的报错说没有这表的话，就重启服务器试试，如果不行就在终端输入这行代码，（注意：这句代码是强行把模型导入并建表，跑完一次就行）
# python -c "from sqlmodel import SQLModel; from db.session import engine; import models.user, models.chat; SQLModel.metadata.create_all(bind=engine)"