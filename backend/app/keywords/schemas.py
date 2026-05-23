"""核心主词请求/响应Schema"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class KeywordCreateRequest(BaseModel):
    keyword: str = Field(..., min_length=1, max_length=100, description="主词")
    target_word: Optional[str] = Field(None, max_length=200, description="目标转化词")
    industry: Optional[str] = Field(None, max_length=50, description="行业")
    related_product: Optional[str] = Field(None, max_length=200, description="关联产品")
    target_region: Optional[str] = Field(None, max_length=100, description="目标地区")


class KeywordUpdateRequest(BaseModel):
    keyword: Optional[str] = Field(None, min_length=1, max_length=100, description="主词")
    target_word: Optional[str] = Field(None, max_length=200, description="目标转化词")
    industry: Optional[str] = Field(None, max_length=50, description="行业")
    related_product: Optional[str] = Field(None, max_length=200, description="关联产品")
    target_region: Optional[str] = Field(None, max_length=100, description="目标地区")
    status: Optional[int] = Field(None, ge=0, le=1, description="状态：1=启用 0=停用")


class KeywordResponse(BaseModel):
    id: int
    keyword: str
    target_word: Optional[str] = None
    industry: Optional[str] = None
    related_product: Optional[str] = None
    target_region: Optional[str] = None
    status: int
    generated_article_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ExpansionKeywordResponse(BaseModel):
    id: int
    core_keyword_id: int
    phrase: str
    phrase_type: Optional[str] = None
    source: Optional[str] = None
    used_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class GenerateExpansionResponse(BaseModel):
    core_keyword: str
    target_word: str
    sub_keywords: list[str] = Field(description="副词列表")
    combined_keywords: list[str] = Field(description="组合词列表")


class SubwordResponse(BaseModel):
    id: int
    core_keyword_id: int
    name: str
    reason: Optional[str] = None
    search_potential_score: Optional[int] = None
    source: str
    status: int
    created_at: datetime

    model_config = {"from_attributes": True}


class CombinationResponse(BaseModel):
    id: int
    subword_id: int
    word: str
    intent: Optional[str] = None
    priority: Optional[int] = None
    source: str
    article_status: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class SubwordCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="副词名称")


class CombinationCreateRequest(BaseModel):
    word: str = Field(..., min_length=1, max_length=300, description="组合词内容")
    intent: Optional[str] = Field(None, max_length=30, description="搜索意图类型")
