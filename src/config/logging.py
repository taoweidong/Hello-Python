"""日志管理模块

提供统一的日志配置和管理功能，支持控制台和文件输出。
"""

import logging
import sys
from typing import Optional
from pathlib import Path
from loguru import logger
from .configuration import get_config, ConfigurationError


class LoggerError(Exception):
    """日志错误异常"""
    pass


class LoggerManager:
    """日志管理器
    
   管应用程序的日志配置，支持多种输出格式和级别。
    """
    
    def __init__(self) -> None:
        """初始化日志管理器"""
        self._is_configured: bool = False
        self._logger = logger
        
    def setup_logger(self, config=None) -> None:
        """设置日志记录器
        
        Args:
            config: 配置对象，如果为None则使用全局配置
            
        Raises:
            LoggerError: 日志配置失败时
        """
        try:
            if config is None:
                try:
                    config = get_config()
                except ConfigurationError as e:
                    raise LoggerError(f"获取配置失败: {e}")
            
            #移除默认的日志处理器
            self._logger.remove()
            
            # 添加控制台输出
            self._logger.add(
                sys.stdout,
                level=config.LOG_LEVEL,
                format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
            )
            
            # 添加文件输出
            self._setup_file_logging(config)
            
            self._is_configured = True
            self._logger.info(f"日志系统已配置，级别: {config.LOG_LEVEL}")
            
        except Exception as e:
            raise LoggerError(f"日志配置失败: {e}")
    
    def _setup_file_logging(self, config) -> None:
        """设置文件日志记录
        
        Args:
            config: 配置对象
        """
        try:
            #确保logs目录存在
            logs_dir = Path("logs")
            logs_dir.mkdir(exist_ok=True)
            
            log_file = logs_dir / "app.log"
            self._logger.add(
                str(log_file),
                level=config.LOG_LEVEL,
                rotation="10 MB",
                retention="10 days",
                compression="zip",
                format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
            )
            
        except Exception as e:
            self._logger.warning(f"无法创建日志文件: {e}")
    
    @property
    def is_configured(self) -> bool:
        """检查日志是否已配置
        
        Returns:
            bool: 是否已配置
        """
        return self._is_configured
    
    def get_logger(self) -> logger:
        """获取日志记录器
        
        Returns:
            logger: 日志记录器实例
        """
        return self._logger


#全局日志管理器实例
_logger_manager: Optional[LoggerManager] = None


def get_logger_manager() -> LoggerManager:
    """获取全局日志管理器实例
    
    Returns:
        LoggerManager: 日志管理器实例
    """
    global _logger_manager
    if _logger_manager is None:
        _logger_manager = LoggerManager()
    return _logger_manager


def setup_logger(config=None) -> logger:
    """设置并获取日志记录器
    
    Args:
        config: 配置对象
        
    Returns:
        logger:配置好的日志记录器
        
    Raises:
        LoggerError: 日志配置失败时
    """
    manager = get_logger_manager()
    manager.setup_logger(config)
    return manager.get_logger()


def get_logger() -> logger:
    """获取日志记录器
    
    Returns:
        logger: 日志记录器实例
    """
    manager = get_logger_manager()
    return manager.get_logger()