"""用户管理路由"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db, get_current_user
from app.common.response import success_response
from app.users import service
from app.users.models import User
from app.users.schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    UserLoginResponse,
    UserInfoResponse,
)

router = APIRouter()


@router.post("/register")
async def register(req: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    user = await service.register(db, req.username, req.password, req.phone)
    return success_response(data={"id": user.id, "username": user.username}, message="注册成功")


@router.post("/login")
async def login(req: UserLoginRequest, db: AsyncSession = Depends(get_db)):
    user, token = await service.login(db, req.username, req.password)
    return success_response(data=UserLoginResponse(access_token=token).model_dump())


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return success_response(data=UserInfoResponse.model_validate(current_user).model_dump())
