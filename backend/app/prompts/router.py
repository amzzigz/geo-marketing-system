"""AI指令模板路由"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db, get_current_user
from app.common.response import success_response
from app.prompts import service
from app.prompts.schemas import (
    PromptCreateRequest,
    PromptUpdateRequest,
    PromptResponse,
    BatchDeleteRequest,
)
from app.users.models import User

router = APIRouter()


@router.post("")
async def create_prompt(
    req: PromptCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建指令模板"""
    template = await service.create_template(
        db,
        user_id=current_user.id,
        name=req.name,
        prompt_type=req.prompt_type,
        content_type=req.content_type,
        platform=req.platform,
        prompt_text=req.prompt_text,
    )
    return success_response(
        data=PromptResponse.model_validate(template).model_dump(),
        message="创建成功",
    )


@router.get("")
async def list_prompts(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页条数"),
    prompt_type: Optional[str] = Query(None, description="指令类型筛选: title/content/fusion"),
    platform: Optional[str] = Query(None, description="平台筛选"),
    name: Optional[str] = Query(None, description="指令名称模糊搜索"),
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """查询指令模板列表"""
    result = await service.list_templates(
        db,
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        prompt_type=prompt_type,
        platform=platform,
        name=name,
        start_date=start_date,
        end_date=end_date,
    )
    result["items"] = [
        PromptResponse.model_validate(item).model_dump() for item in result["items"]
    ]
    return success_response(data=result)


@router.delete("/batch")
async def batch_delete_prompts(
    req: BatchDeleteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """批量删除指令模板"""
    count = await service.batch_delete_templates(
        db, user_id=current_user.id, ids=req.ids
    )
    return success_response(data={"deleted_count": count}, message=f"成功删除{count}条")


@router.get("/{template_id}")
async def get_prompt_detail(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取指令模板详情"""
    template = await service.get_template_by_id(db, template_id)
    if not template:
        from app.common.exceptions import BizException
        raise BizException(code=4041, message="模板不存在")
    return success_response(
        data=PromptResponse.model_validate(template).model_dump()
    )


@router.put("/{template_id}")
async def update_prompt(
    template_id: int,
    req: PromptUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """编辑指令模板"""
    template = await service.update_template(
        db,
        user_id=current_user.id,
        template_id=template_id,
        name=req.name,
        prompt_type=req.prompt_type,
        content_type=req.content_type,
        platform=req.platform,
        prompt_text=req.prompt_text,
    )
    return success_response(
        data=PromptResponse.model_validate(template).model_dump(),
        message="更新成功",
    )


@router.delete("/{template_id}")
async def delete_prompt(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除指令模板"""
    await service.delete_template(db, user_id=current_user.id, template_id=template_id)
    return success_response(message="删除成功")
