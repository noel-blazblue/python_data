"""
统一配置管理模块
"""
import os
import yaml
from dataclasses import dataclass
from typing import Optional, List, Dict
from pathlib import Path
import pytz


@dataclass
class AppConfig:
    """应用基础配置"""
    name: str = "新闻分析服务"
    timezone: str = "Asia/Shanghai"
    log_level: str = "INFO"
    
    @property
    def timezone_obj(self):
        """获取时区对象"""
        return pytz.timezone(self.timezone)


@dataclass
class DatabaseConfig:
    """数据库配置"""
    type: str = "sqlite"
    path: Optional[str] = "data/news.db"
    host: Optional[str] = None
    port: Optional[int] = None
    user: Optional[str] = None
    password: Optional[str] = None
    dbname: Optional[str] = None
    
    def get_url(self) -> str:
        """获取数据库连接 URL"""
        if self.type == "sqlite":
            return f"sqlite:///{self.path}"
        elif self.type == "postgresql":
            return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}"
        else:
            raise ValueError(f"不支持的数据库类型: {self.type}")


@dataclass
class CrawlerConfig:
    """抓取器配置"""
    request_interval: int = 2
    timeout: int = 30
    max_articles_per_source: int = 50
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


@dataclass
class AIConfig:
    """AI 配置"""
    provider: str = "openai"
    api_key: str = ""
    model: str = "gpt-4o-mini"
    base_url: str = ""
    temperature: float = 0.7
    max_tokens: int = 2000
    timeout: int = 60


@dataclass
class AnalysisConfig:
    """分析配置"""
    enabled: bool = True
    language: str = "中文"
    max_articles_per_analysis: int = 20
    analysis_interval: int = 3600


@dataclass
class ServiceConfig:
    """服务配置"""
    fetch_interval: int = 1800
    enable_scheduler: bool = True


@dataclass
class WebConfig:
    """Web 服务配置"""
    enabled: bool = True
    host: str = "0.0.0.0"
    port: int = 8000


@dataclass
class PlatformSource:
    """平台源配置"""
    id: str
    name: str


@dataclass
class PlatformConfig:
    """平台配置"""
    enabled: bool = False
    sources: List[PlatformSource] = None
    
    def __post_init__(self):
        if self.sources is None:
            self.sources = []


@dataclass
class NewsSource:
    """新闻源配置"""
    name: str
    type: str
    url: str
    enabled: bool = True


class Settings:
    """统一配置管理类"""
    
    def __init__(self, config_path: str = "app_config.yaml"):
        """初始化配置"""
        self.config_path = Path(config_path)
        self._raw_config = self._load_config()
        self._init_configs()
    
    def _load_config(self) -> Dict:
        """加载配置文件"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    
    def _init_configs(self):
        """初始化各个配置对象"""
        # 应用配置
        app_cfg = self._raw_config.get('app', {})
        self.app = AppConfig(
            name=app_cfg.get('name', '新闻分析服务'),
            timezone=app_cfg.get('timezone', 'Asia/Shanghai'),
            log_level=app_cfg.get('log_level', 'INFO')
        )
        
        # 数据库配置
        db_cfg = self._raw_config.get('database', {})
        self.database = DatabaseConfig(
            type=db_cfg.get('type', 'sqlite'),
            path=db_cfg.get('path', 'data/news.db'),
            host=db_cfg.get('host'),
            port=db_cfg.get('port'),
            user=db_cfg.get('user'),
            password=db_cfg.get('password'),
            dbname=db_cfg.get('dbname')
        )
        
        # 抓取器配置
        crawler_cfg = self._raw_config.get('crawler', {})
        self.crawler = CrawlerConfig(
            request_interval=crawler_cfg.get('request_interval', 2),
            timeout=crawler_cfg.get('timeout', 30),
            max_articles_per_source=crawler_cfg.get('max_articles_per_source', 50),
            user_agent=crawler_cfg.get('user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        )
        
        # AI 配置
        ai_cfg = self._raw_config.get('ai', {})
        api_key = os.getenv('AI_API_KEY') or ai_cfg.get('api_key', '')
        self.ai = AIConfig(
            provider=ai_cfg.get('provider', 'openai'),
            api_key=api_key,
            model=ai_cfg.get('model', 'gpt-4o-mini'),
            base_url=ai_cfg.get('base_url', ''),
            temperature=ai_cfg.get('temperature', 0.7),
            max_tokens=ai_cfg.get('max_tokens', 2000),
            timeout=ai_cfg.get('timeout', 60)
        )
        
        # 分析配置
        analysis_cfg = self._raw_config.get('analysis', {})
        self.analysis = AnalysisConfig(
            enabled=analysis_cfg.get('enabled', True),
            language=analysis_cfg.get('language', '中文'),
            max_articles_per_analysis=analysis_cfg.get('max_articles_per_analysis', 20),
            analysis_interval=analysis_cfg.get('analysis_interval', 3600)
        )
        
        # 服务配置
        service_cfg = self._raw_config.get('service', {})
        self.service = ServiceConfig(
            fetch_interval=service_cfg.get('fetch_interval', 1800),
            enable_scheduler=service_cfg.get('enable_scheduler', True)
        )
        
        # Web 配置
        web_cfg = self._raw_config.get('web', {})
        self.web = WebConfig(
            enabled=web_cfg.get('enabled', True),
            host=web_cfg.get('host', '0.0.0.0'),
            port=web_cfg.get('port', 8000)
        )
        
        # 平台配置
        platforms_cfg = self._raw_config.get('platforms', {})
        sources = []
        for s in platforms_cfg.get('sources', []):
            sources.append(PlatformSource(
                id=s.get('id'),
                name=s.get('name', s.get('id'))
            ))
        self.platforms = PlatformConfig(
            enabled=platforms_cfg.get('enabled', False),
            sources=sources
        )
        
        # 新闻源配置
        self.news_sources = {
            'domestic': [],
            'international': []
        }
        sources_cfg = self._raw_config.get('news_sources', {})
        for source_type in ['domestic', 'international']:
            for s in sources_cfg.get(source_type, []):
                self.news_sources[source_type].append(NewsSource(
                    name=s.get('name'),
                    type=s.get('type', 'rss'),
                    url=s.get('url'),
                    enabled=s.get('enabled', True)
                ))
    
    def get_enabled_news_sources(self, source_type: Optional[str] = None) -> List[NewsSource]:
        """获取启用的新闻源"""
        sources = []
        types = [source_type] if source_type else ['domestic', 'international']
        
        for st in types:
            sources.extend([
                s for s in self.news_sources.get(st, [])
                if s.enabled
            ])
        
        return sources


# 全局配置实例（延迟初始化）
_settings: Optional[Settings] = None


def get_settings(config_path: str = "app_config.yaml") -> Settings:
    """获取配置实例（单例模式）"""
    global _settings
    if _settings is None:
        _settings = Settings(config_path)
    return _settings
