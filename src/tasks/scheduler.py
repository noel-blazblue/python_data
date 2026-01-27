"""
定时任务调度器
"""
import time
import schedule
from loguru import logger

from src.services import CrawlerService, AnalysisService


class TaskScheduler:
    """任务调度器"""
    
    def __init__(
        self,
        crawler_service: CrawlerService,
        analysis_service: AnalysisService,
        config
    ):
        """
        初始化任务调度器
        
        Args:
            crawler_service: 抓取服务
            analysis_service: 分析服务
            config: 配置对象
        """
        self.crawler_service = crawler_service
        self.analysis_service = analysis_service
        self.config = config
    
    def setup_schedules(self):
        """设置定时任务"""
        if not self.config.service.enable_scheduler:
            logger.info("定时任务已禁用")
            return
        
        # 定时抓取
        fetch_interval = self.config.service.fetch_interval
        schedule.every(fetch_interval).seconds.do(self._fetch_task)
        logger.info(f"抓取任务已设置，间隔: {fetch_interval} 秒")
        
        # 定时分析
        if self.config.analysis.enabled:
            analysis_interval = self.config.analysis.analysis_interval
            schedule.every(analysis_interval).seconds.do(self._analyze_task)
            logger.info(f"分析任务已设置，间隔: {analysis_interval} 秒")
        
        # 每日摘要（每天凌晨1点）
        schedule.every().day.at("01:00").do(self._daily_summary_task)
        logger.info("每日摘要任务已设置，执行时间: 每天 01:00")
    
    def _fetch_task(self):
        """抓取任务"""
        try:
            logger.info("=" * 50)
            logger.info("执行定时抓取任务")
            logger.info("=" * 50)
            self.crawler_service.fetch_all_sources()
        except Exception as e:
            logger.error(f"定时抓取任务失败: {e}")
    
    def _analyze_task(self):
        """分析任务"""
        try:
            logger.info("=" * 50)
            logger.info("执行定时分析任务")
            logger.info("=" * 50)
            self.analysis_service.analyze_unanalyzed_articles()
        except Exception as e:
            logger.error(f"定时分析任务失败: {e}")
    
    def _daily_summary_task(self):
        """每日摘要任务"""
        try:
            logger.info("=" * 50)
            logger.info("执行每日摘要任务")
            logger.info("=" * 50)
            self.analysis_service.generate_daily_summary()
        except Exception as e:
            logger.error(f"每日摘要任务失败: {e}")
    
    def run(self):
        """运行调度器"""
        logger.info("启动定时任务调度器...")
        logger.info("按 Ctrl+C 停止")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
        except KeyboardInterrupt:
            logger.info("调度器已停止")
