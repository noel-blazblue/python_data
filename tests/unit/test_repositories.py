"""
Repository 层单元测试示例
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from src.db.models import Base, NewsArticle
from src.db.repositories import ArticleRepository


@pytest.fixture
def db_session():
    """创建测试数据库会话"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def article_repo(db_session):
    """创建 ArticleRepository 实例"""
    return ArticleRepository(db_session)


def test_add_article(article_repo):
    """测试添加文章"""
    article_data = {
        "title": "测试文章",
        "summary": "这是测试摘要",
        "url": "https://example.com/test",
        "source": "测试源",
        "source_type": "domestic",
        "published_at": datetime.now(),
        "crawled_at": datetime.now(),
        "language": "zh"
    }
    
    article = article_repo.add(article_data)
    assert article is not None
    assert article.title == "测试文章"
    assert article.id is not None


def test_add_duplicate_article(article_repo):
    """测试添加重复文章"""
    article_data = {
        "title": "测试文章",
        "url": "https://example.com/test",
        "source": "测试源",
        "crawled_at": datetime.now()
    }
    
    # 第一次添加
    article1 = article_repo.add(article_data)
    assert article1 is not None
    
    # 第二次添加相同 URL
    article2 = article_repo.add(article_data)
    assert article2 is None  # 应该返回 None，因为已存在


def test_get_unanalyzed(article_repo):
    """测试获取未分析的文章"""
    # 添加几篇文章
    for i in range(5):
        article_data = {
            "title": f"测试文章 {i}",
            "url": f"https://example.com/test{i}",
            "source": "测试源",
            "crawled_at": datetime.now(),
            "is_analyzed": i < 2  # 前2篇已分析
        }
        article_repo.add(article_data)
    
    # 获取未分析的文章
    unanalyzed = article_repo.get_unanalyzed(limit=10)
    assert len(unanalyzed) == 3  # 应该有3篇未分析


def test_search_articles(article_repo):
    """测试搜索文章"""
    # 添加测试文章
    article_data = {
        "title": "Python 编程教程",
        "summary": "学习 Python 编程",
        "url": "https://example.com/python",
        "source": "测试源",
        "crawled_at": datetime.now()
    }
    article_repo.add(article_data)
    
    # 搜索
    articles, total = article_repo.search(keyword="Python", limit=10)
    assert total >= 1
    assert any("Python" in a.title for a in articles)
