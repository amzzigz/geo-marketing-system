"""AI指令模板请求/响应Schema"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PromptCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="模板名称")
    prompt_type: str = Field(..., pattern=r"^(title|content|fusion)$", description="指令类型: title/content/fusion")
    content_type: Optional[str] = Field(None, max_length=20, description="内容类型: seo/news/tech等")
    platform: Optional[str] = Field(None, max_length=50, description="适用平台")
    prompt_text: str = Field(..., min_length=1, max_length=3000, description="指令文本")


class PromptUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="模板名称")
    prompt_type: Optional[str] = Field(None, pattern=r"^(title|content|fusion)$", description="指令类型: title/content/fusion")
    content_type: Optional[str] = Field(None, max_length=20, description="内容类型")
    platform: Optional[str] = Field(None, max_length=50, description="适用平台")
    prompt_text: Optional[str] = Field(None, min_length=1, max_length=3000, description="指令文本")


class BatchDeleteRequest(BaseModel):
    ids: list[int] = Field(..., min_length=1, description="要删除的模板ID列表")


class PromptResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    name: str
    prompt_type: str
    content_type: Optional[str] = None
    platform: Optional[str] = None
    prompt_text: str
    is_default: bool
    status: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
