"""核心主词管理路由"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db, get_current_user
from app.common.response import success_response
from app.keywords import service
from app.keywords.schemas import (
    KeywordCreateRequest, KeywordUpdateRequest, KeywordResponse,
    ExpansionKeywordResponse, GenerateExpansionResponse,
    SubwordResponse, CombinationResponse,
    SubwordCreateRequest, CombinationCreateRequest,
)
from app.users.models import User

router = APIRouter()


@router.post("")
async def create_keyword(
    req: KeywordCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """添加主词"""
    obj = await service.create_keyword(
        db,
        user_id=current_user.id,
        keyword=req.keyword,
        target_word=req.target_word,
        industry=req.industry,
        related_product=req.related_product,
        target_region=req.target_region,
    )
    return success_response(data=KeywordResponse.model_validate(obj).model_dump(), message="添加成功")


@router.get("")
async def list_keywords(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页条数"),
    keyword: str | None = Query(None, description="主词模糊搜索"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """分页查询主词列表"""
    result = await service.get_keyword_list(db, user_id=current_user.id, page=page, page_size=page_size, keyword=keyword)
    result["items"] = [KeywordResponse.model_validate(item).model_dump() for item in result["items"]]
    return success_response(data=result)


@router.get("/{keyword_id}")
async def get_keyword(
    keyword_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取主词详情"""
    obj = await service.get_keyword_by_id(db, keyword_id=keyword_id, user_id=current_user.id)
    return success_response(data=KeywordResponse.model_validate(obj).model_dump())


@router.put("/{keyword_id}")
async def update_keyword(
    keyword_id: int,
    req: KeywordUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """编辑主词"""
    update_data = req.model_dump(exclude_unset=True)
    obj = await service.update_keyword(db, keyword_id=keyword_id, user_id=current_user.id, **update_data)
    return success_response(data=KeywordResponse.model_validate(obj).model_dump(), message="更新成功")


@router.delete("/{keyword_id}")
async def delete_keyword(
    keyword_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """软删除主词"""
    await service.delete_keyword(db, keyword_id=keyword_id, user_id=current_user.id)
    return success_response(message="删除成功")


@router.post("/{keyword_id}/expansions/generate")
async def generate_expansions(
    keyword_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """AI生成拓展词（副词+组合词）"""
    result = await service.generate_and_save_expansions(db, user_id=current_user.id, core_keyword_id=keyword_id)
    return success_response(
        data=GenerateExpansionResponse(**result).model_dump(),
        message="生成成功",
    )


@router.get("/{keyword_id}/expansions")
async def list_expansions(
    keyword_id: int,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=200, description="每页条数"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取某主词的拓展词列表"""
    result = await service.get_expansions_by_keyword(
        db, user_id=current_user.id, core_keyword_id=keyword_id, page=page, page_size=page_size
    )
    result["items"] = [ExpansionKeywordResponse.model_validate(item).model_dump() for item in result["items"]]
    return success_response(data=result)


@router.delete("/expansions/{expansion_id}")
async def delete_expansion(
    expansion_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除单条拓展词"""
    await service.delete_expansion(db, expansion_id=expansion_id, user_id=current_user.id)
    return success_response(message="删除成功")


# ========== 关键词树 ==========


@router.post("/{keyword_id}/generate-tree")
async def generate_tree(
    keyword_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """AI生成完整关键词树"""
    result = await service.generate_keyword_tree_service(db, user_id=current_user.id, core_keyword_id=keyword_id)
    return success_response(data=result, message="关键词树生成成功")


@router.get("/{keyword_id}/subwords")
async def list_subwords(
    keyword_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取副词列表"""
    items = await service.get_subwords(db, user_id=current_user.id, core_keyword_id=keyword_id)
    return success_response(data=[SubwordResponse.model_validate(item).model_dump() for item in items])


@router.post("/{keyword_id}/subwords")
async def create_subword(
    keyword_id: int,
    req: SubwordCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """手动添加副词"""
    obj = await service.add_subword_manual(db, user_id=current_user.id, core_keyword_id=keyword_id, name=req.name)
    return success_response(data=SubwordResponse.model_validate(obj).model_dump(), message="添加成功")


@router.get("/subwords/{subword_id}/combinations")
async def list_combinations(
    subword_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取组合词列表"""
    items = await service.get_combinations(db, user_id=current_user.id, subword_id=subword_id)
    return success_response(data=[CombinationResponse.model_validate(item).model_dump() for item in items])


@router.post("/subwords/{subword_id}/combinations")
async def create_combination(
    subword_id: int,
    req: CombinationCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """手动添加组合词"""
    obj = await service.add_combination_manual(db, user_id=current_user.id, subword_id=subword_id, word=req.word, intent=req.intent)
    return success_response(data=CombinationResponse.model_validate(obj).model_dump(), message="添加成功")


@router.delete("/subwords/{subword_id}")
async def remove_subword(
    subword_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除副词"""
    await service.delete_subword(db, user_id=current_user.id, subword_id=subword_id)
    return success_response(message="删除成功")


@router.delete("/combinations/{combination_id}")
async def remove_combination(
    combination_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除组合词"""
    await service.delete_combination(db, user_id=current_user.id, combination_id=combination_id)
    return success_response(message="删除成功")
