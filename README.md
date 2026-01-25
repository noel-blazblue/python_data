# 新闻抓取与分析服务

一个基于 Python 的新闻抓取、存储和 AI 分析服务，支持国内外多个新闻源，自动抓取新闻并生成摘要，使用 AI 进行深度分析。

## 功能特性

- 📰 **多源新闻抓取**：支持 RSS 订阅源，可配置国内外多个新闻源
- 💾 **数据库存储**：使用 SQLite 或 PostgreSQL 存储新闻文章和分析结果
- 🤖 **AI 分析**：支持 OpenAI、Anthropic、DeepSeek 等 AI 服务进行新闻分析
- 📊 **自动摘要**：自动提取新闻摘要，支持批量分析和每日摘要
- ⏰ **定时任务**：支持定时抓取和分析，可配置执行间隔
- 📝 **日志记录**：完整的日志系统，便于调试和监控

## 项目结构

```
python_data/
├── main.py              # 主程序入口
├── database.py          # 数据库模型和管理
├── news_crawler.py      # 新闻抓取模块
├── ai_analyzer.py       # AI 分析模块
├── app_config.yaml      # 配置文件
├── requirements.txt     # 依赖包
├── .env.example         # 环境变量示例
├── query_news.py        # 新闻查询工具
├── web_service.py       # Web 服务模块
├── README.md           # 说明文档
├── data/               # 数据目录（自动创建）
└── logs/               # 日志目录（自动创建）
```

## 安装步骤

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填入你的 AI API Key：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的 API Key：

```
AI_API_KEY=your_api_key_here
```

### 3. 配置新闻源

编辑 `app_config.yaml` 文件，配置你需要的新闻源：

```yaml
news_sources:
  domestic:
    - name: "新浪新闻"
      type: "rss"
      url: "https://news.sina.com.cn/roll/index.d.html"
      enabled: true
  # ... 更多配置
```

### 4. 配置 AI 服务

在 `app_config.yaml` 中配置 AI 服务：

```yaml
ai:
  provider: "openai"  # openai, anthropic, deepseek
  api_key: ""  # 从环境变量读取
  model: "gpt-4o-mini"
  temperature: 0.7
  max_tokens: 2000
```

## 使用方法

### 命令行模式

#### 运行一次（抓取+分析）

```bash
python main.py --once
```

#### 持续运行（定时任务）

```bash
python main.py
```

#### 单独执行新闻爬虫

```bash
python main.py --mode fetch
```

#### 单独执行 AI 分析

```bash
python main.py --mode analyze
```

#### 仅启动定时任务调度器

```bash
python main.py --mode scheduler
```

#### 启动 Web 服务

```bash
python main.py --mode web
```

或者直接运行：

```bash
python web_service.py
```

服务将按照配置的间隔自动抓取和分析新闻。

### Web 服务模式

启动 Web 服务后，访问：

- **Web 界面**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs
- **统计信息**: http://localhost:8000/api/stats
- **新闻列表**: http://localhost:8000/api/articles
- **分析结果**: http://localhost:8000/api/analyses

#### Web API 接口

- `GET /api/stats` - 获取统计信息
- `POST /api/fetch` - 手动触发新闻抓取
- `POST /api/analyze` - 手动触发 AI 分析
- `GET /api/articles` - 获取新闻列表（支持 limit, offset, source, analyzed 参数）
- `GET /api/analyses` - 获取分析结果列表
- `GET /api/article/{article_id}` - 获取单篇文章详情

### 查询新闻数据

使用 `query_news.py` 工具查询已存储的新闻：

```bash
# 查询最近的新闻（默认最近1天，10篇）
python query_news.py recent

# 查询最近3天的20篇新闻
python query_news.py recent 20 3

# 查询分析结果
python query_news.py analysis

# 查询统计信息
python query_news.py stats
```

## 配置说明

### 数据库配置

默认使用 SQLite，数据库文件保存在 `data/news.db`。如需使用 PostgreSQL：

```yaml
database:
  type: "postgresql"
  host: "localhost"
  port: 5432
  user: "your_user"
  password: "your_password"
  dbname: "news_db"
```

### 抓取配置

```yaml
crawler:
  request_interval: 2  # 请求间隔（秒）
  timeout: 30          # 请求超时（秒）
  max_articles_per_source: 50  # 每个源最多抓取文章数
```

### 服务配置

```yaml
service:
  fetch_interval: 1800      # 抓取间隔（秒），30分钟
  enable_scheduler: true    # 是否启用定时任务

analysis:
  enabled: true             # 是否启用 AI 分析
  analysis_interval: 3600   # 分析间隔（秒），1小时
  max_articles_per_analysis: 20  # 每次分析的文章数量

web:
  enabled: true             # 是否启用 Web 服务
  host: "0.0.0.0"          # 监听地址
  port: 8000                # 监听端口
```

## 数据库结构

### news_articles（新闻文章表）

- `id`: 主键
- `title`: 标题
- `summary`: 摘要
- `content`: 完整内容
- `url`: 文章链接（唯一）
- `source`: 新闻源
- `source_type`: 来源类型（domestic/international）
- `published_at`: 发布时间
- `crawled_at`: 抓取时间
- `language`: 语言
- `is_analyzed`: 是否已分析

### news_analysis（分析结果表）

- `id`: 主键
- `article_id`: 关联的文章ID
- `analysis_content`: 分析内容
- `sentiment`: 情感倾向
- `sentiment_score`: 情感分数
- `key_points`: 关键要点
- `created_at`: 创建时间

### news_summaries（摘要表）

- `id`: 主键
- `summary_date`: 摘要日期
- `summary_type`: 摘要类型（daily/weekly）
- `summary_content`: 摘要内容
- `article_count`: 文章数量

## 支持的 AI 服务

- **OpenAI**: GPT-4, GPT-3.5, GPT-4o-mini 等
- **Anthropic**: Claude 系列
- **DeepSeek**: DeepSeek Chat 等
- **自定义**: 任何 OpenAI 兼容的 API

## 注意事项

1. **API 费用**：使用 AI 分析会产生 API 调用费用，请注意控制分析频率和文章数量
2. **请求频率**：请遵守各新闻源的爬虫协议，合理设置请求间隔
3. **数据存储**：SQLite 适合小规模使用，大规模建议使用 PostgreSQL
4. **环境变量**：敏感信息（如 API Key）建议使用环境变量，不要提交到版本控制

## 扩展开发

### 添加新的新闻源

在 `app_config.yaml` 的 `news_sources` 中添加：

```yaml
- name: "新新闻源"
  type: "rss"
  url: "https://example.com/feed.xml"
  enabled: true
```

### 自定义分析提示词

修改 `ai_analyzer.py` 中的 `analyze_single_article` 方法，调整提示词模板。

### 添加新的分析类型

在 `database.py` 中扩展 `NewsAnalysis` 模型，在 `ai_analyzer.py` 中添加对应的分析方法。

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
