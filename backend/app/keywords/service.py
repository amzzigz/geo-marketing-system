"""核心主词业务逻辑"""

from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.common.pagination import paginate
from app.keywords.models import CoreKeyword, ExpansionKeyword, Subword, Combination
from app.keywords.ai_service import call_deepseek_legacy as call_deepseek, generate_keyword_tree


async def create_keyword(db: AsyncSession, user_id: int, keyword: str, target_word: str | None, industry: str | None, related_product: str | None, target_region: str | None = None) -> CoreKeyword:
    """添加主词"""
    obj = CoreKeyword(
        user_id=user_id,
        keyword=keyword,
        target_word=target_word,
        industry=industry,
        related_product=related_product,
        target_region=target_region,
    )
    db.add(obj)
    await db.flush()
    await db.refresh(obj)
    return obj


async def get_keyword_list(db: AsyncSession, user_id: int, page: int, page_size: int, keyword: str | None = None) -> dict:
    """分页查询主词列表"""
    query = (
        select(CoreKeyword)
        .where(CoreKeyword.user_id == user_id, CoreKeyword.is_deleted == False)
        .order_by(CoreKeyword.id.desc())
    )
    if keyword:
        query = query.where(CoreKeyword.keyword.contains(keyword))
    return await paginate(db, query, page=page, page_size=page_size)


async def get_keyword_by_id(db: AsyncSession, keyword_id: int, user_id: int) -> CoreKeyword:
    """获取主词详情，校验归属"""
    result = await db.execute(
        select(CoreKeyword).where(
            CoreKeyword.id == keyword_id,
            CoreKeyword.user_id == user_id,
            CoreKeyword.is_deleted == False,
        )
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise BizException(code=4004, message="主词不存在或无权访问")
    return obj


async def update_keyword(db: AsyncSession, keyword_id: int, user_id: int, **kwargs) -> CoreKeyword:
    """编辑主词"""
    obj = await get_keyword_by_id(db, keyword_id, user_id)
    for key, value in kwargs.items():
        if value is not None:
            setattr(obj, key, value)
    obj.updated_at = datetime.now()
    await db.flush()
    await db.refresh(obj)
    return obj


async def delete_keyword(db: AsyncSession, keyword_id: int, user_id: int) -> None:
    """软删除主词"""
    obj = await get_keyword_by_id(db, keyword_id, user_id)
    if obj.generated_article_count > 0:
        raise BizException(code=4001, message="该主词已有关联文章，无法删除")
    obj.is_deleted = True
    obj.updated_at = datetime.now()
    await db.flush()


async def generate_and_save_expansions(db: AsyncSession, user_id: int, core_keyword_id: int) -> dict:
    """调用AI生成拓展词并存储"""
    keyword_obj = await get_keyword_by_id(db, core_keyword_id, user_id)
    if not keyword_obj.target_word:
        raise BizException(code=4002, message="请先填写目标转化词再生成拓展词")

    result = await call_deepseek(keyword_obj.keyword, keyword_obj.target_word)

    sub_keywords = result.get("副词列表", [])
    combined_keywords = result.get("组合词列表", [])

    # 软删除该主词下旧的AI生成拓展词
    await db.execute(
        update(ExpansionKeyword)
        .where(
            ExpansionKeyword.core_keyword_id == core_keyword_id,
            ExpansionKeyword.user_id == user_id,
            ExpansionKeyword.source == "ai",
            ExpansionKeyword.is_deleted == False,
        )
        .values(is_deleted=True)
    )

    # 批量写入新的拓展词
    for phrase in sub_keywords:
        db.add(ExpansionKeyword(
            user_id=user_id,
            core_keyword_id=core_keyword_id,
            phrase=phrase,
            phrase_type="suffix",
            source="ai",
        ))
    for phrase in combined_keywords:
        db.add(ExpansionKeyword(
            user_id=user_id,
            core_keyword_id=core_keyword_id,
            phrase=phrase,
            phrase_type="combined",
            source="ai",
        ))

    await db.flush()

    return {
        "core_keyword": keyword_obj.keyword,
        "target_word": keyword_obj.target_word,
        "sub_keywords": sub_keywords,
        "combined_keywords": combined_keywords,
    }


async def get_expansions_by_keyword(db: AsyncSession, user_id: int, core_keyword_id: int, page: int, page_size: int) -> dict:
    """查询某主词下的拓展词列表"""
    await get_keyword_by_id(db, core_keyword_id, user_id)
    query = (
        select(ExpansionKeyword)
        .where(
            ExpansionKeyword.core_keyword_id == core_keyword_id,
            ExpansionKeyword.user_id == user_id,
            ExpansionKeyword.is_deleted == False,
        )
        .order_by(ExpansionKeyword.id.desc())
    )
    return await paginate(db, query, page=page, page_size=page_size)


async def delete_expansion(db: AsyncSession, expansion_id: int, user_id: int) -> None:
    """软删除单条拓展词"""
    result = await db.execute(
        select(ExpansionKeyword).where(
            ExpansionKeyword.id == expansion_id,
            ExpansionKeyword.user_id == user_id,
            ExpansionKeyword.is_deleted == False,
        )
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise BizException(code=4004, message="拓展词不存在或无权访问")
    obj.is_deleted = True
    await db.flush()


# ========== 关键词树服务 ==========


async def generate_keyword_tree_service(db: AsyncSession, user_id: int, core_keyword_id: int) -> dict:
    """AI生成完整关键词树"""
    keyword_obj = await get_keyword_by_id(db, core_keyword_id, user_id)
    if not keyword_obj.target_word:
        raise BizException(code=4002, message="请先填写目标转化词再生成关键词树")

    result = await generate_keyword_tree(
        keyword=keyword_obj.keyword,
        target_word=keyword_obj.target_word,
        industry=keyword_obj.industry,
        related_product=keyword_obj.related_product,
        target_region=keyword_obj.target_region,
    )

    # 软删除旧的 AI 生成数据
    await db.execute(
        update(Subword).where(
            Subword.core_keyword_id == core_keyword_id,
            Subword.user_id == user_id,
            Subword.source == "ai",
            Subword.is_deleted == False,
        ).values(is_deleted=True)
    )
    await db.execute(
        update(Combination).where(
            Combination.core_keyword_id == core_keyword_id,
            Combination.user_id == user_id,
            Combination.source == "ai",
            Combination.is_deleted == False,
        ).values(is_deleted=True)
    )

    # 批量插入
    sub_words_data = result.get("sub_words", [])
    for sw in sub_words_data:
        subword_obj = Subword(
            user_id=user_id,
            core_keyword_id=core_keyword_id,
            name=sw["name"],
            reason=sw.get("reason"),
            search_potential_score=sw.get("search_potential_score"),
            source="ai",
        )
        db.add(subword_obj)
        await db.flush()

        for cw in sw.get("combo_words", []):
            db.add(Combination(
                user_id=user_id,
                core_keyword_id=core_keyword_id,
                subword_id=subword_obj.id,
                word=cw["word"],
                intent=cw.get("intent"),
                priority=cw.get("priority"),
                source="ai",
            ))

    await db.flush()
    return result


async def get_subwords(db: AsyncSession, user_id: int, core_keyword_id: int) -> list:
    """获取副词列表"""
    await get_keyword_by_id(db, core_keyword_id, user_id)
    result = await db.execute(
        select(Subword).where(
            Subword.core_keyword_id == core_keyword_id,
            Subword.user_id == user_id,
            Subword.is_deleted == False,
        ).order_by(Subword.search_potential_score.desc())
    )
    return list(result.scalars().all())


async def get_combinations(db: AsyncSession, user_id: int, subword_id: int) -> list:
    """获取组合词列表"""
    result = await db.execute(
        select(Combination).where(
            Combination.subword_id == subword_id,
            Combination.user_id == user_id,
            Combination.is_deleted == False,
        ).order_by(Combination.priority.desc())
    )
    return list(result.scalars().all())


async def delete_subword(db: AsyncSession, user_id: int, subword_id: int) -> None:
    """软删除副词及其下属组合词"""
    result = await db.execute(
        select(Subword).where(
            Subword.id == subword_id,
            Subword.user_id == user_id,
            Subword.is_deleted == False,
        )
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise BizException(code=4004, message="副词不存在")
    obj.is_deleted = True
    # 级联软删组合词
    await db.execute(
        update(Combination).where(
            Combination.subword_id == subword_id,
            Combination.is_deleted == False,
        ).values(is_deleted=True)
    )
    await db.flush()


async def delete_combination(db: AsyncSession, user_id: int, combination_id: int) -> None:
    """软删除单条组合词"""
    result = await db.execute(
        select(Combination).where(
            Combination.id == combination_id,
            Combination.user_id == user_id,
            Combination.is_deleted == False,
        )
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise BizException(code=4004, message="组合词不存在")
    obj.is_deleted = True
    await db.flush()


async def add_subword_manual(db: AsyncSession, user_id: int, core_keyword_id: int, name: str) -> Subword:
    """手动添加副词"""
    await get_keyword_by_id(db, core_keyword_id, user_id)
    obj = Subword(user_id=user_id, core_keyword_id=core_keyword_id, name=name, source="manual")
    db.add(obj)
    await db.flush()
    await db.refresh(obj)
    return obj


async def add_combination_manual(db: AsyncSession, user_id: int, subword_id: int, word: str, intent: str | None) -> Combination:
    """手动添加组合词"""
    # 验证 subword 存在
    result = await db.execute(
        select(Subword).where(
            Subword.id == subword_id,
            Subword.user_id == user_id,
            Subword.is_deleted == False,
        )
    )
    sw = result.scalar_one_or_none()
    if not sw:
        raise BizException(code=4004, message="副词不存在")
    obj = Combination(
        user_id=user_id,
        core_keyword_id=sw.core_keyword_id,
        subword_id=subword_id,
        word=word,
        intent=intent,
        source="manual",
    )
    db.add(obj)
    await db.flush()
    await db.refresh(obj)
    return obj
