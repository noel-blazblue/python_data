"""
新闻查询工具
用于查询和分析已存储的新闻数据
"""
import sys
from database import DatabaseManager
from datetime import datetime, timedelta
from loguru import logger


def query_recent_news(limit=10, days=1):
    """查询最近的新闻"""
    db = DatabaseManager()
    session = db.get_session()
    
    try:
        from database import NewsArticle
        cutoff_date = datetime.now() - timedelta(days=days)
        
        articles = session.query(NewsArticle).filter(
            NewsArticle.published_at >= cutoff_date
        ).order_by(NewsArticle.published_at.desc()).limit(limit).all()
        
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
    
    finally:
        session.close()


def query_analysis_results(limit=10):
    """查询分析结果"""
    db = DatabaseManager()
    session = db.get_session()
    
    try:
        from database import NewsAnalysis, NewsArticle
        
        analyses = session.query(NewsAnalysis).order_by(
            NewsAnalysis.created_at.desc()
        ).limit(limit).all()
        
        print(f"\n最近的分析结果（共 {len(analyses)} 条）:\n")
        print("=" * 80)
        
        for analysis in analyses:
            article = session.query(NewsArticle).filter_by(id=analysis.article_id).first()
            
            if article:
                print(f"\n文章标题: {article.title}")
                print(f"来源: {article.source}")
            
            print(f"分析内容: {analysis.analysis_content[:300]}...")
            print(f"情感倾向: {analysis.sentiment} (分数: {analysis.sentiment_score})")
            print(f"分析时间: {analysis.created_at}")
            print("-" * 80)
    
    finally:
        session.close()


def query_statistics():
    """查询统计信息"""
    db = DatabaseManager()
    session = db.get_session()
    
    try:
        from database import NewsArticle, NewsAnalysis, NewsSummary
        from sqlalchemy import func
        
        # 总文章数
        total_articles = session.query(NewsArticle).count()
        
        # 已分析文章数
        analyzed_count = session.query(NewsArticle).filter_by(is_analyzed=True).count()
        
        # 按来源统计
        source_stats = session.query(
            NewsArticle.source,
            func.count(NewsArticle.id).label('count')
        ).group_by(NewsArticle.source).all()
        
        # 按类型统计
        type_stats = session.query(
            NewsArticle.source_type,
            func.count(NewsArticle.id).label('count')
        ).group_by(NewsArticle.source_type).all()
        
        # 分析结果数
        total_analyses = session.query(NewsAnalysis).count()
        
        # 摘要数
        total_summaries = session.query(NewsSummary).count()
        
        print("\n" + "=" * 80)
        print("数据库统计信息")
        print("=" * 80)
        print(f"\n总文章数: {total_articles}")
        print(f"已分析文章数: {analyzed_count} ({analyzed_count/total_articles*100:.1f}%)" if total_articles > 0 else "已分析文章数: 0")
        print(f"分析结果数: {total_analyses}")
        print(f"摘要数: {total_summaries}")
        
        print("\n按来源统计:")
        for source, count in source_stats:
            print(f"  {source}: {count} 篇")
        
        print("\n按类型统计:")
        for source_type, count in type_stats:
            print(f"  {source_type}: {count} 篇")
        
        print("=" * 80)
    
    finally:
        session.close()


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法:")
        print("  python query_news.py recent [limit] [days]  # 查询最近新闻")
        print("  python query_news.py analysis [limit]      # 查询分析结果")
        print("  python query_news.py stats                  # 查询统计信息")
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
