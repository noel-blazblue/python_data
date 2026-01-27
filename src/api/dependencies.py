"""
API 依赖注入
"""
from typing import Generator
from sqlalchemy.orm import Session

from src.db import get_db
from src.db.repositories import ArticleRepository, AnalysisRepository, SummaryRepository


def get_article_repository(db: Session = None) -> ArticleRepository:
    """获取文章 Repository"""
    if db is None:
        db = next(get_db())
    return ArticleRepository(db)


def get_analysis_repository(db: Session = None) -> AnalysisRepository:
    """获取分析 Repository"""
    if db is None:
        db = next(get_db())
    return AnalysisRepository(db)


def get_summary_repository(db: Session = None) -> SummaryRepository:
    """获取摘要 Repository"""
    if db is None:
        db = next(get_db())
    return SummaryRepository(db)
