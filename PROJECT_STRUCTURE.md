# 项目结构说明

## 目录结构

```
python_data/
├── src/                    # 源代码目录
│   ├── config/            # 配置管理
│   ├── db/                # 数据库层（模型+访问层）
│   ├── services/          # 业务逻辑层
│   ├── crawlers/          # 抓取器模块
│   ├── analyzers/         # 分析器模块
│   ├── api/               # API 层
│   ├── core/              # 核心功能（日志、异常）
│   ├── tasks/             # 定时任务
│   └── main_new.py        # 新的主程序入口
│
├── scripts/               # 脚本工具
├── tests/                 # 测试目录
├── app_config.yaml        # 配置文件
└── main.py               # 旧的主程序（保留）
```

## 各层职责

### 1. 配置层 (`config/`)

- **职责**: 统一管理所有配置
- **文件**: `settings.py`
- **特点**: 使用 dataclass，类型安全，支持环境变量

### 2. 数据库层 (`db/`)

- **models.py**: SQLAlchemy 数据模型
- **session.py**: 数据库连接和会话管理
- **repositories.py**: 数据访问层（Repository 模式）

### 3. 业务逻辑层 (`services/`)

- **职责**: 处理业务逻辑，协调 Repository 和 Crawler/Analyzer
- **文件**: 
  - `crawler_service.py`: 抓取服务
  - `analysis_service.py`: 分析服务

### 4. 抓取器层 (`crawlers/`)

- **职责**: 负责从各种源抓取新闻
- **文件**:
  - `base.py`: 基础接口
  - `rss_crawler.py`: RSS 抓取器
  - `platform_crawler.py`: 平台热榜抓取器

### 5. 分析器层 (`analyzers/`)

- **职责**: 负责新闻分析
- **文件**:
  - `base.py`: 基础接口
  - `ai_analyzer.py`: AI 分析器实现

### 6. API 层 (`api/`)

- **职责**: Web API 接口（待完善）
- **文件**: `dependencies.py`: 依赖注入

### 7. 核心层 (`core/`)

- **职责**: 通用功能
- **文件**:
  - `exceptions.py`: 自定义异常
  - `logging.py`: 日志配置

### 8. 任务层 (`tasks/`)

- **职责**: 定时任务调度
- **文件**: `scheduler.py`

## 数据流

```
配置文件 (app_config.yaml)
    ↓
配置层 (config/settings.py)
    ↓
数据库层 (db/)
    ├── models.py (数据模型)
    ├── session.py (连接管理)
    └── repositories.py (数据访问)
    ↓
业务逻辑层 (services/)
    ├── crawler_service.py
    └── analysis_service.py
    ↓
抓取器/分析器 (crawlers/analyzers/)
    ↓
主程序 (main_new.py)
```

## 设计模式

1. **Repository 模式**: 数据访问层封装
2. **Service 模式**: 业务逻辑层封装
3. **依赖注入**: 降低耦合度
4. **接口模式**: Crawler 和 Analyzer 使用接口

## 优势

1. **职责分离**: 每层职责清晰
2. **易于测试**: Repository 和 Service 可独立测试
3. **易于扩展**: 新增功能只需添加新的 Repository 或 Service
4. **类型安全**: 使用类型提示，IDE 支持好
5. **维护性强**: 代码组织清晰，便于维护
