"""知识库业务逻辑"""

import uuid
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.common.exceptions import BizException
from app.common.pagination import paginate
from app.knowledge.models import KnowledgeFile, KnowledgeChunk

settings = get_settings()

ALLOWED_EXTENSIONS = {"docx", "txt", "pdf"}
UPLOAD_SUBDIR = "knowledge"


def _get_upload_dir() -> Path:
    upload_dir = Path(settings.UPLOAD_DIR) / UPLOAD_SUBDIR
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


def _get_file_extension(filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext


def _extract_text_from_docx(file_path: str) -> str:
    from docx import Document
    doc = Document(file_path)
    return "\n".join(p.text for p in doc.paragraphs)


def _extract_text_from_pdf(file_path: str) -> str:
    import pdfplumber
    texts = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                texts.append(page_text)
    return "\n".join(texts)


def _extract_text_from_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def _extract_text(file_path: str, file_type: str) -> str:
    if file_type == "docx":
        return _extract_text_from_docx(file_path)
    elif file_type == "pdf":
        return _extract_text_from_pdf(file_path)
    elif file_type == "txt":
        return _extract_text_from_txt(file_path)
    else:
        raise BizException(code=4001, message="不支持的文件类型")


def _split_into_chunks(text: str) -> list[str]:
    chunks = []
    current_chunk = []
    for line in text.split("\n"):
        if line.strip() == "":
            if current_chunk:
                chunks.append("\n".join(current_chunk))
                current_chunk = []
        else:
            current_chunk.append(line)
    if current_chunk:
        chunks.append("\n".join(current_chunk))
    return [c for c in chunks if c.strip()]


async def upload_file(db: AsyncSession, user_id: int, file_content: bytes, original_name: str) -> KnowledgeFile:
    file_type = _get_file_extension(original_name)
    if file_type not in ALLOWED_EXTENSIONS:
        raise BizException(code=4001, message="不支持的文件类型，仅支持docx/txt/pdf")

    unique_name = f"{uuid.uuid4().hex}.{file_type}"
    upload_dir = _get_upload_dir()
    file_path = upload_dir / unique_name

    with open(file_path, "wb") as f:
        f.write(file_content)

    try:
        full_text = _extract_text(str(file_path), file_type)
    except BizException:
        raise
    except Exception as e:
        raise BizException(code=4002, message=f"文件内容提取失败：{str(e)}")

    chunks = _split_into_chunks(full_text)

    knowledge_file = KnowledgeFile(
        user_id=user_id,
        file_name=original_name,
        file_type=file_type,
        file_path=str(file_path),
        file_size=len(file_content),
        content_text=full_text,
    )
    db.add(knowledge_file)
    await db.flush()

    for idx, chunk_content in enumerate(chunks):
        chunk = KnowledgeChunk(
            file_id=knowledge_file.id,
            user_id=user_id,
            chunk_text=chunk_content,
            chunk_order=idx + 1,
        )
        db.add(chunk)

    await db.refresh(knowledge_file)
    return knowledge_file


async def get_file_list(db: AsyncSession, user_id: int, page: int, page_size: int) -> dict:
    query = (
        select(KnowledgeFile)
        .where(KnowledgeFile.user_id == user_id, KnowledgeFile.is_deleted == False)
        .order_by(KnowledgeFile.created_at.desc())
    )
    return await paginate(db, query, page=page, page_size=page_size)


async def get_file_detail(db: AsyncSession, user_id: int, file_id: int) -> dict:
    result = await db.execute(
        select(KnowledgeFile).where(KnowledgeFile.id == file_id, KnowledgeFile.is_deleted == False)
    )
    file = result.scalar_one_or_none()
    if not file:
        raise BizException(code=4004, message="文件不存在")
    if file.user_id != user_id:
        raise BizException(code=4003, message="无权访问该文件")

    chunks_result = await db.execute(
        select(KnowledgeChunk).where(KnowledgeChunk.file_id == file_id).order_by(KnowledgeChunk.chunk_order)
    )
    chunks = chunks_result.scalars().all()
    return {"file": file, "chunks": chunks}


async def delete_file(db: AsyncSession, user_id: int, file_id: int) -> None:
    result = await db.execute(
        select(KnowledgeFile).where(KnowledgeFile.id == file_id, KnowledgeFile.is_deleted == False)
    )
    file = result.scalar_one_or_none()
    if not file:
        raise BizException(code=4004, message="文件不存在")
    if file.user_id != user_id:
        raise BizException(code=4003, message="无权操作该文件")
    file.is_deleted = True
