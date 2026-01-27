"""
文章相关路由
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from loguru import logger

from src.db import get_db
from src.db.repositories import ArticleRepository, AnalysisRepository
from src.api.schemas.article import ArticleResponse, ArticleListResponse, ArticleWithAnalysis

router = APIRouter(prefix="/api/articles", tags=["articles"])


@router.get("", response_model=ArticleListResponse)
async def get_articles(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    source: Optional[str] = None,
    source_type: Optional[str] = None,
    category: Optional[str] = None,
    analyzed: Optional[bool] = None,
    search: Optional[str] = None,
    sort_by: str = Query("published_at", regex="^(published_at|crawled_at|title)$"),
    order: str = Query("desc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db)
):
    """获取新闻列表"""
    try:
        article_repo = ArticleRepository(db)
        
        # 处理 analyzed 参数（可能是字符串 "true"/"false"）
        if isinstance(analyzed, str):
            analyzed = analyzed.lower() == "true"
        
        articles, total = article_repo.search(
            keyword=search,
            source=source,
            source_type=source_type,
            category=category,
            analyzed=analyzed,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            order=order
        )
        
        return {
            "total": total,
            "offset": offset,
            "limit": limit,
            "articles": [
                ArticleResponse(
                    id=a.id,
                    title=a.title,
                    summary=a.summary,
                    content=a.content,
                    url=a.url,
                    source=a.source,
                    source_type=a.source_type,
                    published_at=a.published_at,
                    crawled_at=a.crawled_at,
                    language=a.language,
                    category=a.category,
                    tags=a.tags,
                    is_analyzed=a.is_analyzed
                )
                for a in articles
            ]
        }
    except Exception as e:
        logger.error(f"获取文章列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{article_id}", response_model=ArticleWithAnalysis)
async def get_article(
    article_id: int,
    db: Session = Depends(get_db)
):
    """获取单篇文章详情"""
    try:
        article_repo = ArticleRepository(db)
        analysis_repo = AnalysisRepository(db)
        
        article = article_repo.get_by_id(article_id)
        if not article:
            raise HTTPException(status_code=404, detail="文章不存在")
        
        # 获取分析结果
        analysis = analysis_repo.get_by_article_id(article_id)
        
        result = ArticleWithAnalysis(
            id=article.id,
            title=article.title,
            summary=article.summary,
            content=article.content,
            url=article.url,
            source=article.source,
            source_type=article.source_type,
            published_at=article.published_at,
            crawled_at=article.crawled_at,
            language=article.language,
            category=article.category,
            tags=article.tags,
            is_analyzed=article.is_analyzed
        )
        
        if analysis:
            analysis_preview = analysis.analysis_content[:200] + "..." if len(analysis.analysis_content) > 200 else analysis.analysis_content
            result.analysis = {
                "sentiment": analysis.sentiment,
                "sentiment_score": analysis.sentiment_score,
                "analysis_preview": analysis_preview
            }
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取文章详情失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sources/list")
async def get_sources(db: Session = Depends(get_db)):
    """获取所有新闻源列表（去重）"""
    try:
        from src.db.models import NewsArticle
        from sqlalchemy import distinct, func
        
        # 使用 group_by 确保去重，并获取每个源的类型
        sources = db.query(
            NewsArticle.source,
            NewsArticle.source_type
        ).group_by(
            NewsArticle.source,
            NewsArticle.source_type
        ).all()
        
        # 进一步去重：如果同一个源有多个类型，只保留第一个
        seen = set()
        unique_sources = []
        for source, source_type in sources:
            if source not in seen:
                seen.add(source)
                unique_sources.append({"name": source, "type": source_type})
        
        return {
            "sources": unique_sources
        }
    except Exception as e:
        logger.error(f"获取新闻源列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories/list")
async def get_categories(db: Session = Depends(get_db)):
    """获取所有分类列表（去重）"""
    try:
        from src.db.models import NewsArticle
        from sqlalchemy import distinct
        
        categories = db.query(
            distinct(NewsArticle.category)
        ).filter(
            NewsArticle.category.isnot(None)
        ).all()
        
        # 去重并过滤空值
        unique_categories = list(set([c[0] for c in categories if c[0]]))
        unique_categories.sort()  # 排序以便显示
        
        return {
            "categories": unique_categories
        }
    except Exception as e:
        logger.error(f"获取分类列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
