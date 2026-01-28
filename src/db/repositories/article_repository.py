from typing import List, Optional, Dict, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc, func
from datetime import datetime, timedelta
from src.db.models import NewsArticle

class ArticleRepository:
    """文章数据访问层"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def add(self, article_data: Dict) -> Optional[NewsArticle]:
        """
        添加文章，如果已存在则返回 None
        
        Args:
            article_data: 文章数据字典
            
        Returns:
            新创建的文章对象，如果已存在则返回 None
        """
        try:
            # 检查是否已存在
            existing = self.session.query(NewsArticle).filter_by(
                url=article_data['url']
            ).first()
            if existing:
                return None
            
            # 处理时区感知的 datetime
            if 'published_at' in article_data and article_data['published_at']:
                if hasattr(article_data['published_at'], 'tzinfo') and article_data['published_at'].tzinfo is not None:
                    import pytz
                    article_data['published_at'] = article_data['published_at'].astimezone(pytz.UTC).replace(tzinfo=None)
            
            if 'crawled_at' in article_data and article_data['crawled_at']:
                if hasattr(article_data['crawled_at'], 'tzinfo') and article_data['crawled_at'].tzinfo is not None:
                    import pytz
                    article_data['crawled_at'] = article_data['crawled_at'].astimezone(pytz.UTC).replace(tzinfo=None)
            
            # 创建新文章
            article = NewsArticle(**article_data)
            self.session.add(article)
            self.session.commit()
            self.session.refresh(article)
            return article
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_by_id(self, article_id: int) -> Optional[NewsArticle]:
        """根据 ID 获取文章"""
        return self.session.query(NewsArticle).filter_by(id=article_id).first()
    
    def get_unanalyzed(self, limit: int = 20) -> List[NewsArticle]:
        """获取未分析的文章"""
        return (
            self.session.query(NewsArticle)
            .filter_by(is_analyzed=False)
            .order_by(desc(NewsArticle.published_at))
            .limit(limit)
            .all()
        )
    
    def search(
        self,
        keyword: Optional[str] = None,
        source: Optional[str] = None,
        source_type: Optional[str] = None,
        category: Optional[str] = None,
        analyzed: Optional[bool] = None,
        limit: int = 20,
        offset: int = 0,
        sort_by: str = "published_at",
        order: str = "desc"
    ) -> Tuple[List[NewsArticle], int]:
        """
        搜索文章
        
        Returns:
            (文章列表, 总数) 元组
        """
        query = self.session.query(NewsArticle)
        
        # 搜索条件
        if keyword:
            keyword_pattern = f"%{keyword}%"
            query = query.filter(
                or_(
                    NewsArticle.title.like(keyword_pattern),
                    NewsArticle.summary.like(keyword_pattern)
                )
            )
        
        if source:
            query = query.filter(NewsArticle.source == source)
        
        if source_type:
            query = query.filter(NewsArticle.source_type == source_type)
        
        if category:
            query = query.filter(NewsArticle.category == category)
        
        if analyzed is not None:
            query = query.filter(NewsArticle.is_analyzed == analyzed)
        
        # 排序
        order_func = desc if order == "desc" else asc
        if sort_by == "published_at":
            query = query.order_by(order_func(NewsArticle.published_at))
        elif sort_by == "crawled_at":
            query = query.order_by(order_func(NewsArticle.crawled_at))
        elif sort_by == "title":
            order_func = asc if order == "asc" else desc
            query = query.order_by(order_func(NewsArticle.title))
        
        # 总数
        total = query.count()
        
        # 分页
        articles = query.offset(offset).limit(limit).all()
        
        return articles, total
    
    def mark_as_analyzed(self, article_id: int) -> bool:
        """标记文章为已分析"""
        article = self.get_by_id(article_id)
        if article:
            article.is_analyzed = True
            self.session.commit()
            return True
        return False
    
    def get_recent(self, days: int = 1, limit: int = 10) -> List[NewsArticle]:
        """获取最近 N 天的文章"""
        cutoff_date = datetime.now() - timedelta(days=days)
        return (
            self.session.query(NewsArticle)
            .filter(NewsArticle.published_at >= cutoff_date)
            .order_by(desc(NewsArticle.published_at))
            .limit(limit)
            .all()
        )
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        total = self.session.query(NewsArticle).count()
        analyzed = self.session.query(NewsArticle).filter_by(is_analyzed=True).count()
        
        today = datetime.now().date()
        today_count = self.session.query(NewsArticle).filter(
            func.date(NewsArticle.crawled_at) == today
        ).count()
        
        return {
            'total_articles': total,
            'analyzed_count': analyzed,
            'today_articles': today_count
        }
