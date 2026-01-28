from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime

from src.db.models.base import Base

class NewsSummary(Base):
    """新闻摘要表（用于批量分析）"""
    __tablename__ = 'news_summaries'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    summary_date = Column(DateTime, nullable=False, index=True)  # 摘要日期
    summary_type = Column(String(50), default='daily')  # 摘要类型：daily/weekly
    summary_content = Column(Text, nullable=False)  # 摘要内容
    article_count = Column(Integer, default=0)  # 包含的文章数量
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<NewsSummary(summary_date={self.summary_date}, type='{self.summary_type}')>"