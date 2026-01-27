"""
新闻抓取与分析服务主程序
"""
import os
import sys
import time
import yaml
import argparse
from datetime import datetime
from loguru import logger
import schedule
from dotenv import load_dotenv
import pytz

from database import DatabaseManager
from news_crawler import NewsCrawler
from ai_analyzer import AIAnalyzer
from fetcher import DataFetcher

# 加载环境变量
load_dotenv()


class NewsService:
    """新闻服务主类"""
    
    def __init__(self, config_path='app_config.yaml'):
        """初始化服务"""
        # 配置日志
        logger.add(
            "logs/news_service_{time}.log",
            rotation="1 day",
            retention="7 days",
            level="INFO"
        )
        
        # 确保日志目录存在
        os.makedirs('logs', exist_ok=True)
        
        logger.info("初始化新闻服务...")
        
        # 加载配置
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # 初始化组件
        self.db = DatabaseManager(config_path)
        self.crawler = NewsCrawler(config_path)
        self.analyzer = AIAnalyzer(config_path)

        # 读取应用时区（用于平台热榜的抓取时间）
        app_config = self.config.get('app', {})
        self.timezone = pytz.timezone(app_config.get('timezone', 'Asia/Shanghai'))
        
        # 获取服务配置
        service_config = self.config.get('service', {})
        self.fetch_interval = service_config.get('fetch_interval', 1800)  # 30分钟
        self.enable_scheduler = service_config.get('enable_scheduler', True)
        
        analysis_config = self.config.get('analysis', {})
        self.analysis_enabled = analysis_config.get('enabled', True)
        self.analysis_interval = analysis_config.get('analysis_interval', 3600)  # 1小时
        self.max_articles_per_analysis = analysis_config.get('max_articles_per_analysis', 20)

        # 热榜平台配置 & 获取器
        platforms_config = self.config.get('platforms', {})
        self.platforms_enabled = platforms_config.get('enabled', False)
        self.platform_sources = platforms_config.get('sources', []) or []
        # 如需代理/API 自定义，后续可从配置中读取，这里先使用默认值
        self.platform_fetcher = DataFetcher()
        
        logger.info("新闻服务初始化完成")
    
    def fetch_news(self):
        """抓取新闻"""
        logger.info("开始抓取新闻...")
        try:
            # 1. 抓取 RSS 新闻源
            articles = self.crawler.crawl_all_sources()
            
            saved_count = 0
            for article in articles:
                try:
                    # 提取摘要
                    article['summary'] = self.crawler.extract_summary(article)
                    
                    # 保存到数据库
                    saved_article = self.db.add_article(article)
                    if saved_article:
                        saved_count += 1
                
                except Exception as e:
                    logger.error(f"保存文章失败: {e}")
                    continue

            # 2. 抓取热榜平台数据（如果启用）
            platform_saved = self.fetch_platform_hotlists()
            total_saved = saved_count + platform_saved
            
            logger.info(
                f"成功保存 {total_saved} 篇新记录 "
                f"(RSS: {saved_count} 篇, 热榜平台: {platform_saved} 篇)"
            )
            return total_saved
        
        except Exception as e:
            logger.error(f"抓取新闻失败: {e}")
            return 0

    def fetch_platform_hotlists(self) -> int:
        """抓取热榜平台数据并写入数据库"""
        if not self.platforms_enabled:
            logger.info("热榜平台抓取已禁用（platforms.enabled = false）")
            return 0

        if not self.platform_sources:
            logger.info("未配置任何热榜平台（platforms.sources 为空）")
            return 0

        logger.info("开始抓取热榜平台数据...")

        # 构造平台 ID 列表：(平台ID, 显示名称)
        ids_list = []
        for s in self.platform_sources:
            platform_id = s.get('id')
            if not platform_id:
                continue
            name = s.get('name', platform_id)
            ids_list.append((platform_id, name))

        if not ids_list:
            logger.info("热榜平台 ID 列表为空，跳过抓取")
            return 0

        try:
            results, id_to_name, failed_ids = self.platform_fetcher.crawl_websites(
                ids_list=ids_list,
                request_interval=100,  # 默认 100ms 左右的间隔即可
            )

            saved_count = 0
            now = datetime.now(self.timezone)

            for platform_id, items in results.items():
                source_name = id_to_name.get(platform_id, platform_id)

                for title, info in items.items():
                    url = info.get("mobileUrl") or info.get("url") or ""
                    if not url:
                        continue

                    article_data = {
                        "title": title,
                        "summary": None,
                        "content": None,
                        "url": url,
                        "source": source_name,
                        # 热榜平台归类为国内新闻源
                        "source_type": "domestic",
                        "published_at": None,
                        "crawled_at": now,
                        "language": "zh",
                        "category": "hot_platform",
                        "tags": platform_id,
                    }

                    try:
                        saved_article = self.db.add_article(article_data)
                        if saved_article:
                            saved_count += 1
                    except Exception as e:
                        logger.error(f"保存热榜数据失败 ({source_name}): {e}")
                        continue

            if failed_ids:
                logger.warning(f"部分热榜平台抓取失败: {failed_ids}")

            logger.info(f"热榜平台数据抓取完成，成功保存 {saved_count} 条记录")
            return saved_count

        except Exception as e:
            logger.error(f"抓取热榜平台数据失败: {e}")
            return 0
    
    def analyze_news(self):
        """分析新闻"""
        if not self.analysis_enabled:
            logger.info("AI 分析功能已禁用")
            return
        
        logger.info("开始分析新闻...")
        try:
            # 获取未分析的文章
            articles = self.db.get_unanalyzed_articles(limit=self.max_articles_per_analysis)
            
            if not articles:
                logger.info("没有需要分析的文章")
                return
            
            logger.info(f"找到 {len(articles)} 篇待分析文章")
            
            analyzed_count = 0
            for article in articles:
                try:
                    # 转换为字典格式
                    article_dict = {
                        'title': article.title,
                        'summary': article.summary,
                        'content': article.content,
                        'source': article.source
                    }
                    
                    # AI 分析
                    analysis_result = self.analyzer.analyze_single_article(article_dict)
                    
                    if analysis_result:
                        # 保存分析结果
                        self.db.save_analysis(article.id, analysis_result)
                        analyzed_count += 1
                        logger.info(f"已分析: {article.title[:50]}...")
                    
                    # 避免请求过快
                    time.sleep(1)
                
                except Exception as e:
                    logger.error(f"分析文章失败 {article.id}: {e}")
                    continue
            
            logger.info(f"成功分析 {analyzed_count} 篇文章")
        
        except Exception as e:
            logger.error(f"分析新闻失败: {e}")
    
    def generate_daily_summary(self):
        """生成每日摘要"""
        logger.info("生成每日摘要...")
        try:
            # 获取今天的文章
            from datetime import date
            today = date.today()
            
            session = self.db.get_session()
            try:
                from database import NewsArticle
                articles = session.query(NewsArticle).filter(
                    NewsArticle.published_at >= datetime.combine(today, datetime.min.time())
                ).limit(50).all()
                
                if not articles:
                    logger.info("今天没有文章可生成摘要")
                    return
                
                # 转换为字典格式
                articles_dict = [
                    {
                        'title': a.title,
                        'summary': a.summary,
                        'source': a.source
                    }
                    for a in articles
                ]
                
                # 批量分析
                summary_result = self.analyzer.analyze_batch_articles(articles_dict)
                
                if summary_result:
                    summary_data = {
                        'summary_date': datetime.combine(today, datetime.min.time()),
                        'summary_type': 'daily',
                        'summary_content': summary_result['summary_content'],
                        'article_count': summary_result['article_count']
                    }
                    
                    self.db.save_summary(summary_data)
                    logger.info("每日摘要生成成功")
            
            finally:
                session.close()
        
        except Exception as e:
            logger.error(f"生成每日摘要失败: {e}")
    
    def run_once(self):
        """运行一次（抓取+分析）"""
        logger.info("=" * 50)
        logger.info("开始执行新闻服务任务")
        logger.info("=" * 50)
        
        # 抓取新闻
        self.fetch_news()
        
        # 分析新闻
        if self.analysis_enabled:
            self.analyze_news()
        
        logger.info("任务执行完成")
    
    def run_scheduler(self):
        """运行定时任务"""
        if not self.enable_scheduler:
            logger.info("定时任务已禁用")
            return
        
        logger.info("启动定时任务调度器...")
        
        # 定时抓取
        schedule.every(self.fetch_interval).seconds.do(self.fetch_news)
        
        # 定时分析
        if self.analysis_enabled:
            schedule.every(self.analysis_interval).seconds.do(self.analyze_news)
        
        # 每日摘要（每天凌晨1点）
        schedule.every().day.at("01:00").do(self.generate_daily_summary)
        
        logger.info(f"抓取间隔: {self.fetch_interval} 秒")
        logger.info(f"分析间隔: {self.analysis_interval} 秒")
        logger.info("定时任务已启动，按 Ctrl+C 停止")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
        except KeyboardInterrupt:
            logger.info("服务已停止")
    
    def run(self):
        """运行服务"""
        # 先执行一次
        self.run_once()
        
        # 如果启用定时任务，则持续运行
        if self.enable_scheduler:
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
        
        with open(args.config, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        web_config = config.get('web', {})
        host = web_config.get('host', '0.0.0.0')
        port = web_config.get('port', 8000)
        
        logger.info(f"Web 服务地址: http://{host}:{port}")
        uvicorn.run("web_service:app", host=host, port=port, reload=False)
    
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
