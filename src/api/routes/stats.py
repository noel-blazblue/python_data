"""
统计信息路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from loguru import logger

from src.db import get_db
from src.db.repositories import ArticleRepository, AnalysisRepository
from src.api.schemas.common import StatsResponse

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("", response_model=StatsResponse)
async def get_stats(db: Session = Depends(get_db)):
    """获取统计信息"""
    try:
        article_repo = ArticleRepository(db)
        analysis_repo = AnalysisRepository(db)
        
        stats = article_repo.get_stats()
        total_analyses = analysis_repo.get_stats()
        
        return {
            "total_articles": stats['total_articles'],
            "analyzed_count": stats['analyzed_count'],
            "total_analyses": total_analyses,
            "today_articles": stats['today_articles']
        }
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
