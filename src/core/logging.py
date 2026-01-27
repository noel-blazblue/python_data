"""
日志配置模块
"""
import os
import sys
from loguru import logger
from pathlib import Path


def setup_logging(log_level: str = "INFO", log_dir: str = "logs"):
    """
    配置日志系统
    
    Args:
        log_level: 日志级别
        log_dir: 日志目录
    """
    # 移除默认处理器
    logger.remove()
    
    # 确保日志目录存在
    os.makedirs(log_dir, exist_ok=True)
    
    # 控制台输出（带颜色）
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True
    )
    
    # 文件输出（按天轮转）
    logger.add(
        f"{log_dir}/news_service_{{time:YYYY-MM-DD}}.log",
        rotation="00:00",  # 每天午夜轮转
        retention="7 days",  # 保留7天
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        encoding="utf-8"
    )
    
    # 错误日志单独文件
    logger.add(
        f"{log_dir}/error_{{time:YYYY-MM-DD}}.log",
        rotation="00:00",
        retention="30 days",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        encoding="utf-8"
    )
    
    return logger
