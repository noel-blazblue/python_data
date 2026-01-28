from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from datetime import datetime
from src.db.models.base import Base

class NewsArticle(Base):
    """新闻文章模型"""
    __tablename__ = 'news_articles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False, index=True)
    summary = Column(Text)  # 摘要
    content = Column(Text)  # 完整内容（可选）
    url = Column(String(1000), unique=True, nullable=False, index=True)
    source = Column(String(200), nullable=False, index=True)  # 新闻源名称
    source_type = Column(String(50))  # 来源类型：domestic/international
    published_at = Column(DateTime, index=True)  # 发布时间
    crawled_at = Column(DateTime, default=datetime.utcnow, index=True)  # 抓取时间
    language = Column(String(20), default='zh')  # 语言：zh/en
    category = Column(String(100))  # 分类
    tags = Column(String(500))  # 标签（逗号分隔）
    
    # 状态字段
    is_analyzed = Column(Boolean, default=False, index=True)  # 是否已分析
    is_processed = Column(Boolean, default=False)  # 是否已处理
    
    def __repr__(self):
        return f"<NewsArticle(id={self.id}, title='{self.title[:50]}...', source='{self.source}')>"