"""
数据库模型和连接管理
"""
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
import yaml
import pytz

Base = declarative_base()


class NewsArticle(Base):
    """新闻文章表"""
    __tablename__ = 'news_articles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False, index=True)
    summary = Column(Text)  # 摘要
    content = Column(Text)  # 完整内容（可选）
    url = Column(String(1000), unique=True, nullable=False, index=True)
    source = Column(String(200), nullable=False, index=True)  # 新闻源名称
    source_type = Column(String(50))  # 来源类型：domestic/international
    published_at = Column(DateTime, index=True)  # 发布时间
    crawled_at = Column(DateTime, default=datetime.utcnow, index=True)  # 抓取时间
    language = Column(String(20), default='zh')  # 语言：zh/en
    category = Column(String(100))  # 分类
    tags = Column(String(500))  # 标签（逗号分隔）
    
    # 状态字段
    is_analyzed = Column(Boolean, default=False, index=True)  # 是否已分析
    is_processed = Column(Boolean, default=False)  # 是否已处理
    
    def __repr__(self):
        return f"<NewsArticle(title='{self.title[:50]}...', source='{self.source}')>"


class NewsAnalysis(Base):
    """新闻分析结果表"""
    __tablename__ = 'news_analysis'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(Integer, nullable=False, index=True)  # 关联的文章ID
    analysis_type = Column(String(50), default='general')  # 分析类型
    analysis_content = Column(Text, nullable=False)  # 分析内容
    sentiment = Column(String(20))  # 情感分析：positive/negative/neutral
    sentiment_score = Column(Float)  # 情感分数
    key_points = Column(Text)  # 关键要点（JSON格式）
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<NewsAnalysis(article_id={self.article_id}, sentiment='{self.sentiment}')>"


class NewsSummary(Base):
    """新闻摘要表（用于批量分析）"""
    __tablename__ = 'news_summaries'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    summary_date = Column(DateTime, nullable=False, index=True)  # 摘要日期
    summary_type = Column(String(50), default='daily')  # 摘要类型：daily/weekly
    summary_content = Column(Text, nullable=False)  # 摘要内容
    article_count = Column(Integer, default=0)  # 包含的文章数量
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<NewsSummary(summary_date={self.summary_date}, type='{self.summary_type}')>"


class DatabaseManager:
    """数据库管理类"""
    
    def __init__(self, config_path='app_config.yaml'):
        """初始化数据库连接"""
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        db_config = config.get('database', {})
        db_type = db_config.get('type', 'sqlite')
        
        if db_type == 'sqlite':
            db_path = db_config.get('path', 'data/news.db')
            # 确保目录存在
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        elif db_type == 'postgresql':
            host = db_config.get('host', 'localhost')
            port = db_config.get('port', 5432)
            user = db_config.get('user')
            password = db_config.get('password')
            dbname = db_config.get('dbname')
            self.engine = create_engine(
                f'postgresql://{user}:{password}@{host}:{port}/{dbname}',
                echo=False
            )
        else:
            raise ValueError(f"不支持的数据库类型: {db_type}")
        
        # 创建表
        Base.metadata.create_all(self.engine)
        
        # 创建会话工厂
        self.Session = sessionmaker(bind=self.engine)
    
    def get_session(self):
        """获取数据库会话"""
        return self.Session()
    
    def add_article(self, article_data):
        """添加新闻文章"""
        session = self.get_session()
        try:
            # 检查是否已存在
            existing = session.query(NewsArticle).filter_by(url=article_data['url']).first()
            if existing:
                return None  # 已存在，返回 None 而不是 existing
            
            # 处理时区感知的 datetime
            if 'published_at' in article_data and article_data['published_at']:
                if article_data['published_at'].tzinfo is not None:
                    # 转换为 UTC 存储
                    article_data['published_at'] = article_data['published_at'].astimezone(pytz.UTC).replace(tzinfo=None)
            
            if 'crawled_at' in article_data and article_data['crawled_at']:
                if article_data['crawled_at'].tzinfo is not None:
                    article_data['crawled_at'] = article_data['crawled_at'].astimezone(pytz.UTC).replace(tzinfo=None)
            
            article = NewsArticle(**article_data)
            session.add(article)
            session.commit()
            session.refresh(article)
            return article
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_unanalyzed_articles(self, limit=20):
        """获取未分析的文章"""
        session = self.get_session()
        try:
            articles = session.query(NewsArticle).filter_by(
                is_analyzed=False
            ).order_by(NewsArticle.published_at.desc()).limit(limit).all()
            return articles
        finally:
            session.close()
    
    def save_analysis(self, article_id, analysis_data):
        """保存分析结果"""
        session = self.get_session()
        try:
            analysis = NewsAnalysis(article_id=article_id, **analysis_data)
            session.add(analysis)
            
            # 更新文章状态
            article = session.query(NewsArticle).filter_by(id=article_id).first()
            if article:
                article.is_analyzed = True
            
            session.commit()
            return analysis
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def save_summary(self, summary_data):
        """保存摘要"""
        session = self.get_session()
        try:
            summary = NewsSummary(**summary_data)
            session.add(summary)
            session.commit()
            return summary
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
