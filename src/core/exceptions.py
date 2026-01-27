"""
自定义异常类
"""


class NewsServiceException(Exception):
    """新闻服务基础异常"""
    pass


class CrawlerException(NewsServiceException):
    """抓取器异常"""
    pass


class AnalysisException(NewsServiceException):
    """分析异常"""
    pass


class DatabaseException(NewsServiceException):
    """数据库异常"""
    pass


class ConfigurationException(NewsServiceException):
    """配置异常"""
    pass
