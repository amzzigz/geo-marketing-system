"""用户请求/响应Schema"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=6, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)


class UserLoginRequest(BaseModel):
    username: str
    password: str


class UserLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserInfoResponse(BaseModel):
    id: int
    username: str
    phone: Optional[str] = None
    email: Optional[str] = None
    company_name: Optional[str] = None
    role: str
    balance: float
    status: int
    created_at: datetime

    model_config = {"from_attributes": True}
