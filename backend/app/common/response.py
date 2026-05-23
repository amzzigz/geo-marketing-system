"""统一响应格式"""

from typing import Any, Optional, Generic, TypeVar, List

from pydantic import BaseModel

T = TypeVar("T")


def success_response(data: Any = None, message: str = "success") -> dict:
    """成功响应"""
    return {"code": 0, "data": data, "message": message}


def error_response(code: int, message: str) -> dict:
    """错误响应"""
    return {"code": code, "data": None, "message": message}


class PageResponse(BaseModel, Generic[T]):
    """分页响应Schema"""
    items: List[T] = []
    total: int = 0
    page: int = 1
    page_size: int = 20
