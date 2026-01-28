from src.db.models import NewsAnalysis
from typing import List, Optional, Dict, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc


class AnalysisRepository:
    """分析结果数据访问层"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def add(self, article_id: int, analysis_data: Dict) -> NewsAnalysis:
        """保存分析结果"""
        try:
            analysis = NewsAnalysis(
                article_id=article_id,
                **analysis_data
            )
            self.session.add(analysis)
            self.session.commit()
            self.session.refresh(analysis)
            return analysis
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_by_article_id(self, article_id: int) -> Optional[NewsAnalysis]:
        """根据文章 ID 获取分析结果"""
        return (
            self.session.query(NewsAnalysis)
            .filter_by(article_id=article_id)
            .first()
        )
    
    def get_recent(self, limit: int = 20, offset: int = 0) -> Tuple[List[NewsAnalysis], int]:
        """获取最近的分析结果"""
        query = self.session.query(NewsAnalysis)
        total = query.count()
        analyses = (
            query.order_by(desc(NewsAnalysis.created_at))
            .offset(offset)
            .limit(limit)
            .all()
        )
        return analyses, total
    
    def get_stats(self) -> int:
        """获取分析结果总数"""
        return self.session.query(NewsAnalysis).count()
