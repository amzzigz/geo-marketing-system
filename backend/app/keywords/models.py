"""核心主词ORM模型"""

from datetime import datetime

from sqlalchemy import BigInteger, String, Integer, SmallInteger, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class CoreKeyword(Base):
    __tablename__ = "mkt_core_keywords"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    keyword: Mapped[str] = mapped_column(String(100), nullable=False)
    target_word: Mapped[str | None] = mapped_column(String(200), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(50), nullable=True)
    related_product: Mapped[str | None] = mapped_column(String(200), nullable=True)
    target_region: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)
    generated_article_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)


class ExpansionKeyword(Base):
    __tablename__ = "mkt_keyword_expansions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    core_keyword_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    phrase: Mapped[str] = mapped_column(String(300), nullable=False)
    phrase_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    source: Mapped[str | None] = mapped_column(String(20), nullable=True)
    quality_score: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    status: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)
    used_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)


class Subword(Base):
    __tablename__ = "mkt_keyword_subwords"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    core_keyword_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    search_potential_score: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    source: Mapped[str] = mapped_column(String(20), nullable=False, default="ai")
    status: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)


class Combination(Base):
    __tablename__ = "mkt_keyword_combinations"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    core_keyword_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    subword_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    word: Mapped[str] = mapped_column(String(300), nullable=False)
    intent: Mapped[str | None] = mapped_column(String(30), nullable=True)
    priority: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    source: Mapped[str] = mapped_column(String(20), nullable=False, default="ai")
    article_status: Mapped[str | None] = mapped_column(String(20), nullable=True, default="unused")
    article_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    platform: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    generated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
