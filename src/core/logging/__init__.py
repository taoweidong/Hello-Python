"""核心日志模块

提供统一的日志接口，支持多种输出方式和配置。
设计为与具体日志实现解耦，便于替换和扩展。
"""

from .logger import Logger, get_logger, setup_logger

__all__ = ["Logger", "get_logger", "setup_logger"]
