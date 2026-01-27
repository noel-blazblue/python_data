"""
抓取器基础接口
"""
from abc import ABC, abstractmethod
from typing import List, Dict
from loguru import logger


class BaseCrawler(ABC):
    """抓取器基类"""
    
    @abstractmethod
    def fetch(self, source_config: Dict) -> List[Dict]:
        """
        抓取新闻
        
        Args:
            source_config: 新闻源配置
            
        Returns:
            文章列表
        """
        pass
    
    def extract_summary(self, article: Dict) -> str:
        """
        提取文章摘要
        
        Args:
            article: 文章数据
            
        Returns:
            摘要文本
        """
        if article.get('summary'):
            return article['summary']
        
        if article.get('content'):
            return article['content'][:200] + '...'
        
        return article.get('title', '无摘要')
