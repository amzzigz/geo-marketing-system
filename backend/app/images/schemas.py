"""图片素材请求/响应Schema"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CategoryCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    related_keyword_id: Optional[int] = None


class CategoryUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    related_keyword_id: Optional[int] = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    related_keyword_id: Optional[int] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ImageResponse(BaseModel):
    id: int
    category_id: int
    file_url: str
    file_name: str
    file_size: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    created_at: datetime

    model_config = {"from_attributes": True}
