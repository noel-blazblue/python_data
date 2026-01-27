"""
新闻抓取与分析服务主程序（重构版）
"""
import argparse
from loguru import logger

from src.config import get_settings
from src.core.logging import setup_logging
from src.db import init_db, get_db_manager
from src.db.repositories import ArticleRepository, AnalysisRepository, SummaryRepository
from src.crawlers import RSSCrawler, PlatformCrawler
from src.analyzers import AIAnalyzer
from src.services import CrawlerService, AnalysisService
from src.tasks import TaskScheduler


class NewsService:
    """新闻服务主类"""
    
    def __init__(self, config_path: str = 'app_config.yaml'):
        """
        初始化服务
        
        Args:
            config_path: 配置文件路径
        """
        # 加载配置
        self.config = get_settings(config_path)
        
        # 配置日志
        setup_logging(
            log_level=self.config.app.log_level,
            log_dir='logs'
        )
        
        logger.info("初始化新闻服务...")
        
        # 初始化数据库
        database_url = self.config.database.get_url()
        init_db(database_url)
        self.db_manager = get_db_manager()
        
        # 初始化抓取器
        self.rss_crawler = RSSCrawler(self.config)
        self.platform_crawler = PlatformCrawler(self.config)
        
        # 初始化分析器
        self.analyzer = AIAnalyzer(self.config)
        
        # 初始化服务层
        self.crawler_service = CrawlerService(
            db_manager=self.db_manager,
            rss_crawler=self.rss_crawler,
            platform_crawler=self.platform_crawler,
            config=self.config
        )
        
        self.analysis_service = AnalysisService(
            db_manager=self.db_manager,
            analyzer=self.analyzer,
            config=self.config
        )
        
        logger.info("新闻服务初始化完成")
    
    def fetch_news(self) -> int:
        """抓取新闻"""
        logger.info("开始抓取新闻...")
        return self.crawler_service.fetch_all_sources()
    
    def analyze_news(self, limit: int = None) -> int:
        """分析新闻"""
        logger.info("开始分析新闻...")
        return self.analysis_service.analyze_unanalyzed_articles(limit=limit)
    
    def generate_daily_summary(self) -> bool:
        """生成每日摘要"""
        logger.info("生成每日摘要...")
        return self.analysis_service.generate_daily_summary()
    
    def run_once(self):
        """运行一次（抓取+分析）"""
        logger.info("=" * 50)
        logger.info("开始执行新闻服务任务")
        logger.info("=" * 50)
        
        # 抓取新闻
        self.fetch_news()
        
        # 分析新闻
        if self.config.analysis.enabled:
            self.analyze_news()
        
        logger.info("任务执行完成")
    
    def run_scheduler(self):
        """运行定时任务"""
        scheduler = TaskScheduler(
            crawler_service=self.crawler_service,
            analysis_service=self.analysis_service,
            config=self.config
        )
        
        scheduler.setup_schedules()
        scheduler.run()
    
    def run(self):
        """运行服务"""
        # 先执行一次
        self.run_once()
        
        # 如果启用定时任务，则持续运行
        if self.config.service.enable_scheduler:
            self.run_scheduler()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='新闻抓取与分析服务')
    parser.add_argument(
        '--mode',
        choices=['all', 'fetch', 'analyze', 'scheduler', 'web'],
        default='all',
        help='运行模式: all(全部), fetch(仅抓取), analyze(仅分析), scheduler(定时任务), web(Web服务)'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='只运行一次（不启动定时任务）'
    )
    parser.add_argument(
        '--config',
        default='app_config.yaml',
        help='配置文件路径（默认: app_config.yaml）'
    )
    
    args = parser.parse_args()
    
    service = NewsService(config_path=args.config)
    
    if args.mode == 'web':
        # 启动 Web 服务
        logger.info("启动 Web 服务...")
        import uvicorn
        
        web_config = service.config.web
        logger.info(f"Web 服务地址: http://{web_config.host}:{web_config.port}")
        uvicorn.run("src.api.app:app", host=web_config.host, port=web_config.port, reload=False)
    
    elif args.mode == 'fetch':
        # 仅执行新闻抓取
        logger.info("执行新闻抓取任务...")
        service.fetch_news()
    
    elif args.mode == 'analyze':
        # 仅执行 AI 分析
        logger.info("执行 AI 分析任务...")
        service.analyze_news()
    
    elif args.mode == 'scheduler':
        # 仅启动定时任务
        logger.info("启动定时任务调度器...")
        service.run_scheduler()
    
    elif args.mode == 'all':
        # 全部功能
        if args.once:
            service.run_once()
        else:
            service.run()


if __name__ == '__main__':
    main()
