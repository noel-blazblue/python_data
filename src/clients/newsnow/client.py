"""
NewsNow API Client
"""
import json
import random
import time
from typing import Optional

import requests
from loguru import logger

from .constants import (
    BASE_URL,
    DEFAULT_HEADERS,
    DEFAULT_MAX_RETRIES,
    DEFAULT_MAX_RETRY_WAIT,
    DEFAULT_MIN_RETRY_WAIT,
    DEFAULT_TIMEOUT,
    VALID_STATUSES,
)
from .exceptions import NewsNowRequestError, NewsNowResponseError
from .model import HotlistResponse


class NewsNowClient:
    """NewsNow 热榜 API 客户端"""

    def __init__(
        self,
        base_url: Optional[str] = None,
        proxy_url: Optional[str] = None,
        headers: Optional[dict] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        min_retry_wait: float = DEFAULT_MIN_RETRY_WAIT,
        max_retry_wait: float = DEFAULT_MAX_RETRY_WAIT,
    ):
        """
        初始化 NewsNow 客户端

        Args:
            base_url: API 基础 URL，默认使用官方地址
            proxy_url: 代理服务器 URL（可选）
            headers: 自定义请求头（可选）
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
            min_retry_wait: 最小重试等待时间（秒）
            max_retry_wait: 最大重试等待时间（秒）
        """
        self.base_url = base_url or BASE_URL
        self.proxy_url = proxy_url
        self.headers = headers or DEFAULT_HEADERS.copy()
        self.timeout = timeout
        self.max_retries = max_retries
        self.min_retry_wait = min_retry_wait
        self.max_retry_wait = max_retry_wait

    def _build_url(self, platform_id: str, use_latest: bool = True) -> str:
        """构建请求 URL"""
        url = f"{self.base_url}?id={platform_id}"
        if use_latest:
            url += "&latest"
        return url

    def _request(self, url: str) -> dict:
        """
        执行 HTTP 请求，带重试逻辑

        Returns:
            解析后的 JSON 字典

        Raises:
            NewsNowRequestError: 请求失败
            NewsNowResponseError: 响应状态异常
        """
        proxies = None
        if self.proxy_url:
            proxies = {"http": self.proxy_url, "https": self.proxy_url}

        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                response = requests.get(
                    url,
                    proxies=proxies,
                    headers=self.headers,
                    timeout=self.timeout,
                )
                response.raise_for_status()

                data = json.loads(response.text)
                status = data.get("status", "")

                if status not in VALID_STATUSES:
                    raise NewsNowResponseError(f"响应状态异常: {status}")

                return data

            except requests.RequestException as e:
                last_error = NewsNowRequestError(f"请求失败: {e}")
            except json.JSONDecodeError as e:
                last_error = NewsNowResponseError(f"响应解析失败: {e}")
            except NewsNowResponseError:
                raise

            if attempt < self.max_retries:
                wait_time = random.uniform(
                    self.min_retry_wait, self.max_retry_wait
                ) + (attempt * random.uniform(1, 2))
                logger.debug(f"请求失败，{wait_time:.2f} 秒后重试...")
                time.sleep(wait_time)

        raise last_error

    def get_hotlist(
        self,
        platform_id: str,
        use_latest: bool = True,
    ) -> HotlistResponse:
        """
        获取平台热榜

        Args:
            platform_id: 平台 ID（如 weibo、zhihu）
            use_latest: 是否使用 latest 参数获取最新数据

        Returns:
            HotlistResponse 热榜响应

        Raises:
            NewsNowRequestError: 请求失败
            NewsNowResponseError: 响应异常
        """
        url = self._build_url(platform_id, use_latest)
        data = self._request(url)
        return HotlistResponse.from_dict(data)

    def get_hotlist_raw(
        self,
        platform_id: str,
        use_latest: bool = True,
    ) -> Optional[str]:
        """
        获取平台热榜原始 JSON 文本（兼容旧调用方式）

        Args:
            platform_id: 平台 ID
            use_latest: 是否使用 latest 参数

        Returns:
            原始响应文本，失败返回 None
        """
        try:
            url = self._build_url(platform_id, use_latest)
            data = self._request(url)
            return json.dumps(data, ensure_ascii=False)
        except (NewsNowRequestError, NewsNowResponseError) as e:
            logger.error(f"获取 {platform_id} 热榜失败: {e}")
            return None
