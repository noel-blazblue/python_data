"""数据库模块 - 统一导出常用类和函数"""

from src.db.models import Base, NewsArticle, NewsAnalysis, NewsSummary
from src.db.session import DatabaseManager, init_db, get_db, get_db_manager
from src.db.repositories import (
    ArticleRepository,
    AnalysisRepository,
    SummaryRepository,
)

__all__ = [
    # 模型
    'Base',
    'NewsArticle',
    'NewsAnalysis',
    'NewsSummary',
    # 数据库管理
    'DatabaseManager',
    'init_db',
    'get_db',
    'get_db_manager',
    # 数据访问层
    'ArticleRepository',
    'AnalysisRepository',
    'SummaryRepository',
]
