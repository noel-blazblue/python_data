"""
分析服务 - 业务逻辑层
"""
import time
from typing import List, Dict
from datetime import date, datetime
from loguru import logger

from src.db.repositories import ArticleRepository, AnalysisRepository, SummaryRepository
from src.analyzers import AIAnalyzer
from src.core.exceptions import AnalysisException


class AnalysisService:
    """分析服务"""
    
    def __init__(
        self,
        db_manager,
        analyzer: AIAnalyzer,
        config
    ):
        """
        初始化分析服务
        
        Args:
            db_manager: 数据库管理器
            analyzer: AI 分析器
            config: 配置对象
        """
        self.db_manager = db_manager
        self.analyzer = analyzer
        self.config = config
    
    def analyze_unanalyzed_articles(self, limit: int = None) -> int:
        """
        分析未分析的文章
        
        Args:
            limit: 分析数量限制，None 则使用配置中的值
            
        Returns:
            成功分析的文章数量
        """
        if not self.config.analysis.enabled:
            logger.info("AI 分析功能已禁用")
            return 0
        
        limit = limit or self.config.analysis.max_articles_per_analysis
        
        logger.info(f"开始分析未分析的文章（限制: {limit}）...")
        
        with self.db_manager.session_scope() as session:
            article_repo = ArticleRepository(session)
            analysis_repo = AnalysisRepository(session)
            
            # 获取未分析的文章
            articles = article_repo.get_unanalyzed(limit=limit)
            
            if not articles:
                logger.info("没有需要分析的文章")
                return 0
            
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
                    analysis_result = self.analyzer.analyze_single(article_dict)
                    
                    if analysis_result:
                        # 保存分析结果
                        analysis_repo.add(article.id, analysis_result)
                        
                        # 标记为已分析
                        article_repo.mark_as_analyzed(article.id)
                        
                        analyzed_count += 1
                        logger.info(f"已分析: {article.title[:50]}...")
                    
                    # 避免请求过快
                    time.sleep(1)
                
                except AnalysisException as e:
                    logger.error(f"分析文章失败 {article.id}: {e}")
                    continue
                except Exception as e:
                    logger.error(f"分析文章失败 {article.id}: {e}")
                    continue
        
        logger.info(f"成功分析 {analyzed_count} 篇文章")
        return analyzed_count
    
    def generate_daily_summary(self) -> bool:
        """
        生成每日摘要
        
        Returns:
            是否成功生成
        """
        logger.info("生成每日摘要...")
        
        try:
            with self.db_manager.session_scope() as session:
                article_repo = ArticleRepository(session)
                summary_repo = SummaryRepository(session)
                
                # 获取今天的文章
                today = date.today()
                articles = article_repo.get_recent(days=1, limit=50)
                
                if not articles:
                    logger.info("今天没有文章可生成摘要")
                    return False
                
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
                summary_result = self.analyzer.analyze_batch(articles_dict)
                
                if summary_result:
                    summary_data = {
                        'summary_date': datetime.combine(today, datetime.min.time()),
                        'summary_type': 'daily',
                        'summary_content': summary_result['summary_content'],
                        'article_count': summary_result['article_count']
                    }
                    
                    summary_repo.add(summary_data)
                    logger.info("每日摘要生成成功")
                    return True
            
            return False
        
        except Exception as e:
            logger.error(f"生成每日摘要失败: {e}")
            return False
