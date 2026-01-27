"""
抓取服务 - 业务逻辑层
"""
import time
from typing import List, Dict
from loguru import logger

from src.db.repositories import ArticleRepository
from src.crawlers import RSSCrawler, PlatformCrawler
from src.core.exceptions import CrawlerException


class CrawlerService:
    """抓取服务"""
    
    def __init__(
        self,
        db_manager,
        rss_crawler: RSSCrawler,
        platform_crawler: PlatformCrawler,
        config
    ):
        """
        初始化抓取服务
        
        Args:
            db_manager: 数据库管理器
            rss_crawler: RSS 抓取器
            platform_crawler: 平台抓取器
            config: 配置对象
        """
        self.db_manager = db_manager
        self.rss_crawler = rss_crawler
        self.platform_crawler = platform_crawler
        self.config = config
    
    def fetch_all_sources(self) -> int:
        """
        抓取所有配置的新闻源
        
        Returns:
            成功保存的文章数量
        """
        logger.info("开始抓取所有新闻源...")
        total_saved = 0
        
        # 1. 抓取 RSS 新闻源
        rss_saved = self._fetch_rss_sources()
        total_saved += rss_saved
        
        # 2. 抓取平台热榜（如果启用）
        if self.config.platforms.enabled:
            platform_saved = self._fetch_platform_sources()
            total_saved += platform_saved
        else:
            logger.info("平台热榜抓取已禁用")
        
        logger.info(f"抓取完成，共保存 {total_saved} 篇新文章")
        return total_saved
    
    def _fetch_rss_sources(self) -> int:
        """抓取 RSS 新闻源"""
        saved_count = 0
        
        # 获取所有启用的新闻源
        sources = self.config.get_enabled_news_sources()
        
        with self.db_manager.session_scope() as session:
            article_repo = ArticleRepository(session)
            
            for source in sources:
                try:
                    # 构建源配置
                    source_type = 'domestic' if source in self.config.news_sources['domestic'] else 'international'
                    source_config = {
                        'name': source.name,
                        'url': source.url,
                        'type': source.type,
                        'source_type': source_type
                    }
                    
                    # 抓取文章
                    articles = self.rss_crawler.fetch(source_config)
                    
                    # 保存文章
                    for article in articles:
                        try:
                            # 提取摘要
                            article['summary'] = self.rss_crawler.extract_summary(article)
                            
                            # 保存到数据库
                            saved_article = article_repo.add(article)
                            if saved_article:
                                saved_count += 1
                        
                        except Exception as e:
                            logger.error(f"保存文章失败: {e}")
                            continue
                    
                    # 请求间隔
                    time.sleep(self.config.crawler.request_interval)
                
                except CrawlerException as e:
                    logger.error(f"抓取 RSS 源失败 {source.name}: {e}")
                    continue
        
        logger.info(f"RSS 源抓取完成，保存 {saved_count} 篇新文章")
        return saved_count
    
    def _fetch_platform_sources(self) -> int:
        """抓取平台热榜数据"""
        if not self.config.platforms.sources:
            logger.info("未配置任何平台热榜源")
            return 0
        
        saved_count = 0
        
        # 构建平台 ID 列表
        ids_list = [
            (s.id, s.name)
            for s in self.config.platforms.sources
        ]
        
        try:
            # 批量抓取平台数据
            results, id_to_name, failed_ids = self.platform_crawler.crawl_websites(
                ids_list=ids_list,
                request_interval=100  # 100ms 间隔
            )
            
            # 保存数据
            from datetime import datetime
            now = datetime.now(self.config.app.timezone_obj)
            
            with self.db_manager.session_scope() as session:
                article_repo = ArticleRepository(session)
                
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
                            "source_type": "domestic",
                            "published_at": None,
                            "crawled_at": now,
                            "language": "zh",
                            "category": "hot_platform",
                            "tags": platform_id,
                        }
                        
                        try:
                            saved_article = article_repo.add(article_data)
                            if saved_article:
                                saved_count += 1
                        except Exception as e:
                            logger.error(f"保存热榜数据失败 ({source_name}): {e}")
                            continue
            
            if failed_ids:
                logger.warning(f"部分平台抓取失败: {failed_ids}")
            
            logger.info(f"平台热榜抓取完成，保存 {saved_count} 条记录")
            return saved_count
        
        except Exception as e:
            logger.error(f"抓取平台热榜数据失败: {e}")
            return 0
