"""知识库Pydantic Schema"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class KnowledgeFileOut(BaseModel):
    id: int
    file_name: str
    file_type: str
    file_size: Optional[int] = None
    status: int = 1
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class KnowledgeChunkOut(BaseModel):
    id: int
    chunk_order: int
    chunk_text: str

    model_config = {"from_attributes": True}


class KnowledgeFileDetail(BaseModel):
    id: int
    file_name: str
    file_type: str
    file_size: Optional[int] = None
    content_text: Optional[str] = None
    status: int = 1
    created_at: datetime
    updated_at: datetime
    chunks: List[KnowledgeChunkOut] = []

    model_config = {"from_attributes": True}
