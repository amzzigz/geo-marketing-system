"""知识库路由"""

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db, get_current_user
from app.common.response import success_response
from app.common.pagination import PaginationParams
from app.knowledge import service
from app.knowledge.schemas import KnowledgeFileOut, KnowledgeFileDetail, KnowledgeChunkOut

router = APIRouter()


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """上传知识库文件"""
    content = await file.read()
    knowledge_file = await service.upload_file(
        db, user_id=current_user.id, file_content=content, original_name=file.filename
    )
    return success_response(
        data=KnowledgeFileOut.model_validate(knowledge_file).model_dump(),
        message="上传成功",
    )


@router.get("")
async def get_file_list(
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """获取知识库文件列表"""
    result = await service.get_file_list(
        db, user_id=current_user.id, page=pagination.page, page_size=pagination.page_size
    )
    items = [KnowledgeFileOut.model_validate(item).model_dump() for item in result["items"]]
    return success_response(data={
        "items": items,
        "total": result["total"],
        "page": result["page"],
        "page_size": result["page_size"],
    })


@router.get("/{file_id}")
async def get_file_detail(
    file_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """获取文件详情"""
    result = await service.get_file_detail(db, user_id=current_user.id, file_id=file_id)
    file_data = KnowledgeFileDetail(
        id=result["file"].id,
        file_name=result["file"].file_name,
        file_type=result["file"].file_type,
        file_size=result["file"].file_size,
        content_text=result["file"].content_text,
        status=result["file"].status,
        created_at=result["file"].created_at,
        updated_at=result["file"].updated_at,
        chunks=[KnowledgeChunkOut.model_validate(c) for c in result["chunks"]],
    )
    return success_response(data=file_data.model_dump())


@router.delete("/{file_id}")
async def delete_file(
    file_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """删除知识库文件（软删除）"""
    await service.delete_file(db, user_id=current_user.id, file_id=file_id)
    return success_response(message="删除成功")
