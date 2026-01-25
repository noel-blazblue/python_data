"""
新闻抓取模块
支持 RSS 和网页抓取
"""
import requests
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime
import time
import yaml
from loguru import logger
from typing import List, Dict, Optional
import pytz


class NewsCrawler:
    """新闻抓取器"""
    
    def __init__(self, config_path='app_config.yaml'):
        """初始化抓取器"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        crawler_config = self.config.get('crawler', {})
        self.request_interval = crawler_config.get('request_interval', 2)
        self.timeout = crawler_config.get('timeout', 30)
        self.max_articles = crawler_config.get('max_articles_per_source', 50)
        self.user_agent = crawler_config.get(
            'user_agent',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        self.timezone = pytz.timezone(self.config.get('app', {}).get('timezone', 'Asia/Shanghai'))
        
        # 配置会话
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.user_agent})
    
    def fetch_rss_feed(self, url: str, source_name: str, source_type: str) -> List[Dict]:
        """抓取 RSS 源"""
        articles = []
        try:
            logger.info(f"正在抓取 RSS: {source_name} - {url}")
            feed = feedparser.parse(url)
            
            if feed.bozo and feed.bozo_exception:
                logger.warning(f"RSS 解析错误: {feed.bozo_exception}")
                return articles
            
            for entry in feed.entries[:self.max_articles]:
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
                        'summary': summary[:500] if summary else None,  # 限制摘要长度
                        'url': entry.link if hasattr(entry, 'link') else '',
                        'source': source_name,
                        'source_type': source_type,
                        'published_at': published_at,
                        'language': 'zh' if source_type == 'domestic' else 'en',
                        'crawled_at': datetime.now(self.timezone)
                    }
                    
                    if article['url']:  # 确保有 URL
                        articles.append(article)
                
                except Exception as e:
                    logger.error(f"解析文章条目失败: {e}")
                    continue
            
            logger.info(f"成功抓取 {len(articles)} 篇文章来自 {source_name}")
            return articles
        
        except Exception as e:
            logger.error(f"抓取 RSS 失败 {source_name}: {e}")
            return articles
    
    def fetch_web_article(self, url: str) -> Optional[Dict]:
        """抓取网页文章内容（可选，用于获取完整内容）"""
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 提取标题
            title = soup.find('title')
            title = title.get_text(strip=True) if title else '无标题'
            
            # 提取正文（简单方法，可根据具体网站调整）
            content = ""
            # 尝试查找常见的正文容器
            for tag in ['article', 'main', '.content', '.post-content', '#content']:
                element = soup.select_one(tag)
                if element:
                    content = element.get_text(strip=True)
                    break
            
            if not content:
                # 如果没有找到，尝试提取所有段落
                paragraphs = soup.find_all('p')
                content = '\n'.join([p.get_text(strip=True) for p in paragraphs])
            
            return {
                'title': title,
                'content': content[:5000] if content else None  # 限制内容长度
            }
        
        except Exception as e:
            logger.error(f"抓取网页内容失败 {url}: {e}")
            return None
    
    def crawl_all_sources(self) -> List[Dict]:
        """抓取所有配置的新闻源"""
        all_articles = []
        sources_config = self.config.get('news_sources', {})
        
        # 抓取国内新闻
        domestic_sources = sources_config.get('domestic', [])
        for source in domestic_sources:
            if not source.get('enabled', True):
                continue
            
            if source.get('type') == 'rss':
                articles = self.fetch_rss_feed(
                    source['url'],
                    source['name'],
                    'domestic'
                )
                all_articles.extend(articles)
            
            # 添加延迟避免请求过快
            time.sleep(self.request_interval)
        
        # 抓取国际新闻
        international_sources = sources_config.get('international', [])
        for source in international_sources:
            if not source.get('enabled', True):
                continue
            
            if source.get('type') == 'rss':
                articles = self.fetch_rss_feed(
                    source['url'],
                    source['name'],
                    'international'
                )
                all_articles.extend(articles)
            
            # 添加延迟避免请求过快
            time.sleep(self.request_interval)
        
        logger.info(f"总共抓取 {len(all_articles)} 篇文章")
        return all_articles
    
    def extract_summary(self, article: Dict) -> str:
        """提取文章摘要（如果已有则返回，否则尝试生成）"""
        if article.get('summary'):
            return article['summary']
        
        # 如果有完整内容，提取前200字作为摘要
        if article.get('content'):
            return article['content'][:200] + '...'
        
        return article.get('title', '无摘要')
