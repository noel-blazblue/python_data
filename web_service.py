"""
Web 服务模块
提供 REST API 和 Web 界面
"""
import os
import yaml
import asyncio
from datetime import datetime
from typing import Optional, Dict
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from loguru import logger

from database import DatabaseManager
from news_crawler import NewsCrawler
from ai_analyzer import AIAnalyzer

# 创建 FastAPI 应用
app = FastAPI(
    title="新闻分析服务 API",
    description="新闻抓取、存储和 AI 分析服务",
    version="1.0.0"
)

# 全局服务实例
db_manager = None
crawler = None
analyzer = None
config = None


class TaskResponse(BaseModel):
    """任务响应模型"""
    success: bool
    message: str
    task_id: Optional[str] = None
    data: Optional[Dict] = None


class ArticleResponse(BaseModel):
    """文章响应模型"""
    id: int
    title: str
    summary: Optional[str]
    url: str
    source: str
    source_type: str
    published_at: Optional[datetime]
    crawled_at: datetime
    is_analyzed: bool


class AnalysisResponse(BaseModel):
    """分析响应模型"""
    id: int
    article_id: int
    analysis_content: str
    sentiment: Optional[str]
    sentiment_score: Optional[float]
    created_at: datetime


def init_services(config_path='app_config.yaml'):
    """初始化服务组件"""
    global db_manager, crawler, analyzer, config
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    db_manager = DatabaseManager(config_path)
    crawler = NewsCrawler(config_path)
    analyzer = AIAnalyzer(config_path)
    
    logger.info("Web 服务组件初始化完成")


@app.on_event("startup")
async def startup_event():
    """启动时初始化"""
    init_services()


@app.get("/", response_class=HTMLResponse)
async def root():
    """Web 界面首页"""
    html_content = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>新闻分析服务</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            .header {
                background: white;
                padding: 30px;
                border-radius: 10px;
                margin-bottom: 20px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .header h1 {
                color: #333;
                margin-bottom: 10px;
            }
            .header p {
                color: #666;
            }
            .card {
                background: white;
                padding: 25px;
                border-radius: 10px;
                margin-bottom: 20px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .card h2 {
                color: #333;
                margin-bottom: 15px;
                font-size: 1.5em;
            }
            .button-group {
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
            }
            button {
                padding: 12px 24px;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-size: 16px;
                transition: all 0.3s;
                font-weight: 500;
            }
            .btn-primary {
                background: #667eea;
                color: white;
            }
            .btn-primary:hover {
                background: #5568d3;
                transform: translateY(-2px);
            }
            .btn-success {
                background: #48bb78;
                color: white;
            }
            .btn-success:hover {
                background: #38a169;
                transform: translateY(-2px);
            }
            .btn-info {
                background: #4299e1;
                color: white;
            }
            .btn-info:hover {
                background: #3182ce;
                transform: translateY(-2px);
            }
            .btn-danger {
                background: #f56565;
                color: white;
            }
            .btn-danger:hover {
                background: #e53e3e;
                transform: translateY(-2px);
            }
            button:disabled {
                opacity: 0.6;
                cursor: not-allowed;
            }
            .status {
                margin-top: 15px;
                padding: 15px;
                border-radius: 6px;
                display: none;
            }
            .status.success {
                background: #c6f6d5;
                color: #22543d;
                border: 1px solid #9ae6b4;
            }
            .status.error {
                background: #fed7d7;
                color: #742a2a;
                border: 1px solid #fc8181;
            }
            .status.info {
                background: #bee3f8;
                color: #2c5282;
                border: 1px solid #90cdf4;
            }
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-top: 15px;
            }
            .stat-item {
                background: #f7fafc;
                padding: 15px;
                border-radius: 6px;
                text-align: center;
            }
            .stat-value {
                font-size: 2em;
                font-weight: bold;
                color: #667eea;
            }
            .stat-label {
                color: #666;
                margin-top: 5px;
            }
            .loading {
                display: inline-block;
                width: 20px;
                height: 20px;
                border: 3px solid rgba(255,255,255,.3);
                border-radius: 50%;
                border-top-color: #fff;
                animation: spin 1s ease-in-out infinite;
            }
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📰 新闻分析服务</h1>
                <p>新闻抓取、存储和 AI 分析平台</p>
            </div>

            <div class="card">
                <h2>📊 统计信息</h2>
                <div class="stats" id="stats">
                    <div class="stat-item">
                        <div class="stat-value" id="total-articles">-</div>
                        <div class="stat-label">总文章数</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value" id="analyzed-articles">-</div>
                        <div class="stat-label">已分析</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value" id="total-analyses">-</div>
                        <div class="stat-label">分析结果</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value" id="today-articles">-</div>
                        <div class="stat-label">今日新增</div>
                    </div>
                </div>
            </div>

            <div class="card">
                <h2>🔄 新闻爬虫</h2>
                <p style="color: #666; margin-bottom: 15px;">手动触发新闻抓取任务</p>
                <div class="button-group">
                    <button class="btn-primary" onclick="fetchNews()">开始抓取新闻</button>
                    <button class="btn-info" onclick="loadStats()">刷新统计</button>
                </div>
                <div class="status" id="fetch-status"></div>
            </div>

            <div class="card">
                <h2>🤖 AI 分析</h2>
                <p style="color: #666; margin-bottom: 15px;">对未分析的新闻进行 AI 分析</p>
                <div class="button-group">
                    <button class="btn-success" onclick="analyzeNews()">开始分析</button>
                    <button class="btn-info" onclick="loadStats()">刷新统计</button>
                </div>
                <div class="status" id="analysis-status"></div>
            </div>

            <div class="card">
                <h2>📋 数据查看</h2>
                <p style="color: #666; margin-bottom: 15px;">查看新闻和分析结果</p>
                <div class="button-group">
                    <button class="btn-info" onclick="window.location.href='/news'">浏览新闻列表</button>
                    <button class="btn-info" onclick="window.open('/api/analyses?limit=20', '_blank')">查看分析结果</button>
                    <button class="btn-info" onclick="window.open('/docs', '_blank')">API 文档</button>
                </div>
            </div>
        </div>

        <script>
            // 加载统计信息
            async function loadStats() {
                try {
                    const response = await fetch('/api/stats');
                    const data = await response.json();
                    
                    document.getElementById('total-articles').textContent = data.total_articles || 0;
                    document.getElementById('analyzed-articles').textContent = data.analyzed_count || 0;
                    document.getElementById('total-analyses').textContent = data.total_analyses || 0;
                    document.getElementById('today-articles').textContent = data.today_articles || 0;
                } catch (error) {
                    console.error('加载统计信息失败:', error);
                }
            }

            // 抓取新闻
            async function fetchNews() {
                const statusDiv = document.getElementById('fetch-status');
                statusDiv.className = 'status info';
                statusDiv.style.display = 'block';
                statusDiv.innerHTML = '<span class="loading"></span> 正在抓取新闻，请稍候...';
                
                try {
                    const response = await fetch('/api/fetch', { method: 'POST' });
                    const data = await response.json();
                    
                    if (data.success) {
                        statusDiv.className = 'status success';
                        statusDiv.textContent = `✅ ${data.message} (新增 ${data.data?.saved_count || 0} 篇)`;
                    } else {
                        statusDiv.className = 'status error';
                        statusDiv.textContent = `❌ ${data.message}`;
                    }
                    
                    // 刷新统计
                    setTimeout(loadStats, 1000);
                } catch (error) {
                    statusDiv.className = 'status error';
                    statusDiv.textContent = `❌ 请求失败: ${error.message}`;
                }
            }

            // 分析新闻
            async function analyzeNews() {
                const statusDiv = document.getElementById('analysis-status');
                statusDiv.className = 'status info';
                statusDiv.style.display = 'block';
                statusDiv.innerHTML = '<span class="loading"></span> 正在分析新闻，请稍候...';
                
                try {
                    const response = await fetch('/api/analyze', { method: 'POST' });
                    const data = await response.json();
                    
                    if (data.success) {
                        statusDiv.className = 'status success';
                        statusDiv.textContent = `✅ ${data.message} (分析 ${data.data?.analyzed_count || 0} 篇)`;
                    } else {
                        statusDiv.className = 'status error';
                        statusDiv.textContent = `❌ ${data.message}`;
                    }
                    
                    // 刷新统计
                    setTimeout(loadStats, 1000);
                } catch (error) {
                    statusDiv.className = 'status error';
                    statusDiv.textContent = `❌ 请求失败: ${error.message}`;
                }
            }

            // 页面加载时获取统计信息
            loadStats();
            // 每30秒自动刷新统计
            setInterval(loadStats, 30000);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/api/stats")
async def get_stats():
    """获取统计信息"""
    try:
        session = db_manager.get_session()
        try:
            from database import NewsArticle, NewsAnalysis
            from sqlalchemy import func
            
            # 总文章数
            total_articles = session.query(NewsArticle).count()
            
            # 已分析文章数
            analyzed_count = session.query(NewsArticle).filter_by(is_analyzed=True).count()
            
            # 分析结果数
            total_analyses = session.query(NewsAnalysis).count()
            
            # 今日新增
            today = datetime.now().date()
            today_articles = session.query(NewsArticle).filter(
                func.date(NewsArticle.crawled_at) == today
            ).count()
            
            return {
                "total_articles": total_articles,
                "analyzed_count": analyzed_count,
                "total_analyses": total_analyses,
                "today_articles": today_articles
            }
        finally:
            session.close()
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/fetch", response_model=TaskResponse)
async def fetch_news():
    """手动触发新闻抓取"""
    try:
        logger.info("Web API: 开始抓取新闻")
        
        # 在后台执行抓取任务
        def do_fetch():
            try:
                articles = crawler.crawl_all_sources()
                saved_count = 0
                for article in articles:
                    try:
                        article['summary'] = crawler.extract_summary(article)
                        saved_article = db_manager.add_article(article)
                        if saved_article:
                            saved_count += 1
                    except Exception as e:
                        logger.error(f"保存文章失败: {e}")
                        continue
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


@app.post("/api/analyze", response_model=TaskResponse)
async def analyze_news():
    """手动触发 AI 分析"""
    try:
        logger.info("Web API: 开始分析新闻")
        
        def do_analyze():
            try:
                articles = db_manager.get_unanalyzed_articles(limit=20)
                
                if not articles:
                    return 0
                
                analyzed_count = 0
                for article in articles:
                    try:
                        article_dict = {
                            'title': article.title,
                            'summary': article.summary,
                            'content': article.content,
                            'source': article.source
                        }
                        
                        analysis_result = analyzer.analyze_single_article(article_dict)
                        
                        if analysis_result:
                            db_manager.save_analysis(article.id, analysis_result)
                            analyzed_count += 1
                    except Exception as e:
                        logger.error(f"分析文章失败 {article.id}: {e}")
                        continue
                
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


@app.get("/api/articles")
async def get_articles(
    limit: int = 20,
    offset: int = 0,
    source: Optional[str] = None,
    source_type: Optional[str] = None,
    analyzed: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = "published_at",
    order: str = "desc"
):
    """获取新闻列表"""
    try:
        session = db_manager.get_session()
        try:
            from database import NewsArticle
            from sqlalchemy import or_, desc, asc
            
            query = session.query(NewsArticle)
            
            # 搜索功能
            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    or_(
                        NewsArticle.title.like(search_term),
                        NewsArticle.summary.like(search_term)
                    )
                )
            
            # 过滤功能
            if source:
                query = query.filter(NewsArticle.source == source)
            
            if source_type:
                query = query.filter(NewsArticle.source_type == source_type)
            
            if analyzed is not None:
                # 处理字符串 "true"/"false"
                if isinstance(analyzed, str):
                    analyzed = analyzed.lower() == "true"
                query = query.filter(NewsArticle.is_analyzed == analyzed)
            
            # 排序
            if sort_by == "published_at":
                order_func = desc if order == "desc" else asc
                query = query.order_by(order_func(NewsArticle.published_at))
            elif sort_by == "crawled_at":
                order_func = desc if order == "desc" else asc
                query = query.order_by(order_func(NewsArticle.crawled_at))
            elif sort_by == "title":
                order_func = asc if order == "asc" else desc
                query = query.order_by(order_func(NewsArticle.title))
            
            total = query.count()
            articles = query.offset(offset).limit(limit).all()
            
            # 获取分析结果
            from database import NewsAnalysis
            result_articles = []
            for a in articles:
                article_data = {
                    "id": a.id,
                    "title": a.title,
                    "summary": a.summary,
                    "url": a.url,
                    "source": a.source,
                    "source_type": a.source_type,
                    "published_at": a.published_at.isoformat() if a.published_at else None,
                    "crawled_at": a.crawled_at.isoformat() if a.crawled_at else None,
                    "is_analyzed": a.is_analyzed
                }
                
                # 如果有分析结果，添加分析摘要
                if a.is_analyzed:
                    analysis = session.query(NewsAnalysis).filter_by(article_id=a.id).first()
                    if analysis:
                        article_data["analysis"] = {
                            "sentiment": analysis.sentiment,
                            "sentiment_score": analysis.sentiment_score,
                            "analysis_preview": analysis.analysis_content[:200] + "..." if len(analysis.analysis_content) > 200 else analysis.analysis_content
                        }
                
                result_articles.append(article_data)
            
            return {
                "total": total,
                "offset": offset,
                "limit": limit,
                "articles": result_articles
            }
        finally:
            session.close()
    except Exception as e:
        logger.error(f"获取文章列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sources")
async def get_sources():
    """获取所有新闻源列表"""
    try:
        session = db_manager.get_session()
        try:
            from database import NewsArticle
            from sqlalchemy import distinct
            
            sources = session.query(
                distinct(NewsArticle.source),
                NewsArticle.source_type
            ).all()
            
            return {
                "sources": [
                    {"name": s[0], "type": s[1]}
                    for s in sources
                ]
            }
        finally:
            session.close()
    except Exception as e:
        logger.error(f"获取新闻源列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analyses")
async def get_analyses(limit: int = 20, offset: int = 0):
    """获取分析结果列表"""
    try:
        session = db_manager.get_session()
        try:
            from database import NewsAnalysis, NewsArticle
            
            total = session.query(NewsAnalysis).count()
            analyses = session.query(NewsAnalysis).order_by(
                NewsAnalysis.created_at.desc()
            ).offset(offset).limit(limit).all()
            
            result = []
            for analysis in analyses:
                article = session.query(NewsArticle).filter_by(id=analysis.article_id).first()
                result.append({
                    "id": analysis.id,
                    "article_id": analysis.article_id,
                    "article_title": article.title if article else "未知",
                    "analysis_content": analysis.analysis_content,
                    "sentiment": analysis.sentiment,
                    "sentiment_score": analysis.sentiment_score,
                    "created_at": analysis.created_at.isoformat() if analysis.created_at else None
                })
            
            return {
                "total": total,
                "offset": offset,
                "limit": limit,
                "analyses": result
            }
        finally:
            session.close()
    except Exception as e:
        logger.error(f"获取分析结果失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/news", response_class=HTMLResponse)
async def news_list_page(
    page: int = 1,
    limit: int = 20,
    source: Optional[str] = None,
    source_type: Optional[str] = None,
    analyzed: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = "published_at",
    order: str = "desc"
):
    """新闻列表浏览页面"""
    html_content = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>新闻列表 - 新闻分析服务</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                background: #f5f7fa;
                color: #333;
                line-height: 1.6;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px 0;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .header-content {
                max-width: 1200px;
                margin: 0 auto;
                padding: 0 20px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .header h1 {
                font-size: 24px;
                font-weight: 600;
            }
            .header a {
                color: white;
                text-decoration: none;
                padding: 8px 16px;
                background: rgba(255,255,255,0.2);
                border-radius: 6px;
                transition: background 0.3s;
            }
            .header a:hover {
                background: rgba(255,255,255,0.3);
            }
            .container {
                max-width: 1200px;
                margin: 30px auto;
                padding: 0 20px;
            }
            .filters {
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            .filter-row {
                display: flex;
                gap: 15px;
                flex-wrap: wrap;
                margin-bottom: 15px;
            }
            .filter-group {
                flex: 1;
                min-width: 200px;
            }
            .filter-group label {
                display: block;
                margin-bottom: 5px;
                font-weight: 500;
                color: #555;
                font-size: 14px;
            }
            .filter-group input,
            .filter-group select {
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 6px;
                font-size: 14px;
                transition: border-color 0.3s;
            }
            .filter-group input:focus,
            .filter-group select:focus {
                outline: none;
                border-color: #667eea;
            }
            .btn {
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 500;
                transition: all 0.3s;
            }
            .btn-primary {
                background: #667eea;
                color: white;
            }
            .btn-primary:hover {
                background: #5568d3;
                transform: translateY(-1px);
            }
            .btn-secondary {
                background: #e2e8f0;
                color: #4a5568;
            }
            .btn-secondary:hover {
                background: #cbd5e0;
            }
            .news-list {
                display: flex;
                flex-direction: column;
                gap: 15px;
            }
            .news-item {
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                transition: all 0.3s;
                cursor: pointer;
                border-left: 4px solid transparent;
            }
            .news-item:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                border-left-color: #667eea;
            }
            .news-item.analyzed {
                border-left-color: #48bb78;
            }
            .news-header {
                display: flex;
                justify-content: space-between;
                align-items: start;
                margin-bottom: 10px;
            }
            .news-title {
                font-size: 18px;
                font-weight: 600;
                color: #2d3748;
                margin-bottom: 8px;
                line-height: 1.4;
            }
            .news-title a {
                color: #2d3748;
                text-decoration: none;
                transition: color 0.3s;
            }
            .news-title a:hover {
                color: #667eea;
            }
            .news-meta {
                display: flex;
                gap: 15px;
                font-size: 13px;
                color: #718096;
                flex-wrap: wrap;
            }
            .news-meta span {
                display: flex;
                align-items: center;
                gap: 5px;
            }
            .badge {
                display: inline-block;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: 500;
            }
            .badge-source {
                background: #e6fffa;
                color: #234e52;
            }
            .badge-analyzed {
                background: #c6f6d5;
                color: #22543d;
            }
            .badge-sentiment {
                background: #fed7d7;
                color: #742a2a;
            }
            .badge-sentiment.positive {
                background: #c6f6d5;
                color: #22543d;
            }
            .badge-sentiment.neutral {
                background: #feebc8;
                color: #7c2d12;
            }
            .news-summary {
                color: #4a5568;
                margin: 12px 0;
                line-height: 1.6;
            }
            .news-analysis {
                margin-top: 12px;
                padding: 12px;
                background: #f7fafc;
                border-radius: 6px;
                border-left: 3px solid #48bb78;
            }
            .news-analysis-title {
                font-weight: 600;
                color: #2d3748;
                margin-bottom: 8px;
                font-size: 14px;
            }
            .news-analysis-content {
                color: #4a5568;
                font-size: 13px;
                line-height: 1.6;
            }
            .pagination {
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 10px;
                margin-top: 30px;
                padding: 20px;
            }
            .pagination button {
                padding: 8px 16px;
                border: 1px solid #ddd;
                background: white;
                border-radius: 6px;
                cursor: pointer;
                transition: all 0.3s;
            }
            .pagination button:hover:not(:disabled) {
                background: #667eea;
                color: white;
                border-color: #667eea;
            }
            .pagination button:disabled {
                opacity: 0.5;
                cursor: not-allowed;
            }
            .pagination .page-info {
                padding: 8px 16px;
                color: #718096;
            }
            .loading {
                text-align: center;
                padding: 40px;
                color: #718096;
            }
            .empty {
                text-align: center;
                padding: 60px 20px;
                color: #a0aec0;
            }
            .empty-icon {
                font-size: 48px;
                margin-bottom: 15px;
            }
            .external-link {
                color: #667eea;
                text-decoration: none;
                font-size: 13px;
                display: inline-flex;
                align-items: center;
                gap: 5px;
                margin-left: 10px;
            }
            .external-link:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <div class="header-content">
                <h1>📰 新闻列表</h1>
                <a href="/">返回首页</a>
            </div>
        </div>
        
        <div class="container">
            <div class="filters">
                <div class="filter-row">
                    <div class="filter-group">
                        <label>搜索</label>
                        <input type="text" id="search" placeholder="搜索标题或摘要..." value="">
                    </div>
                    <div class="filter-group">
                        <label>来源类型</label>
                        <select id="source_type">
                            <option value="">全部</option>
                            <option value="domestic">国内</option>
                            <option value="international">国际</option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <label>分析状态</label>
                        <select id="analyzed">
                            <option value="">全部</option>
                            <option value="true">已分析</option>
                            <option value="false">未分析</option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <label>排序方式</label>
                        <select id="sort_by">
                            <option value="published_at">发布时间</option>
                            <option value="crawled_at">抓取时间</option>
                            <option value="title">标题</option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <label>排序顺序</label>
                        <select id="order">
                            <option value="desc">降序</option>
                            <option value="asc">升序</option>
                        </select>
                    </div>
                </div>
                <div class="filter-row">
                    <button class="btn btn-primary" onclick="loadNews()">搜索</button>
                    <button class="btn btn-secondary" onclick="resetFilters()">重置</button>
                </div>
            </div>
            
            <div id="news-container">
                <div class="loading">加载中...</div>
            </div>
        </div>
        
        <script>
            let currentPage = 1;
            const pageSize = 20;
            
            // 从 URL 参数获取初始值
            function getUrlParams() {
                const params = new URLSearchParams(window.location.search);
                return {
                    page: parseInt(params.get('page')) || 1,
                    search: params.get('search') || '',
                    source_type: params.get('source_type') || '',
                    analyzed: params.get('analyzed') || '',
                    sort_by: params.get('sort_by') || 'published_at',
                    order: params.get('order') || 'desc'
                };
            }
            
            // 初始化
            function init() {
                const params = getUrlParams();
                currentPage = params.page;
                document.getElementById('search').value = params.search;
                document.getElementById('source_type').value = params.source_type;
                document.getElementById('analyzed').value = params.analyzed;
                document.getElementById('sort_by').value = params.sort_by;
                document.getElementById('order').value = params.order;
                loadNews();
            }
            
            // 加载新闻
            async function loadNews(page = currentPage) {
                currentPage = page;
                const container = document.getElementById('news-container');
                container.innerHTML = '<div class="loading">加载中...</div>';
                
                const search = document.getElementById('search').value;
                const sourceType = document.getElementById('source_type').value;
                const analyzed = document.getElementById('analyzed').value;
                const sortBy = document.getElementById('sort_by').value;
                const order = document.getElementById('order').value;
                
                // 更新 URL
                const params = new URLSearchParams({
                    page: page,
                    limit: pageSize,
                    sort_by: sortBy,
                    order: order
                });
                if (search) params.set('search', search);
                if (sourceType) params.set('source_type', sourceType);
                if (analyzed) params.set('analyzed', analyzed);
                window.history.pushState({}, '', '/news?' + params.toString());
                
                try {
                    const url = `/api/articles?${params.toString()}`;
                    const response = await fetch(url);
                    const data = await response.json();
                    
                    if (data.articles.length === 0) {
                        container.innerHTML = `
                            <div class="empty">
                                <div class="empty-icon">📭</div>
                                <div>暂无新闻数据</div>
                            </div>
                        `;
                        return;
                    }
                    
                    let html = '<div class="news-list">';
                    data.articles.forEach(article => {
                        const publishedDate = article.published_at 
                            ? new Date(article.published_at).toLocaleString('zh-CN')
                            : '未知';
                        const analyzedClass = article.is_analyzed ? 'analyzed' : '';
                        const sentimentBadge = article.analysis 
                            ? `<span class="badge badge-sentiment ${article.analysis.sentiment}">${getSentimentText(article.analysis.sentiment)}</span>`
                            : '';
                        
                        html += `
                            <div class="news-item ${analyzedClass}" onclick="window.open('${article.url}', '_blank')">
                                <div class="news-header">
                                    <div style="flex: 1;">
                                        <div class="news-title">
                                            <a href="${article.url}" target="_blank" onclick="event.stopPropagation()">
                                                ${escapeHtml(article.title)}
                                            </a>
                                        </div>
                                        <div class="news-meta">
                                            <span>📅 ${publishedDate}</span>
                                            <span class="badge badge-source">${escapeHtml(article.source)}</span>
                                            ${article.is_analyzed ? '<span class="badge badge-analyzed">✓ 已分析</span>' : ''}
                                            ${sentimentBadge}
                                        </div>
                                    </div>
                                </div>
                                ${article.summary ? `<div class="news-summary">${escapeHtml(article.summary)}</div>` : ''}
                                ${article.analysis ? `
                                    <div class="news-analysis">
                                        <div class="news-analysis-title">🤖 AI 分析预览</div>
                                        <div class="news-analysis-content">${escapeHtml(article.analysis.analysis_preview)}</div>
                                    </div>
                                ` : ''}
                            </div>
                        `;
                    });
                    html += '</div>';
                    
                    // 分页
                    const totalPages = Math.ceil(data.total / pageSize);
                    html += renderPagination(totalPages, page, data.total);
                    
                    container.innerHTML = html;
                } catch (error) {
                    container.innerHTML = `<div class="empty">加载失败: ${error.message}</div>`;
                }
            }
            
            // 渲染分页
            function renderPagination(totalPages, current, total) {
                if (totalPages <= 1) return '';
                
                let html = '<div class="pagination">';
                html += `<button onclick="loadNews(${Math.max(1, current - 1)})" ${current === 1 ? 'disabled' : ''}>上一页</button>`;
                html += `<span class="page-info">第 ${current} / ${totalPages} 页 (共 ${total} 条)</span>`;
                html += `<button onclick="loadNews(${Math.min(totalPages, current + 1)})" ${current === totalPages ? 'disabled' : ''}>下一页</button>`;
                html += '</div>';
                return html;
            }
            
            // 重置过滤器
            function resetFilters() {
                document.getElementById('search').value = '';
                document.getElementById('source_type').value = '';
                document.getElementById('analyzed').value = '';
                document.getElementById('sort_by').value = 'published_at';
                document.getElementById('order').value = 'desc';
                loadNews(1);
            }
            
            // 工具函数
            function escapeHtml(text) {
                if (!text) return '';
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }
            
            function getSentimentText(sentiment) {
                const map = {
                    'positive': '积极',
                    'negative': '消极',
                    'neutral': '中性'
                };
                return map[sentiment] || sentiment;
            }
            
            // 回车搜索
            document.addEventListener('DOMContentLoaded', function() {
                init();
                document.getElementById('search').addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') {
                        loadNews(1);
                    }
                });
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/api/article/{article_id}")
async def get_article(article_id: int):
    """获取单篇文章详情"""
    try:
        session = db_manager.get_session()
        try:
            from database import NewsArticle, NewsAnalysis
            
            article = session.query(NewsArticle).filter_by(id=article_id).first()
            if not article:
                raise HTTPException(status_code=404, detail="文章不存在")
            
            # 获取分析结果
            analysis = session.query(NewsAnalysis).filter_by(article_id=article_id).first()
            
            result = {
                "id": article.id,
                "title": article.title,
                "summary": article.summary,
                "content": article.content,
                "url": article.url,
                "source": article.source,
                "source_type": article.source_type,
                "published_at": article.published_at.isoformat() if article.published_at else None,
                "crawled_at": article.crawled_at.isoformat() if article.crawled_at else None,
                "is_analyzed": article.is_analyzed
            }
            
            if analysis:
                result["analysis"] = {
                    "id": analysis.id,
                    "analysis_content": analysis.analysis_content,
                    "sentiment": analysis.sentiment,
                    "sentiment_score": analysis.sentiment_score,
                    "created_at": analysis.created_at.isoformat() if analysis.created_at else None
                }
            
            return result
        finally:
            session.close()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取文章详情失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    # 从配置文件读取端口
    with open('app_config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    web_config = config.get('web', {})
    host = web_config.get('host', '0.0.0.0')
    port = web_config.get('port', 8000)
    
    uvicorn.run(app, host=host, port=port)
