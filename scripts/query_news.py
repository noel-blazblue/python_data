"""
新闻查询工具（重构版）
"""
import sys
from datetime import datetime, timedelta
from loguru import logger

from src.config import get_settings
from src.core.logging import setup_logging
from src.db import init_db, get_db_manager
from src.db.repositories import ArticleRepository, AnalysisRepository


def query_recent_news(limit=10, days=1):
    """查询最近的新闻"""
    config = get_settings()
    setup_logging(log_level=config.app.log_level)
    
    init_db(config.database.get_url())
    db_manager = get_db_manager()
    
    with db_manager.session_scope() as session:
        article_repo = ArticleRepository(session)
        articles = article_repo.get_recent(days=days, limit=limit)
        
        print(f"\n最近 {days} 天的新闻（共 {len(articles)} 篇）:\n")
        print("=" * 80)
        
        for article in articles:
            print(f"\n标题: {article.title}")
            print(f"来源: {article.source} ({article.source_type})")
            print(f"发布时间: {article.published_at}")
            if article.summary:
                print(f"摘要: {article.summary[:200]}...")
            print(f"链接: {article.url}")
            print(f"已分析: {'是' if article.is_analyzed else '否'}")
            print("-" * 80)


def query_analysis_results(limit=10):
    """查询分析结果"""
    config = get_settings()
    setup_logging(log_level=config.app.log_level)
    
    init_db(config.database.get_url())
    db_manager = get_db_manager()
    
    with db_manager.session_scope() as session:
        analysis_repo = AnalysisRepository(session)
        article_repo = ArticleRepository(session)
        
        analyses, total = analysis_repo.get_recent(limit=limit)
        
        print(f"\n最近的分析结果（共 {len(analyses)} 条）:\n")
        print("=" * 80)
        
        for analysis in analyses:
            article = article_repo.get_by_id(analysis.article_id)
            
            if article:
                print(f"\n文章标题: {article.title}")
                print(f"来源: {article.source}")
            
            print(f"分析内容: {analysis.analysis_content[:300]}...")
            print(f"情感倾向: {analysis.sentiment} (分数: {analysis.sentiment_score})")
            print(f"分析时间: {analysis.created_at}")
            print("-" * 80)


def query_statistics():
    """查询统计信息"""
    config = get_settings()
    setup_logging(log_level=config.app.log_level)
    
    init_db(config.database.get_url())
    db_manager = get_db_manager()
    
    with db_manager.session_scope() as session:
        article_repo = ArticleRepository(session)
        analysis_repo = AnalysisRepository(session)
        
        stats = article_repo.get_stats()
        total_analyses = analysis_repo.get_stats()
        
        print("\n" + "=" * 80)
        print("数据库统计信息")
        print("=" * 80)
        print(f"\n总文章数: {stats['total_articles']}")
        print(f"已分析文章数: {stats['analyzed_count']} ({stats['analyzed_count']/stats['total_articles']*100:.1f}%)" if stats['total_articles'] > 0 else "已分析文章数: 0")
        print(f"分析结果数: {total_analyses}")
        print(f"今日新增: {stats['today_articles']}")
        print("=" * 80)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法:")
        print("  python -m scripts.query_news recent [limit] [days]  # 查询最近新闻")
        print("  python -m scripts.query_news analysis [limit]      # 查询分析结果")
        print("  python -m scripts.query_news stats                  # 查询统计信息")
        return
    
    command = sys.argv[1]
    
    if command == 'recent':
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        days = int(sys.argv[3]) if len(sys.argv) > 3 else 1
        query_recent_news(limit, days)
    
    elif command == 'analysis':
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        query_analysis_results(limit)
    
    elif command == 'stats':
        query_statistics()
    
    else:
        print(f"未知命令: {command}")


if __name__ == '__main__':
    main()
