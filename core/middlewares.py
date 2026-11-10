import time
import uuid
from core.logger import logger
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from core.config import settings

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        req_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:16])
        request.state.req_id = req_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = req_id

        return response

class LogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        client_ip = request.client.host
        method = request.method
        path = request.url.path
        req_id = getattr(request.state, "req_id", "unknown")
        logger.info(f"[{req_id}] 请求进入: {method} {path} | 客户端IP: {client_ip}")

        try:
            response = await call_next(request)
        except Exception as e:
            logger.error(f"[{req_id}] 请求发生异常: {str(e)}", exc_info=True)
            raise e

        cost = round((time.perf_counter() - start_time) * 1000, 2)
        response.headers["X-Request-Cost-ms"] = str(cost)
        logger.info(f"[{req_id}] 请求结束: {method} {path} | 状态码: {response.status_code} | 耗时: {cost}ms")

        return response


def register_middlewares(app: FastAPI):

    app.add_middleware(LogMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(RequestIDMiddleware)