# 使用示例

## 命令行使用

### 1. 单独执行新闻爬虫

```bash
# 只抓取新闻，不进行分析
python main.py --mode fetch
```

### 2. 单独执行 AI 分析

```bash
# 只对已抓取的新闻进行 AI 分析
python main.py --mode analyze
```

### 3. 运行一次完整流程

```bash
# 抓取 + 分析，然后退出
python main.py --once
```

### 4. 启动定时任务

```bash
# 按照配置的间隔自动执行抓取和分析
python main.py --mode scheduler
```

### 5. 启动 Web 服务

```bash
# 启动 Web 服务（默认端口 8000）
python main.py --mode web

# 或者直接运行
python web_service.py
```

## Web 服务使用

### 启动服务

```bash
python main.py --mode web
```

访问 http://localhost:8000 查看 Web 界面。

### API 调用示例

#### 1. 获取统计信息

```bash
curl http://localhost:8000/api/stats
```

响应：
```json
{
  "total_articles": 150,
  "analyzed_count": 120,
  "total_analyses": 120,
  "today_articles": 25
}
```

#### 2. 手动触发新闻抓取

```bash
curl -X POST http://localhost:8000/api/fetch
```

响应：
```json
{
  "success": true,
  "message": "成功抓取并保存 15 篇新文章",
  "data": {
    "saved_count": 15
  }
}
```

#### 3. 手动触发 AI 分析

```bash
curl -X POST http://localhost:8000/api/analyze
```

响应：
```json
{
  "success": true,
  "message": "成功分析 10 篇文章",
  "data": {
    "analyzed_count": 10
  }
}
```

#### 4. 获取新闻列表

```bash
# 获取前20篇新闻
curl http://localhost:8000/api/articles?limit=20

# 获取未分析的新闻
curl http://localhost:8000/api/articles?analyzed=false

# 获取特定来源的新闻
curl http://localhost:8000/api/articles?source=新浪新闻

# 分页获取
curl http://localhost:8000/api/articles?limit=10&offset=20
```

#### 5. 获取分析结果

```bash
# 获取前20条分析结果
curl http://localhost:8000/api/analyses?limit=20

# 分页获取
curl http://localhost:8000/api/analyses?limit=10&offset=20
```

#### 6. 获取单篇文章详情

```bash
curl http://localhost:8000/api/article/1
```

## Python 脚本调用示例

### 在 Python 代码中使用服务

```python
from database import DatabaseManager
from news_crawler import NewsCrawler
from ai_analyzer import AIAnalyzer

# 初始化
db = DatabaseManager()
crawler = NewsCrawler()
analyzer = AIAnalyzer()

# 抓取新闻
articles = crawler.crawl_all_sources()
for article in articles:
    article['summary'] = crawler.extract_summary(article)
    db.add_article(article)

# 分析新闻
unanalyzed = db.get_unanalyzed_articles(limit=10)
for article in unanalyzed:
    article_dict = {
        'title': article.title,
        'summary': article.summary,
        'source': article.source
    }
    analysis = analyzer.analyze_single_article(article_dict)
    if analysis:
        db.save_analysis(article.id, analysis)
```

## 使用场景示例

### 场景1：每日定时抓取和分析

```bash
# 使用 cron 或 systemd timer 定时执行
# 每天凌晨2点执行一次
0 2 * * * cd /path/to/project && python main.py --once
```

### 场景2：实时监控 + Web 界面

```bash
# 终端1：启动定时任务
python main.py --mode scheduler

# 终端2：启动 Web 服务
python main.py --mode web
```

### 场景3：只抓取不分析（节省 API 费用）

```bash
# 定时抓取
python main.py --mode fetch

# 需要时手动分析
python main.py --mode analyze
```

### 场景4：通过 Web API 集成到其他系统

```python
import requests

# 触发抓取
response = requests.post('http://localhost:8000/api/fetch')
print(response.json())

# 获取统计
stats = requests.get('http://localhost:8000/api/stats').json()
print(f"总文章数: {stats['total_articles']}")

# 获取最新新闻
articles = requests.get('http://localhost:8000/api/articles?limit=10').json()
for article in articles['articles']:
    print(article['title'])
```

## 配置不同模式

### 开发模式（频繁测试）

```yaml
service:
  fetch_interval: 300  # 5分钟
  enable_scheduler: true

analysis:
  enabled: true
  analysis_interval: 600  # 10分钟
  max_articles_per_analysis: 5  # 少量测试
```

### 生产模式（节省资源）

```yaml
service:
  fetch_interval: 3600  # 1小时
  enable_scheduler: true

analysis:
  enabled: true
  analysis_interval: 7200  # 2小时
  max_articles_per_analysis: 20
```

### 仅抓取模式（不分析）

```yaml
analysis:
  enabled: false  # 禁用分析
```
