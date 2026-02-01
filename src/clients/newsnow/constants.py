"""
NewsNow API 常量
"""

BASE_URL = "https://newsnow.busiyi.world/api/s"

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
    "Cache-Control": "no-cache",
}

DEFAULT_TIMEOUT = 10
DEFAULT_MAX_RETRIES = 2
DEFAULT_MIN_RETRY_WAIT = 3
DEFAULT_MAX_RETRY_WAIT = 5

VALID_STATUSES = ("success", "cache")
