"""AI指令模板业务逻辑"""

from datetime import datetime

from sqlalchemy import select, or_, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.common.pagination import paginate
from app.prompts.models import PromptTemplate


async def create_template(
    db: AsyncSession,
    user_id: int,
    name: str,
    prompt_type: str,
    content_type: str | None,
    platform: str | None,
    prompt_text: str,
) -> PromptTemplate:
    """创建指令模板"""
    template = PromptTemplate(
        user_id=user_id,
        name=name,
        prompt_type=prompt_type,
        content_type=content_type,
        platform=platform,
        prompt_text=prompt_text,
    )
    db.add(template)
    await db.flush()
    await db.refresh(template)
    return template


async def list_templates(
    db: AsyncSession,
    user_id: int,
    page: int = 1,
    page_size: int = 20,
    prompt_type: str | None = None,
    platform: str | None = None,
    name: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict:
    """查询模板列表：当前用户的 + 系统预置的"""
    query = select(PromptTemplate).where(
        PromptTemplate.is_deleted == False,
        or_(
            PromptTemplate.user_id == user_id,
            and_(PromptTemplate.user_id.is_(None), PromptTemplate.is_default == True),
        ),
    )

    if prompt_type:
        query = query.where(PromptTemplate.prompt_type == prompt_type)
    if platform:
        query = query.where(PromptTemplate.platform == platform)
    if name:
        query = query.where(PromptTemplate.name.contains(name))
    if start_date:
        query = query.where(PromptTemplate.created_at >= start_date)
    if end_date:
        query = query.where(PromptTemplate.created_at <= end_date + " 23:59:59")

    query = query.order_by(PromptTemplate.created_at.desc())

    return await paginate(db, query, page=page, page_size=page_size)


async def get_template_by_id(db: AsyncSession, template_id: int) -> PromptTemplate | None:
    """根据ID获取模板"""
    stmt = select(PromptTemplate).where(
        PromptTemplate.id == template_id,
        PromptTemplate.is_deleted == False,
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def update_template(
    db: AsyncSession,
    user_id: int,
    template_id: int,
    **kwargs,
) -> PromptTemplate:
    """编辑指令模板（只能编辑自己的）"""
    template = await get_template_by_id(db, template_id)
    if not template:
        raise BizException(code=4041, message="模板不存在")
    if template.user_id is None:
        raise BizException(code=4031, message="系统预置模板不可编辑")
    if template.user_id != user_id:
        raise BizException(code=4032, message="无权编辑他人模板")

    for key, value in kwargs.items():
        if value is not None:
            setattr(template, key, value)
    template.updated_at = datetime.now()

    await db.flush()
    await db.refresh(template)
    return template


async def delete_template(
    db: AsyncSession,
    user_id: int,
    template_id: int,
) -> None:
    """软删除指令模板（只能删除自己的）"""
    template = await get_template_by_id(db, template_id)
    if not template:
        raise BizException(code=4041, message="模板不存在")
    if template.user_id is None:
        raise BizException(code=4031, message="系统预置模板不可删除")
    if template.user_id != user_id:
        raise BizException(code=4032, message="无权删除他人模板")

    template.is_deleted = True
    template.updated_at = datetime.now()
    await db.flush()


async def batch_delete_templates(
    db: AsyncSession,
    user_id: int,
    ids: list[int],
) -> int:
    """批量软删除指令模板（只能删除自己的，跳过系统预置）"""
    stmt = select(PromptTemplate).where(
        PromptTemplate.id.in_(ids),
        PromptTemplate.is_deleted == False,
        PromptTemplate.user_id == user_id,
    )
    result = await db.execute(stmt)
    templates = result.scalars().all()

    count = 0
    for template in templates:
        template.is_deleted = True
        template.updated_at = datetime.now()
        count += 1

    await db.flush()
    return count


async def init_default_prompts(db: AsyncSession) -> None:
    """初始化系统内置指令规则（幂等，已存在则跳过）"""
    # 检查是否已有系统默认数据
    stmt = select(func.count()).select_from(PromptTemplate).where(
        PromptTemplate.is_default == True,
        PromptTemplate.is_deleted == False,
    )
    result = await db.execute(stmt)
    existing_count = result.scalar() or 0
    if existing_count > 0:
        return

    defaults = [
        {
            "name": "区域-百科-35字",
            "platform": "通用类",
            "prompt_type": "content",
            "prompt_text": "请根据以下关键词生成一篇百科类文章，字数不少于800字。要求：内容专业权威，结构清晰，包含定义、背景、详细说明、应用场景等部分。语言客观中立，适合百科收录。关键词自然融入，密度控制在2%-5%。标题控制在35字以内。",
        },
        {
            "name": "区域-测评-35字",
            "platform": "通用类",
            "prompt_type": "content",
            "prompt_text": "请根据以下关键词生成一篇测评类文章，字数不少于800字。要求：从用户视角出发，包含产品概述、核心功能测评、优缺点分析、使用体验、总结推荐等部分。语言真实可信，数据具体，适合消费者参考。标题控制在35字以内。",
        },
        {
            "name": "区域-问答-35字",
            "platform": "通用类",
            "prompt_type": "content",
            "prompt_text": "请根据以下关键词生成一篇问答类文章，字数不少于800字。要求：以一问一答形式组织内容，覆盖用户最关心的5-8个问题。回答专业详尽，引用数据或案例支撑。适合搜索引擎问答场景收录。标题控制在35字以内。",
        },
        {
            "name": "百科类型-35字",
            "platform": "通用类",
            "prompt_type": "title",
            "prompt_text": "请根据以下关键词生成5个百科类文章标题，每个标题不超过35字。要求：标题信息量大，包含核心关键词，适合搜索引擎收录。风格客观权威，避免夸张用语。每行一个标题，不要编号。",
        },
        {
            "name": "测评类型-35字",
            "platform": "通用类",
            "prompt_type": "title",
            "prompt_text": "请根据以下关键词生成5个测评类文章标题，每个标题不超过35字。要求：标题吸引点击，体现测评属性（如对比、评测、体验），包含核心关键词。风格真实可信，避免标题党。每行一个标题，不要编号。",
        },
        {
            "name": "问答类型-35字",
            "platform": "通用类",
            "prompt_type": "title",
            "prompt_text": "请根据以下关键词生成5个问答类文章标题，每个标题不超过35字。要求：标题以疑问句形式呈现，贴近用户真实搜索意图，包含核心关键词。覆盖what/how/why等不同问题类型。每行一个标题，不要编号。",
        },
    ]

    for item in defaults:
        template = PromptTemplate(
            user_id=None,
            name=item["name"],
            platform=item["platform"],
            prompt_type=item["prompt_type"],
            content_type=None,
            prompt_text=item["prompt_text"],
            is_default=True,
            sort_order=0,
        )
        db.add(template)

    await db.flush()
