"""GEO营销系统 - FastAPI入口"""

import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.common.exceptions import (
    BizException,
    biz_exception_handler,
    global_exception_handler,
)

settings = get_settings()

app = FastAPI(
    title="GEO营销系统",
    description="GEO内容营销自动化系统API",
    version="0.1.0",
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册异常处理器
app.add_exception_handler(BizException, biz_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=200,
        content={"code": 422, "data": None, "message": "请求参数错误"},
    )

# 挂载静态文件（uploads目录）
upload_dir = Path(settings.UPLOAD_DIR)
upload_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(upload_dir)), name="uploads")

# ============ 路由注册 ============
from app.users.router import router as users_router
from app.keywords.router import router as keywords_router
from app.knowledge.router import router as knowledge_router
from app.images.router import router as images_router
from app.prompts.router import router as prompts_router

app.include_router(users_router, prefix="/api/users", tags=["用户管理"])
app.include_router(keywords_router, prefix="/api/keywords", tags=["关键词管理"])
app.include_router(knowledge_router, prefix="/api/knowledge", tags=["知识库"])
app.include_router(images_router, prefix="/api/images", tags=["图片素材"])
app.include_router(prompts_router, prefix="/api/prompts", tags=["AI指令"])
# app.include_router(articles_router, prefix="/api/articles", tags=["文章管理"])
# app.include_router(publishing_router, prefix="/api/publishing", tags=["发布管理"])
# app.include_router(media_orders_router, prefix="/api/media-orders", tags=["官媒订单"])
# app.include_router(payments_router, prefix="/api/payments", tags=["支付钱包"])
# app.include_router(reports_router, prefix="/api/reports", tags=["数据报表"])
# ============ 路由注册结束 ============


@app.get("/", tags=["健康检查"])
async def root() -> dict:
    """根路径健康检查"""
    return {"code": 0, "data": {"status": "running"}, "message": "GEO营销系统运行中"}


@app.get("/health", tags=["健康检查"])
async def health_check() -> dict:
    """健康检查接口"""
    return {"code": 0, "data": {"status": "healthy"}, "message": "success"}
