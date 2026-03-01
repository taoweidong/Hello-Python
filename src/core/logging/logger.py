"""统一日志管理器

提供类型安全的日志接口，支持控制台和文件输出，可配置日志级别和格式。
"""

import sys
from pathlib import Path

from loguru import logger as loguru_logger

from ..config import Settings, get_settings


class Logger:
    """日志管理器类

    封日志功能，提供统一的接口。
    """

    def __init__(self, settings: Settings | None = None):
        """初始化日志管理器

        Args:
            settings:配置对象，如果为None则使用全局配置
        """
        self._settings = settings or get_settings()
        self._logger = loguru_logger
        self._is_configured = False

    def setup(self) -> None:
        """设置日志配置"""
        if self._is_configured:
            return

        try:
            # 移除默认处理器
            self._logger.remove()

            # 添加控制台输出
            self._logger.add(sys.stdout, level=self._settings.LOG_LEVEL, format=self._settings.LOG_FORMAT)

            # 添加文件输出
            self._setup_file_logging()

            # 标记为已配置
            self._is_configured = True

            self.info(f"日志系统已配置，级别: {self._settings.LOG_LEVEL}")

        except Exception as e:
            # 如果配置失败，使用基本配置
            self._setup_basic_logging()
            self.error(f"日志配置失败，使用基本配置: {e}")

    def _setup_file_logging(self) -> None:
        """设置文件日志记录"""
        try:
            # 确保日志目录存在
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)

            log_file = log_dir / f"{self._settings.APP_NAME.lower()}.log"
            self._logger.add(
                str(log_file),
                level=self._settings.LOG_LEVEL,
                rotation="10 MB",
                retention="10 days",
                compression="zip",
                format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
            )

        except Exception as e:
            self.warning(f"无法创建日志文件: {e}")

    def _setup_basic_logging(self) -> None:
        """设置基本日志配置"""
        self._logger.remove()
        self._logger.add(sys.stdout, level="INFO")
        self._is_configured = True

    def debug(self, message: str, *args, **kwargs) -> None:
        """输出调试信息"""
        if not self._is_configured:
            self.setup()
        self._logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs) -> None:
        """输出信息"""
        if not self._is_configured:
            self.setup()
        self._logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs) -> None:
        """输出警告信息"""
        if not self._is_configured:
            self.setup()
        self._logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs) -> None:
        """输出错误信息"""
        if not self._is_configured:
            self.setup()
        self._logger.error(message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs) -> None:
        """输出严重错误信息"""
        if not self._is_configured:
            self.setup()
        self._logger.critical(message, *args, **kwargs)

    def exception(self, message: str, *args, **kwargs) -> None:
        """输出异常信息"""
        if not self._is_configured:
            self.setup()
        self._logger.exception(message, *args, **kwargs)

    @property
    def is_configured(self) -> bool:
        """检查日志是否已配置"""
        return self._is_configured

    def get_logger(self):
        """获取底层日志记录器"""
        if not self._is_configured:
            self.setup()
        return self._logger


# 全局日志实例
_global_logger: Logger | None = None


def get_logger(settings: Settings | None = None) -> Logger:
    """获取全局日志实例

    Args:
        settings:配置对象，如果为None则使用全局配置

    Returns:
        Logger: 日志实例
    """
    global _global_logger
    if _global_logger is None:
        _global_logger = Logger(settings)
    return _global_logger


def setup_logger(settings: Settings | None = None) -> Logger:
    """设置并获取日志实例

    Args:
        settings:配置对象

    Returns:
        Logger:配置好的日志实例
    """
    logger = get_logger(settings)
    logger.setup()
    return logger


def debug(message: str, *args, **kwargs) -> None:
    """全局调试日志函数"""
    get_logger().debug(message, *args, **kwargs)


def info(message: str, *args, **kwargs) -> None:
    """全局信息日志函数"""
    get_logger().info(message, *args, **kwargs)


def warning(message: str, *args, **kwargs) -> None:
    """全局警告日志函数"""
    get_logger().warning(message, *args, **kwargs)


def error(message: str, *args, **kwargs) -> None:
    """全局错误日志函数"""
    get_logger().error(message, *args, **kwargs)


def critical(message: str, *args, **kwargs) -> None:
    """全局严重错误日志函数"""
    get_logger().critical(message, *args, **kwargs)


def exception(message: str, *args, **kwargs) -> None:
    """全局异常日志函数"""
    get_logger().exception(message, *args, **kwargs)
