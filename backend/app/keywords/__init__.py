"""核心主词管理模块"""

from app.keywords.models import CoreKeyword
from app.keywords.router import router

__all__ = ["CoreKeyword", "router"]
