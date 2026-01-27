"""
数据模型层
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


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


class NewsAnalysis(Base):
    """新闻分析结果模型"""
    __tablename__ = 'news_analysis'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(Integer, nullable=False, index=True)  # 关联的文章ID
    analysis_type = Column(String(50), default='general')  # 分析类型
    analysis_content = Column(Text, nullable=False)  # 分析内容
    sentiment = Column(String(20))  # 情感分析：positive/negative/neutral
    sentiment_score = Column(Float)  # 情感分数
    key_points = Column(Text)  # 关键要点（JSON格式）
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<NewsAnalysis(article_id={self.article_id}, sentiment='{self.sentiment}')>"


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
