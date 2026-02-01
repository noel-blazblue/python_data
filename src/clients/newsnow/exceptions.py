"""
NewsNow API 自定义异常
"""


class NewsNowAPIError(Exception):
    """NewsNow API 基础异常"""

    pass


class NewsNowRequestError(NewsNowAPIError):
    """请求失败（网络、超时等）"""

    pass


class NewsNowResponseError(NewsNowAPIError):
    """响应异常（状态码、status 字段、解析失败等）"""

    pass
