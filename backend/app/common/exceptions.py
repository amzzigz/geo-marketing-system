"""全局异常处理"""

from fastapi import Request
from fastapi.responses import JSONResponse


class BizException(Exception):
    """业务异常"""

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


async def biz_exception_handler(request: Request, exc: BizException) -> JSONResponse:
    """业务异常处理器"""
    return JSONResponse(
        status_code=200,
        content={"code": exc.code, "data": None, "message": exc.message},
    )


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """全局未捕获异常处理器"""
    return JSONResponse(
        status_code=500,
        content={"code": 500, "data": None, "message": "服务器内部错误"},
    )
