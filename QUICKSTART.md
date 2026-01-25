# 快速启动指南

## 5 分钟快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

创建 `.env` 文件：

```bash
cp .env.example .env
```

编辑 `.env`，填入你的 AI API Key（例如 OpenAI）：

```
AI_API_KEY=sk-your-api-key-here
```

### 3. 运行一次测试

```bash
python main.py --once
```

这将：
- 抓取配置的新闻源
- 保存到数据库
- 使用 AI 分析新闻

### 4. 查看结果

**方式一：使用命令行工具**

```bash
# 查看最近的新闻
python query_news.py recent

# 查看分析结果
python query_news.py analysis

# 查看统计信息
python query_news.py stats
```

**方式二：使用 Web 界面（推荐）**

```bash
# 启动 Web 服务
python main.py --mode web
```

然后访问 http://localhost:8000 查看 Web 界面。

### 5. 启动定时服务

```bash
python main.py
```

服务将按照 `app_config.yaml` 中的配置自动运行。

### 6. 单独执行任务

```bash
# 只抓取新闻
python main.py --mode fetch

# 只执行 AI 分析
python main.py --mode analyze
```

## 常见问题

### Q: 如何添加更多新闻源？

编辑 `app_config.yaml`，在 `news_sources` 部分添加：

```yaml
news_sources:
  domestic:
    - name: "新新闻源"
      type: "rss"
      url: "https://example.com/feed.xml"
      enabled: true
```

### Q: 如何修改 AI 模型？

编辑 `app_config.yaml`：

```yaml
ai:
  provider: "openai"  # 或 "anthropic", "deepseek"
  model: "gpt-4o-mini"  # 修改为你想要的模型
```

### Q: 如何禁用 AI 分析以节省费用？

编辑 `app_config.yaml`：

```yaml
analysis:
  enabled: false  # 改为 false
```

### Q: 数据库文件在哪里？

默认位置：`data/news.db`

### Q: 如何查看日志？

日志文件保存在 `logs/` 目录下，按日期自动轮转。

## 下一步

- 阅读完整的 [README.md](README.md) 了解详细配置
- 根据需要调整 `app_config.yaml` 中的配置
- 探索 `query_news.py` 的更多查询功能
