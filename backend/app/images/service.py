"""图片素材业务逻辑"""

import uuid
from pathlib import Path

from fastapi import UploadFile
from PIL import Image as PILImage
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.common.exceptions import BizException
from app.common.pagination import paginate
from app.images.models import ImageCategory, Image

settings = get_settings()

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE = 2 * 1024 * 1024


async def create_category(db: AsyncSession, user_id: int, name: str, related_keyword_id: int | None) -> ImageCategory:
    category = ImageCategory(user_id=user_id, name=name, related_keyword_id=related_keyword_id)
    db.add(category)
    await db.flush()
    await db.refresh(category)
    return category


async def list_categories(db: AsyncSession, user_id: int) -> list[ImageCategory]:
    stmt = select(ImageCategory).where(
        ImageCategory.user_id == user_id, ImageCategory.is_deleted == False
    ).order_by(ImageCategory.created_at.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_category(db: AsyncSession, category_id: int, user_id: int) -> ImageCategory:
    stmt = select(ImageCategory).where(
        ImageCategory.id == category_id, ImageCategory.user_id == user_id, ImageCategory.is_deleted == False
    )
    result = await db.execute(stmt)
    category = result.scalar_one_or_none()
    if not category:
        raise BizException(code=4040, message="分类不存在")
    return category


async def update_category(db: AsyncSession, category_id: int, user_id: int, name: str | None, related_keyword_id: int | None) -> ImageCategory:
    category = await get_category(db, category_id, user_id)
    if name is not None:
        category.name = name
    if related_keyword_id is not None:
        category.related_keyword_id = related_keyword_id
    await db.flush()
    await db.refresh(category)
    return category


async def delete_category(db: AsyncSession, category_id: int, user_id: int) -> None:
    category = await get_category(db, category_id, user_id)
    count_stmt = select(func.count()).select_from(Image).where(
        Image.category_id == category_id, Image.is_deleted == False
    )
    result = await db.execute(count_stmt)
    if result.scalar() > 0:
        raise BizException(code=4001, message="该分类下还有图片，无法删除")
    category.is_deleted = True
    await db.flush()


async def upload_image(db: AsyncSession, user_id: int, category_id: int, file: UploadFile) -> Image:
    await get_category(db, category_id, user_id)

    if file.content_type not in ALLOWED_MIME_TYPES:
        raise BizException(code=4002, message="不支持的图片格式，仅允许 jpg/png/webp")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise BizException(code=4003, message="图片大小不能超过2MB")

    ext = Path(file.filename).suffix.lower() if file.filename else ".jpg"
    unique_name = f"{uuid.uuid4().hex}{ext}"
    save_dir = Path(settings.UPLOAD_DIR) / "images"
    save_dir.mkdir(parents=True, exist_ok=True)
    save_path = save_dir / unique_name

    save_path.write_bytes(content)

    width, height = None, None
    try:
        with PILImage.open(save_path) as img:
            width, height = img.size
    except Exception:
        pass

    image = Image(
        user_id=user_id,
        category_id=category_id,
        file_url=f"uploads/images/{unique_name}",
        file_name=file.filename or unique_name,
        file_size=len(content),
        width=width,
        height=height,
    )
    db.add(image)
    await db.flush()
    await db.refresh(image)
    return image


async def list_images(db: AsyncSession, user_id: int, category_id: int, page: int, page_size: int) -> dict:
    await get_category(db, category_id, user_id)
    stmt = select(Image).where(
        Image.category_id == category_id, Image.user_id == user_id, Image.is_deleted == False
    ).order_by(Image.created_at.desc())
    return await paginate(db, stmt, page=page, page_size=page_size)


async def delete_image(db: AsyncSession, image_id: int, user_id: int) -> None:
    stmt = select(Image).where(Image.id == image_id, Image.user_id == user_id, Image.is_deleted == False)
    result = await db.execute(stmt)
    image = result.scalar_one_or_none()
    if not image:
        raise BizException(code=4040, message="图片不存在")
    image.is_deleted = True
    await db.flush()
