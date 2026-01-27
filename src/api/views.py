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
    """获取新闻列表页面 HTML（简化版，完整版可以从旧代码复制）"""
    # 这里返回一个简化版本，完整版本可以从旧的 web_service.py 复制
    html_content = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>新闻列表 - 新闻分析服务</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: #f5f7fa;
                padding: 20px;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            .news-item {
                background: white;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 15px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            .news-title {
                font-size: 18px;
                font-weight: 600;
                margin-bottom: 10px;
            }
            .news-title a {
                color: #2d3748;
                text-decoration: none;
            }
            .news-title a:hover {
                color: #667eea;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📰 新闻列表</h1>
                <a href="/" style="color: white;">返回首页</a>
            </div>
            <div id="news-container">
                <p>加载中...</p>
            </div>
        </div>
        <script>
            // 简化的加载逻辑，完整版可以从旧代码复制
            fetch('/api/articles?limit=20')
                .then(r => r.json())
                .then(data => {
                    const container = document.getElementById('news-container');
                    container.innerHTML = data.articles.map(a => `
                        <div class="news-item">
                            <div class="news-title">
                                <a href="${a.url}" target="_blank">${a.title}</a>
                            </div>
                            <p>来源: ${a.source} | 发布时间: ${a.published_at || '未知'}</p>
                        </div>
                    `).join('');
                });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
