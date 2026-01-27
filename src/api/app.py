"""
Web 服务应用（重构版）
"""
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from loguru import logger

from src.config import get_settings
from src.core.logging import setup_logging
from src.db import init_db
from src.api.routes import articles_router, analysis_router, stats_router, tasks_router
from src.api.views import get_home_page, get_news_list_page

# 创建 FastAPI 应用
app = FastAPI(
    title="新闻分析服务 API",
    description="新闻抓取、存储和 AI 分析服务",
    version="2.0.0"
)


@app.on_event("startup")
async def startup_event():
    """启动时初始化"""
    config = get_settings()
    
    # 配置日志
    setup_logging(
        log_level=config.app.log_level,
        log_dir='logs'
    )
    
    # 初始化数据库
    database_url = config.database.get_url()
    init_db(database_url)
    
    logger.info("Web 服务启动完成")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Web 界面首页"""
    return get_home_page()


@app.get("/news", response_class=HTMLResponse)
async def news_list_page(
    page: int = 1,
    limit: int = 20,
    source: str = None,
    source_type: str = None,
    category: str = None,
    analyzed: str = None,
    search: str = None,
    sort_by: str = "published_at",
    order: str = "desc"
):
    """新闻列表浏览页面"""
    return get_news_list_page(
        page=page,
        limit=limit,
        source=source,
        source_type=source_type,
        category=category,
        analyzed=analyzed,
        search=search,
        sort_by=sort_by,
        order=order
    )


# 注册路由
app.include_router(articles_router)
app.include_router(analysis_router)
app.include_router(stats_router)
app.include_router(tasks_router)
