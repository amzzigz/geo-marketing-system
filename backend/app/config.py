"""GEO营销系统配置"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置，从 .env 文件读取"""

    # 数据库
    DATABASE_URL: str = (
        "mssql+aioodbc:///?odbc_connect="
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost;"
        "DATABASE=geo_marketing;"
        "Trusted_Connection=yes"
    )

    # JWT
    JWT_SECRET_KEY: str = "dev-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440

    # One API
    ONE_API_BASE_URL: str = "http://localhost:3000"
    ONE_API_KEY: str = ""
    DEEPSEEK_MODEL: str = "deepseek-chat"

    # 文件上传
    UPLOAD_DIR: str = "./uploads"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


@lru_cache
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()
