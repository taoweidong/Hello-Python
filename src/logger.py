# src/logger.py
import logging
from loguru import logger
from src.config import settings

def setup_logger():
    """设置日志记录器"""
    # 移除默认的日志处理器
    logger.remove()
    
    # 添加控制台输出
    logger.add(
        lambda msg: print(msg, end=''),
        level=settings.LOG_LEVEL,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    )
    
    # 添加文件输出
    try:
        logger.add(
            "logs/app.log",
            level=settings.LOG_LEVEL,
            rotation="10 MB",
            retention="10 days",
            compression="zip",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
        )
    except Exception as e:
        print(f"无法创建日志文件: {e}")
    
    return logger