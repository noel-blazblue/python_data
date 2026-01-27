"""
平台热榜抓取器
"""
import json
import random
import time
from typing import Dict, List, Tuple, Optional, Union
from datetime import datetime
import requests
from loguru import logger
import pytz

from src.crawlers.base import BaseCrawler
from src.core.exceptions import CrawlerException


class PlatformCrawler(BaseCrawler):
    """平台热榜抓取器"""
    
    # 默认 API 地址
    DEFAULT_API_URL = "https://newsnow.busiyi.world/api/s"
    
    # 默认请求头
    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
        "Cache-Control": "no-cache",
    }
    
    def __init__(self, config, proxy_url: Optional[str] = None, api_url: Optional[str] = None):
        """
        初始化平台抓取器
        
        Args:
            config: 配置对象（Settings）
            proxy_url: 代理服务器 URL（可选）
            api_url: API 基础 URL（可选）
        """
        self.config = config
        self.timezone = config.app.timezone_obj
        self.proxy_url = proxy_url
        self.api_url = api_url or self.DEFAULT_API_URL
    
    def fetch_data(
        self,
        id_info: Union[str, Tuple[str, str]],
        max_retries: int = 2,
        min_retry_wait: int = 3,
        max_retry_wait: int = 5,
    ) -> Tuple[Optional[str], str, str]:
        """
        获取指定平台数据，支持重试
        
        Args:
            id_info: 平台ID 或 (平台ID, 别名) 元组
            max_retries: 最大重试次数
            min_retry_wait: 最小重试等待时间（秒）
            max_retry_wait: 最大重试等待时间（秒）
            
        Returns:
            (响应文本, 平台ID, 别名) 元组，失败时响应文本为 None
        """
        if isinstance(id_info, tuple):
            id_value, alias = id_info
        else:
            id_value = id_info
            alias = id_value
        
        url = f"{self.api_url}?id={id_value}&latest"
        
        proxies = None
        if self.proxy_url:
            proxies = {"http": self.proxy_url, "https": self.proxy_url}
        
        retries = 0
        while retries <= max_retries:
            try:
                response = requests.get(
                    url,
                    proxies=proxies,
                    headers=self.DEFAULT_HEADERS,
                    timeout=10,
                )
                response.raise_for_status()
                
                data_text = response.text
                data_json = json.loads(data_text)
                
                status = data_json.get("status", "未知")
                if status not in ["success", "cache"]:
                    raise ValueError(f"响应状态异常: {status}")
                
                return data_text, id_value, alias
            
            except Exception as e:
                retries += 1
                if retries <= max_retries:
                    base_wait = random.uniform(min_retry_wait, max_retry_wait)
                    additional_wait = (retries - 1) * random.uniform(1, 2)
                    wait_time = base_wait + additional_wait
                    logger.debug(f"请求 {id_value} 失败: {e}. {wait_time:.2f}秒后重试...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"请求 {id_value} 失败: {e}")
                    return None, id_value, alias
        
        return None, id_value, alias
    
    def crawl_websites(
        self,
        ids_list: List[Union[str, Tuple[str, str]]],
        request_interval: int = 100,
    ) -> Tuple[Dict, Dict, List]:
        """
        爬取多个平台数据
        
        Args:
            ids_list: 平台ID列表
            request_interval: 请求间隔（毫秒）
            
        Returns:
            (结果字典, ID到名称的映射, 失败ID列表) 元组
        """
        results = {}
        id_to_name = {}
        failed_ids = []
        
        for i, id_info in enumerate(ids_list):
            if isinstance(id_info, tuple):
                id_value, name = id_info
            else:
                id_value = id_info
                name = id_value
            
            id_to_name[id_value] = name
            response, _, _ = self.fetch_data(id_info)
            
            if response:
                try:
                    data = json.loads(response)
                    results[id_value] = {}
                    
                    for index, item in enumerate(data.get("items", []), 1):
                        title = item.get("title")
                        if title is None or isinstance(title, float) or not str(title).strip():
                            continue
                        title = str(title).strip()
                        url = item.get("url", "")
                        mobile_url = item.get("mobileUrl", "")
                        
                        if title in results[id_value]:
                            results[id_value][title]["ranks"].append(index)
                        else:
                            results[id_value][title] = {
                                "ranks": [index],
                                "url": url,
                                "mobileUrl": mobile_url,
                            }
                except json.JSONDecodeError:
                    logger.error(f"解析 {id_value} 响应失败")
                    failed_ids.append(id_value)
                except Exception as e:
                    logger.error(f"处理 {id_value} 数据出错: {e}")
                    failed_ids.append(id_value)
            else:
                failed_ids.append(id_value)
            
            # 请求间隔（除了最后一个）
            if i < len(ids_list) - 1:
                actual_interval = request_interval + random.randint(-10, 20)
                actual_interval = max(50, actual_interval)
                time.sleep(actual_interval / 1000)
        
        return results, id_to_name, failed_ids
    
    def fetch(self, source_config: Dict) -> List[Dict]:
        """
        抓取平台热榜数据
        
        Args:
            source_config: 平台配置，包含 id, name 等
            
        Returns:
            文章列表
        """
        articles = []
        platform_id = source_config.get('id')
        platform_name = source_config.get('name', platform_id)
        
        if not platform_id:
            return articles
        
        try:
            response, _, _ = self.fetch_data((platform_id, platform_name))
            
            if not response:
                return articles
            
            data = json.loads(response)
            now = datetime.now(self.timezone)
            
            for item in data.get("items", []):
                title = item.get("title")
                if title is None or isinstance(title, float) or not str(title).strip():
                    continue
                
                title = str(title).strip()
                url = item.get("mobileUrl") or item.get("url") or ""
                
                if not url:
                    continue
                
                article = {
                    "title": title,
                    "summary": None,
                    "content": None,
                    "url": url,
                    "source": platform_name,
                    "source_type": "domestic",
                    "published_at": None,
                    "crawled_at": now,
                    "language": "zh",
                    "category": "hot_platform",
                    "tags": platform_id,
                }
                
                articles.append(article)
            
            logger.info(f"成功抓取 {len(articles)} 条热榜数据来自 {platform_name}")
            return articles
        
        except Exception as e:
            logger.error(f"抓取平台数据失败 {platform_name}: {e}")
            raise CrawlerException(f"抓取平台数据失败: {e}") from e
