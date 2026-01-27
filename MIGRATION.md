# 迁移指南

## 从旧代码迁移到新架构

### 1. 备份现有代码

```bash
# 备份旧文件
cp main.py main.py.backup
cp web_service.py web_service.py.backup
```

### 2. 更新导入路径

#### 旧代码
```python
from database import DatabaseManager
from news_crawler import NewsCrawler
from ai_analyzer import AIAnalyzer
```

#### 新代码
```python
from src.config import get_settings
from src.db import init_db, get_db_manager
from src.db.repositories import ArticleRepository
from src.services import CrawlerService, AnalysisService
from src.crawlers import RSSCrawler, PlatformCrawler
from src.analyzers import AIAnalyzer
```

### 3. 使用新的主程序

#### 旧方式
```bash
python main.py --once
python main.py --mode web
```

#### 新方式
```bash
python -m src.main_new --once
python -m src.main_new --mode web
```

### 4. 使用新的 Web 服务

#### 旧方式
```bash
python web_service.py
# 或
python main.py --mode web
```

#### 新方式
```bash
python -m src.main_new --mode web
# 或直接运行
uvicorn src.api.app:app --host 0.0.0.0 --port 8000
```

### 5. 使用新的查询工具

#### 旧方式
```bash
python query_news.py recent 10 1
python query_news.py stats
```

#### 新方式
```bash
python -m scripts.query_news recent 10 1
python -m scripts.query_news stats
```

### 6. 代码迁移示例

#### 示例1: 使用 Repository

**旧代码:**
```python
from database import DatabaseManager

db = DatabaseManager()
session = db.get_session()
articles = session.query(NewsArticle).filter_by(is_analyzed=False).all()
```

**新代码:**
```python
from src.db import init_db, get_db_manager
from src.db.repositories import ArticleRepository

init_db("sqlite:///data/news.db")
db_manager = get_db_manager()

with db_manager.session_scope() as session:
    article_repo = ArticleRepository(session)
    articles = article_repo.get_unanalyzed(limit=20)
```

#### 示例2: 使用 Service

**旧代码:**
```python
from news_crawler import NewsCrawler
from database import DatabaseManager

crawler = NewsCrawler('app_config.yaml')
db = DatabaseManager('app_config.yaml')
articles = crawler.crawl_all_sources()
for article in articles:
    db.add_article(article)
```

**新代码:**
```python
from src.config import get_settings
from src.db import init_db, get_db_manager
from src.services import CrawlerService
from src.crawlers import RSSCrawler, PlatformCrawler

config = get_settings()
init_db(config.database.get_url())
db_manager = get_db_manager()

rss_crawler = RSSCrawler(config)
platform_crawler = PlatformCrawler(config)
crawler_service = CrawlerService(
    db_manager=db_manager,
    rss_crawler=rss_crawler,
    platform_crawler=platform_crawler,
    config=config
)

saved_count = crawler_service.fetch_all_sources()
```

### 7. 配置文件

配置文件 `app_config.yaml` 格式保持不变，无需修改。

### 8. 数据库

数据库模型兼容，无需迁移数据库。新代码可以直接使用现有数据库。

### 9. 测试迁移

1. **测试新主程序**
   ```bash
   python -m src.main_new --once
   ```

2. **测试 Web 服务**
   ```bash
   python -m src.main_new --mode web
   # 访问 http://localhost:8000
   ```

3. **测试查询工具**
   ```bash
   python -m scripts.query_news stats
   ```

### 10. 完全迁移

确认新代码工作正常后：

1. **替换主程序**（可选）
   ```bash
   mv main.py main.py.old
   cp src/main_new.py main.py
   ```

2. **更新 Web 服务**（可选）
   ```bash
   # 可以保留旧的 web_service.py 作为备份
   # 新的 Web 服务在 src/api/app.py
   ```

### 11. 常见问题

#### Q: 导入错误怎么办？
A: 确保在项目根目录运行，或使用 `python -m` 方式运行。

#### Q: 数据库连接失败？
A: 检查配置文件中的数据库路径，确保目录存在。

#### Q: 旧代码还能用吗？
A: 可以，旧的 `main.py` 和 `web_service.py` 仍然可用，但建议逐步迁移到新代码。

### 12. 回滚

如果遇到问题需要回滚：

```bash
# 恢复旧文件
cp main.py.backup main.py
cp web_service.py.backup web_service.py
```

## 迁移检查清单

- [ ] 备份旧代码
- [ ] 测试新主程序 (`python -m src.main_new --once`)
- [ ] 测试 Web 服务 (`python -m src.main_new --mode web`)
- [ ] 测试查询工具 (`python -m scripts.query_news stats`)
- [ ] 验证数据一致性
- [ ] 更新部署脚本（如有）
- [ ] 更新文档
