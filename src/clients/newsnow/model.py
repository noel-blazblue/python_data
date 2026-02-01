"""
NewsNow API 请求/响应模型
"""
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class HotlistItem:
    """热榜单项"""

    id: str
    title: str
    url: str
    mobile_url: str
    extra: dict

    @classmethod
    def from_dict(cls, data: dict) -> "HotlistItem":
        return cls(
            id=data.get("id", ""),
            title=data.get("title", ""),
            url=data.get("url", ""),
            mobile_url=data.get("mobileUrl", ""),
            extra=data.get("extra", {}),
        )


@dataclass
class HotlistResponse:
    """热榜响应"""

    status: str  # "success" | "cache"
    id: str
    updated_time: int
    items: list[HotlistItem]

    @classmethod
    def from_dict(cls, data: dict) -> "HotlistResponse":
        items = [
            HotlistItem.from_dict(item)
            for item in data.get("items", [])
        ]
        return cls(
            status=data.get("status", ""),
            id=data.get("id", ""),
            updated_time=data.get("updatedTime", 0),
            items=items,
        )
