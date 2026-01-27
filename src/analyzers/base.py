"""
分析器基础接口
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class BaseAnalyzer(ABC):
    """分析器基类"""
    
    @abstractmethod
    def analyze_single(self, article: Dict) -> Optional[Dict]:
        """
        分析单篇文章
        
        Args:
            article: 文章数据字典
            
        Returns:
            分析结果字典，失败返回 None
        """
        pass
    
    @abstractmethod
    def analyze_batch(self, articles: List[Dict]) -> Optional[Dict]:
        """
        批量分析多篇文章
        
        Args:
            articles: 文章列表
            
        Returns:
            批量分析结果字典，失败返回 None
        """
        pass
