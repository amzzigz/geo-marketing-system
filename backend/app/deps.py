"""公共依赖注入"""

from typing import AsyncGenerator

from fastapi import Depends, Header
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.common.exceptions import BizException
from app.database import get_db as _get_db

settings = get_settings()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话"""
    async for session in _get_db():
        yield session


async def get_current_user(
    authorization: str | None = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """从JWT token解析当前用户"""
    if not authorization or not authorization.startswith("Bearer "):
        raise BizException(code=401, message="未登录或token格式错误")

    token = authorization[7:]
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id = int(payload.get("sub", 0))
    except (JWTError, ValueError):
        raise BizException(code=401, message="token无效或已过期")

    from app.users.service import get_user_by_id
    user = await get_user_by_id(db, user_id)
    if not user:
        raise BizException(code=401, message="用户不存在")
    if user.status == 0:
        raise BizException(code=401, message="账号已被禁用")
    return user
