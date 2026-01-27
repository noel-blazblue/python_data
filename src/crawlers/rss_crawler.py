"""
RSS 抓取器
"""
import requests
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict
from loguru import logger
import pytz

from src.crawlers.base import BaseCrawler
from src.core.exceptions import CrawlerException


class RSSCrawler(BaseCrawler):
    """RSS 抓取器"""
    
    def __init__(self, config):
        """
        初始化 RSS 抓取器
        
        Args:
            config: 配置对象（Settings）
        """
        self.config = config
        self.crawler_config = config.crawler
        self.timezone = config.app.timezone_obj
        
        # 配置会话
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.crawler_config.user_agent})
    
    def fetch(self, source_config: Dict) -> List[Dict]:
        """
        抓取 RSS 源
        
        Args:
            source_config: 新闻源配置，包含 name, url, type 等
            
        Returns:
            文章列表
        """
        articles = []
        source_name = source_config.get('name', '未知')
        url = source_config.get('url', '')
        source_type = source_config.get('source_type', 'domestic')
        
        try:
            logger.info(f"正在抓取 RSS: {source_name} - {url}")
            
            # 先检查 URL 响应
            try:
                response = self.session.get(
                    url,
                    timeout=self.crawler_config.timeout,
                    allow_redirects=True
                )
                response.raise_for_status()
                
                # 检查 Content-Type
                content_type = response.headers.get('Content-Type', '').lower()
                if 'html' in content_type and 'xml' not in content_type and 'rss' not in content_type:
                    logger.error(
                        f"❌ {source_name} 的 URL 不是有效的 RSS feed！"
                        f" Content-Type: {content_type}"
                    )
                    return articles
                
            except requests.RequestException as e:
                logger.error(f"❌ 无法访问 {source_name} 的 URL: {e}")
                return articles
            
            # 解析 RSS feed
            feed = feedparser.parse(url)
            
            # 检查解析错误
            if feed.bozo and feed.bozo_exception:
                error_msg = str(feed.bozo_exception)
                
                # 区分致命错误和非致命警告
                is_fatal_error = True
                non_fatal_keywords = [
                    'us-ascii', 'utf-8', 'encoding', 'charset',
                    'character encoding', 'declared as', 'parsed as'
                ]
                
                error_lower = error_msg.lower()
                if any(keyword in error_lower for keyword in non_fatal_keywords):
                    if feed.entries:
                        logger.warning(
                            f"⚠️  {source_name} RSS feed 有编码警告（非致命）: {error_msg}"
                        )
                        is_fatal_error = False
                    else:
                        logger.error(f"❌ {source_name} RSS feed 编码错误且无文章条目")
                else:
                    logger.error(f"❌ RSS 解析失败 ({source_name}): {error_msg}")
                
                if is_fatal_error or not feed.entries:
                    return articles
            
            # 检查是否成功解析到文章
            if not feed.entries:
                logger.warning(f"⚠️  {source_name} 的 RSS feed 没有找到任何文章条目")
                return articles
            
            # 处理文章条目
            max_articles = self.crawler_config.max_articles_per_source
            for entry in feed.entries[:max_articles]:
                try:
                    # 解析发布时间
                    published_at = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published_at = datetime(*entry.published_parsed[:6])
                        published_at = self.timezone.localize(published_at)
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        published_at = datetime(*entry.updated_parsed[:6])
                        published_at = self.timezone.localize(published_at)
                    
                    # 提取摘要
                    summary = ""
                    if hasattr(entry, 'summary'):
                        summary = entry.summary
                    elif hasattr(entry, 'description'):
                        summary = entry.description
                    
                    # 清理 HTML 标签
                    if summary:
                        soup = BeautifulSoup(summary, 'html.parser')
                        summary = soup.get_text(strip=True)
                    
                    article = {
                        'title': entry.title if hasattr(entry, 'title') else '无标题',
                        'summary': summary[:500] if summary else None,
                        'url': entry.link if hasattr(entry, 'link') else '',
                        'source': source_name,
                        'source_type': source_type,
                        'published_at': published_at,
                        'language': 'zh' if source_type == 'domestic' else 'en',
                        'crawled_at': datetime.now(self.timezone)
                    }
                    
                    if article['url']:
                        articles.append(article)
                
                except Exception as e:
                    logger.error(f"解析文章条目失败: {e}")
                    continue
            
            logger.info(f"成功抓取 {len(articles)} 篇文章来自 {source_name}")
            return articles
        
        except Exception as e:
            logger.error(f"抓取 RSS 失败 {source_name}: {e}")
            raise CrawlerException(f"抓取 RSS 失败: {e}") from e
