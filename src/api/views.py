"""
前端页面视图
"""
from fastapi.responses import HTMLResponse


def get_home_page() -> HTMLResponse:
    """获取首页 HTML"""
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
                    
                    setTimeout(loadStats, 1000);
                } catch (error) {
                    statusDiv.className = 'status error';
                    statusDiv.textContent = `❌ 请求失败: ${error.message}`;
                }
            }

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
                    
                    setTimeout(loadStats, 1000);
                } catch (error) {
                    statusDiv.className = 'status error';
                    statusDiv.textContent = `❌ 请求失败: ${error.message}`;
                }
            }

            loadStats();
            setInterval(loadStats, 30000);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


def get_news_list_page(**kwargs) -> HTMLResponse:
    """获取新闻列表页面 HTML（完整版，包含筛选功能）"""
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
                        <label>新闻源</label>
                        <select id="source">
                            <option value="">全部</option>
                        </select>
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
                        <label>分类</label>
                        <select id="category">
                            <option value="">全部</option>
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
            
            // 加载筛选选项数据
            async function loadFilterOptions() {
                try {
                    // 加载新闻源列表
                    const sourcesResponse = await fetch('/api/articles/sources/list');
                    const sourcesData = await sourcesResponse.json();
                    const sourceSelect = document.getElementById('source');
                    
                    // 清空现有选项（除了"全部"）
                    while (sourceSelect.children.length > 1) {
                        sourceSelect.removeChild(sourceSelect.lastChild);
                    }
                    
                    // 使用 Set 确保去重
                    const seenSources = new Set();
                    sourcesData.sources.forEach(s => {
                        if (!seenSources.has(s.name)) {
                            seenSources.add(s.name);
                            const option = document.createElement('option');
                            option.value = s.name;
                            option.textContent = s.name;
                            sourceSelect.appendChild(option);
                        }
                    });
                    
                    // 加载分类列表
                    const categoriesResponse = await fetch('/api/articles/categories/list');
                    const categoriesData = await categoriesResponse.json();
                    const categorySelect = document.getElementById('category');
                    
                    // 清空现有选项（除了"全部"）
                    while (categorySelect.children.length > 1) {
                        categorySelect.removeChild(categorySelect.lastChild);
                    }
                    
                    // 使用 Set 确保去重
                    const seenCategories = new Set();
                    categoriesData.categories.forEach(c => {
                        if (!seenCategories.has(c)) {
                            seenCategories.add(c);
                            const option = document.createElement('option');
                            option.value = c;
                            option.textContent = c;
                            categorySelect.appendChild(option);
                        }
                    });
                } catch (error) {
                    console.error('加载筛选选项失败:', error);
                }
            }
            
            // 从 URL 参数获取初始值
            function getUrlParams() {
                const params = new URLSearchParams(window.location.search);
                return {
                    page: parseInt(params.get('page')) || 1,
                    search: params.get('search') || '',
                    source: params.get('source') || '',
                    source_type: params.get('source_type') || '',
                    category: params.get('category') || '',
                    analyzed: params.get('analyzed') || '',
                    sort_by: params.get('sort_by') || 'published_at',
                    order: params.get('order') || 'desc'
                };
            }
            
            // 初始化
            async function init() {
                await loadFilterOptions();
                const params = getUrlParams();
                currentPage = params.page;
                document.getElementById('search').value = params.search;
                document.getElementById('source').value = params.source;
                document.getElementById('source_type').value = params.source_type;
                document.getElementById('category').value = params.category;
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
                const source = document.getElementById('source').value;
                const sourceType = document.getElementById('source_type').value;
                const category = document.getElementById('category').value;
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
                if (source) params.set('source', source);
                if (sourceType) params.set('source_type', sourceType);
                if (category) params.set('category', category);
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
                                        </div>
                                    </div>
                                </div>
                                ${article.summary ? `<div class="news-summary">${escapeHtml(article.summary)}</div>` : ''}
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
                document.getElementById('source').value = '';
                document.getElementById('source_type').value = '';
                document.getElementById('category').value = '';
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
