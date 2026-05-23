"""用户业务逻辑"""

from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.common.exceptions import BizException
from app.users.models import User

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: int, username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "username": username, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


async def register(db: AsyncSession, username: str, password: str, phone: str | None) -> User:
    stmt = select(User).where(User.username == username, User.is_deleted == False)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise BizException(code=4001, message="用户名已存在")

    user = User(
        username=username,
        password_hash=hash_password(password),
        phone=phone,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def login(db: AsyncSession, username: str, password: str) -> tuple[User, str]:
    stmt = select(User).where(User.username == username, User.is_deleted == False)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.password_hash):
        raise BizException(code=4002, message="用户名或密码错误")

    if user.status == 0:
        raise BizException(code=4003, message="账号已被禁用")

    token = create_access_token(user.id, user.username)
    return user, token


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    stmt = select(User).where(User.id == user_id, User.is_deleted == False)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
