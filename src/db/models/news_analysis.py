from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float
from datetime import datetime
from src.db.models.base import Base

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