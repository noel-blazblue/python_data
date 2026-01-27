"""
数据库会话管理
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator, Optional

from src.db.models import Base


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, database_url: str):
        """
        初始化数据库管理器
        
        Args:
            database_url: 数据库连接 URL
        """
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False
        )
        # 创建表
        Base.metadata.create_all(self.engine)
    
    def get_session(self) -> Session:
        """获取数据库会话"""
        return self.SessionLocal()
    
    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """
        上下文管理器，自动处理提交和回滚
        
        使用示例:
            with db_manager.session_scope() as session:
                # 使用 session
                pass
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


# 全局数据库管理器实例（在应用启动时初始化）
_db_manager: Optional[DatabaseManager] = None


def init_db(database_url: str):
    """
    初始化数据库
    
    Args:
        database_url: 数据库连接 URL
    """
    global _db_manager
    _db_manager = DatabaseManager(database_url)


def get_db() -> Generator[Session, None, None]:
    """
    依赖注入：获取数据库会话（用于 FastAPI）
    
    使用示例:
        @app.get("/articles")
        def get_articles(db: Session = Depends(get_db)):
            # 使用 db
            pass
    """
    if _db_manager is None:
        raise RuntimeError("数据库未初始化，请先调用 init_db()")
    
    session = _db_manager.get_session()
    try:
        yield session
    finally:
        session.close()


def get_db_manager() -> DatabaseManager:
    """获取数据库管理器实例"""
    if _db_manager is None:
        raise RuntimeError("数据库未初始化，请先调用 init_db()")
    return _db_manager
