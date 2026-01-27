"""
任务相关路由（抓取、分析等）
"""
import asyncio
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from loguru import logger

from src.db import get_db_manager
from src.config import get_settings
from src.services import CrawlerService, AnalysisService
from src.crawlers import RSSCrawler, PlatformCrawler
from src.analyzers import AIAnalyzer
from src.api.schemas.common import TaskResponse

router = APIRouter(prefix="/api", tags=["tasks"])


def get_crawler_service():
    """获取抓取服务（依赖注入）"""
    config = get_settings()
    db_manager = get_db_manager()
    rss_crawler = RSSCrawler(config)
    platform_crawler = PlatformCrawler(config)
    
    return CrawlerService(
        db_manager=db_manager,
        rss_crawler=rss_crawler,
        platform_crawler=platform_crawler,
        config=config
    )


def get_analysis_service():
    """获取分析服务（依赖注入）"""
    config = get_settings()
    db_manager = get_db_manager()
    analyzer = AIAnalyzer(config)
    
    return AnalysisService(
        db_manager=db_manager,
        analyzer=analyzer,
        config=config
    )


@router.post("/fetch", response_model=TaskResponse)
async def fetch_news():
    """手动触发新闻抓取"""
    try:
        logger.info("Web API: 开始抓取新闻")
        
        crawler_service = get_crawler_service()
        
        # 在后台执行抓取任务
        def do_fetch():
            try:
                saved_count = crawler_service.fetch_all_sources()
                logger.info(f"Web API: 成功保存 {saved_count} 篇新文章")
                return saved_count
            except Exception as e:
                logger.error(f"Web API: 抓取失败: {e}")
                raise e
        
        # 使用 asyncio 在后台执行
        loop = asyncio.get_event_loop()
        saved_count = await loop.run_in_executor(None, do_fetch)
        
        return TaskResponse(
            success=True,
            message=f"成功抓取并保存 {saved_count} 篇新文章",
            data={"saved_count": saved_count}
        )
    except Exception as e:
        logger.error(f"抓取新闻失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze", response_model=TaskResponse)
async def analyze_news():
    """手动触发 AI 分析"""
    try:
        logger.info("Web API: 开始分析新闻")
        
        analysis_service = get_analysis_service()
        
        def do_analyze():
            try:
                analyzed_count = analysis_service.analyze_unanalyzed_articles()
                logger.info(f"Web API: 成功分析 {analyzed_count} 篇文章")
                return analyzed_count
            except Exception as e:
                logger.error(f"Web API: 分析失败: {e}")
                raise e
        
        loop = asyncio.get_event_loop()
        analyzed_count = await loop.run_in_executor(None, do_analyze)
        
        return TaskResponse(
            success=True,
            message=f"成功分析 {analyzed_count} 篇文章",
            data={"analyzed_count": analyzed_count}
        )
    except Exception as e:
        logger.error(f"分析新闻失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
