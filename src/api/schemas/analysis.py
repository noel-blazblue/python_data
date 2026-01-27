"""
分析结果相关的 Pydantic 模型
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class AnalysisResponse(BaseModel):
    """分析响应模型"""
    id: int
    article_id: int
    article_title: Optional[str] = None
    analysis_type: Optional[str] = None
    analysis_content: str
    sentiment: Optional[str] = None
    sentiment_score: Optional[float] = None
    key_points: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class AnalysisListResponse(BaseModel):
    """分析结果列表响应模型"""
    total: int
    offset: int
    limit: int
    analyses: List[AnalysisResponse]
