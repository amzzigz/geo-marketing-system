"""图片素材路由"""

from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db, get_current_user
from app.common.response import success_response
from app.common.pagination import PaginationParams
from app.images import service
from app.images.schemas import (
    CategoryCreateRequest,
    CategoryUpdateRequest,
    CategoryResponse,
    ImageResponse,
)
from app.users.models import User

router = APIRouter()


# ========== 分类管理 ==========

@router.post("/categories")
async def create_category(
    req: CategoryCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    category = await service.create_category(
        db, current_user.id, req.name, req.related_keyword_id
    )
    return success_response(data=CategoryResponse.model_validate(category).model_dump())


@router.get("/categories")
async def list_categories(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    categories = await service.list_categories(db, current_user.id)
    data = [CategoryResponse.model_validate(c).model_dump() for c in categories]
    return success_response(data=data)


@router.put("/categories/{category_id}")
async def update_category(
    category_id: int,
    req: CategoryUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    category = await service.update_category(
        db, category_id, current_user.id, req.name, req.related_keyword_id
    )
    return success_response(data=CategoryResponse.model_validate(category).model_dump())


@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await service.delete_category(db, category_id, current_user.id)
    return success_response(message="删除成功")


# ========== 图片管理 ==========

@router.post("/upload")
async def upload_image(
    category_id: int = Form(..., description="分类ID"),
    file: UploadFile = File(..., description="图片文件"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    image = await service.upload_image(db, current_user.id, category_id, file)
    return success_response(data=ImageResponse.model_validate(image).model_dump())


@router.get("/categories/{category_id}/images")
async def list_images(
    category_id: int,
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await service.list_images(db, current_user.id, category_id, pagination.page, pagination.page_size)
    data = {
        "items": [ImageResponse.model_validate(img).model_dump() for img in result["items"]],
        "total": result["total"],
        "page": result["page"],
        "page_size": result["page_size"],
    }
    return success_response(data=data)


@router.delete("/{image_id}")
async def delete_image(
    image_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await service.delete_image(db, image_id, current_user.id)
    return success_response(message="删除成功")
