"""
文章相关的 Pydantic 模型
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class ArticleResponse(BaseModel):
    """文章响应模型"""
    id: int
    title: str
    summary: Optional[str] = None
    content: Optional[str] = None
    url: str
    source: str
    source_type: Optional[str] = None
    published_at: Optional[datetime] = None
    crawled_at: datetime
    language: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    is_analyzed: bool = False
    
    class Config:
        from_attributes = True


class ArticleWithAnalysis(ArticleResponse):
    """带分析结果的文章响应模型"""
    analysis: Optional['AnalysisPreview'] = None


class AnalysisPreview(BaseModel):
    """分析预览模型"""
    sentiment: Optional[str] = None
    sentiment_score: Optional[float] = None
    analysis_preview: Optional[str] = Field(None, description="分析内容预览（前200字）")


class ArticleListResponse(BaseModel):
    """文章列表响应模型"""
    total: int
    offset: int
    limit: int
    articles: List[ArticleResponse]


# 更新前向引用
ArticleWithAnalysis.model_rebuild()
