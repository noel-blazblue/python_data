from typing import List, Optional, Dict, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from src.db.models import NewsSummary

class SummaryRepository:
    """摘要数据访问层"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def add(self, summary_data: Dict) -> NewsSummary:
        """保存摘要"""
        try:
            summary = NewsSummary(**summary_data)
            self.session.add(summary)
            self.session.commit()
            self.session.refresh(summary)
            return summary
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_by_date(self, summary_date: datetime, summary_type: str = 'daily') -> Optional[NewsSummary]:
        """根据日期获取摘要"""
        return (
            self.session.query(NewsSummary)
            .filter_by(
                summary_date=summary_date,
                summary_type=summary_type
            )
            .first()
        )
