"""
分析结果相关路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from loguru import logger

from src.db import get_db
from src.db.repositories import AnalysisRepository, ArticleRepository
from src.api.schemas.analysis import AnalysisResponse, AnalysisListResponse

router = APIRouter(prefix="/api/analyses", tags=["analysis"])


@router.get("", response_model=AnalysisListResponse)
async def get_analyses(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """获取分析结果列表"""
    try:
        analysis_repo = AnalysisRepository(db)
        article_repo = ArticleRepository(db)
        
        analyses, total = analysis_repo.get_recent(limit=limit, offset=offset)
        
        result = []
        for analysis in analyses:
            article = article_repo.get_by_id(analysis.article_id)
            result.append({
                "id": analysis.id,
                "article_id": analysis.article_id,
                "article_title": article.title if article else "未知",
                "analysis_type": analysis.analysis_type,
                "analysis_content": analysis.analysis_content,
                "sentiment": analysis.sentiment,
                "sentiment_score": analysis.sentiment_score,
                "key_points": analysis.key_points,
                "created_at": analysis.created_at
            })
        
        return {
            "total": total,
            "offset": offset,
            "limit": limit,
            "analyses": result
        }
    except Exception as e:
        logger.error(f"获取分析结果失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
