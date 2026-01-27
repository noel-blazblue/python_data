# 项目重构指南

## 重构概述

项目已按照分层架构进行了重构，新的代码结构更加清晰、模块化，便于维护和扩展。

## 新的项目结构

```
python_data/
├── src/                          # 源代码目录
│   ├── config/                   # 配置管理
│   │   ├── __init__.py
│   │   └── settings.py           # 统一配置管理
│   │
│   ├── db/                       # 数据库层
│   │   ├── __init__.py
│   │   ├── models.py            # SQLAlchemy 模型
│   │   ├── session.py            # 数据库会话管理
│   │   └── repositories.py       # 数据访问层（Repository 模式）
│   │
│   ├── services/                 # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── crawler_service.py    # 抓取服务
│   │   └── analysis_service.py   # 分析服务
│   │
│   ├── crawlers/                 # 抓取器模块
│   │   ├── __init__.py
│   │   ├── base.py               # 基础抓取器接口
│   │   ├── rss_crawler.py        # RSS 抓取器
│   │   └── platform_crawler.py   # 平台抓取器
│   │
│   ├── analyzers/                 # 分析器模块
│   │   ├── __init__.py
│   │   ├── base.py               # 基础分析器接口
│   │   └── ai_analyzer.py        # AI 分析器实现
│   │
│   ├── api/                       # API 层
│   │   ├── __init__.py
│   │   └── dependencies.py       # 依赖注入
│   │
│   ├── core/                      # 核心功能
│   │   ├── __init__.py
│   │   ├── exceptions.py        # 自定义异常
│   │   └── logging.py           # 日志配置
│   │
│   ├── tasks/                     # 定时任务
│   │   ├── __init__.py
│   │   └── scheduler.py
│   │
│   └── main_new.py                # 新的主程序入口
│
├── scripts/                        # 脚本工具
│   ├── __init__.py
│   └── query_news.py
│
├── tests/                         # 测试目录
│   ├── __init__.py
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
├── app_config.yaml                # 配置文件（保持不变）
├── main.py                        # 旧的主程序（保留作为备份）
└── README.md
```

## 主要改进

### 1. 分层架构

- **数据模型层** (`db/models.py`): SQLAlchemy 模型定义
- **数据访问层** (`db/repositories.py`): Repository 模式，封装数据访问逻辑
- **业务逻辑层** (`services/`): Service 层，处理业务逻辑
- **API 层** (`api/`): Web API 接口（待重构）

### 2. 统一配置管理

- 所有配置通过 `src.config.settings` 统一管理
- 使用 dataclass 提供类型提示和默认值
- 支持从环境变量读取敏感信息

### 3. 依赖注入

- Service 层通过依赖注入使用 Repository
- 数据库会话通过上下文管理器自动管理
- 便于测试和扩展

### 4. 模块化设计

- 抓取器和分析器使用接口模式，便于扩展
- 每个模块职责单一，耦合度低

## 使用方法

### 使用新的主程序

```bash
# 运行一次（抓取+分析）
python -m src.main_new --once

# 持续运行（定时任务）
python -m src.main_new

# 仅抓取
python -m src.main_new --mode fetch

# 仅分析
python -m src.main_new --mode analyze

# 仅定时任务
python -m src.main_new --mode scheduler
```

### 使用新的查询工具

```bash
# 查询最近的新闻
python -m scripts.query_news recent 10 1

# 查询分析结果
python -m scripts.query_news analysis 10

# 查询统计信息
python -m scripts.query_news stats
```

## 迁移步骤

### 1. 测试新结构

```bash
# 确保配置文件存在
cp app_config.yaml app_config.yaml.backup

# 测试新的主程序
python -m src.main_new --once
```

### 2. 逐步迁移

1. **保持旧代码运行**: 旧的 `main.py` 仍然可用
2. **测试新代码**: 使用 `src/main_new.py` 进行测试
3. **验证功能**: 确保所有功能正常工作
4. **切换主程序**: 确认无误后，可以替换 `main.py`

### 3. API 层迁移（待完成）

`web_service.py` 需要重构以使用新的 Service 层和 Repository 层。目前可以：
- 继续使用旧的 `web_service.py`
- 或等待 API 层重构完成

## 代码示例

### 使用配置

```python
from src.config import get_settings

config = get_settings()
print(config.app.name)
print(config.database.get_url())
```

### 使用 Repository

```python
from src.db import init_db, get_db_manager
from src.db.repositories import ArticleRepository

init_db("sqlite:///data/news.db")
db_manager = get_db_manager()

with db_manager.session_scope() as session:
    article_repo = ArticleRepository(session)
    articles = article_repo.get_unanalyzed(limit=10)
```

### 使用 Service

```python
from src.config import get_settings
from src.db import init_db, get_db_manager
from src.services import CrawlerService, AnalysisService
from src.crawlers import RSSCrawler, PlatformCrawler
from src.analyzers import AIAnalyzer

config = get_settings()
init_db(config.database.get_url())
db_manager = get_db_manager()

# 初始化服务
rss_crawler = RSSCrawler(config)
platform_crawler = PlatformCrawler(config)
analyzer = AIAnalyzer(config)

crawler_service = CrawlerService(
    db_manager=db_manager,
    rss_crawler=rss_crawler,
    platform_crawler=platform_crawler,
    config=config
)

# 使用服务
crawler_service.fetch_all_sources()
```

## 注意事项

1. **数据库兼容性**: 新的模型与旧模型兼容，数据库无需迁移
2. **配置文件**: `app_config.yaml` 格式保持不变
3. **向后兼容**: 旧的 `main.py` 和 `web_service.py` 仍然可用
4. **测试**: 建议在测试环境先验证新代码

## 后续工作

- [ ] 重构 `web_service.py` 使用新的 Service 层
- [ ] 添加单元测试
- [ ] 添加集成测试
- [ ] 完善 API 文档
- [ ] 性能优化

## 问题反馈

如有问题，请检查：
1. Python 版本（建议 3.8+）
2. 依赖包是否安装完整
3. 配置文件是否正确
4. 数据库路径是否正确
