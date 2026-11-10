from core.logger import logger
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from core.response import ApiResp




def register_exception_handlers(app: FastAPI):

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):

        error_msgs = []
        for error in exc.errors():
            loc = " -> ".join([str(x) for x in error["loc"]])
            msg = error["msg"]
            error_msgs.append(f"{loc}: {msg}")

        error_msg_str = "; ".join(error_msgs)
        logger.warning(f"参数校验失败: {error_msg_str}")


        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content=ApiResp(code=422, msg=f"参数校验失败: {error_msg_str}").model_dump()
        )


    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        logger.warning(f"业务异常拦截: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content=ApiResp(code=exc.status_code, msg=str(exc.detail)).model_dump(),
            headers=exc.headers
        )


    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):

        logger.error(f"服务器内部错误: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ApiResp(code=500, msg="服务器内部错误，请联系管理员").model_dump()
        )