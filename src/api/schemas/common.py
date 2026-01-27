"""
通用响应模型
"""
from typing import Optional, Dict
from pydantic import BaseModel


class TaskResponse(BaseModel):
    """任务响应模型"""
    success: bool
    message: str
    task_id: Optional[str] = None
    data: Optional[Dict] = None


class StatsResponse(BaseModel):
    """统计信息响应模型"""
    total_articles: int
    analyzed_count: int
    total_analyses: int
    today_articles: int
