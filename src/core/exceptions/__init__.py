"""核心异常处理模块

定义项目中使用的核心异常基类和标准异常类型。
"""

from .base import CoreException, ConfigurationError, ValidationError, DatabaseError, InitializationError

__all__ = [
    'CoreException',
    'ConfigurationError', 
    'ValidationError',
    'DatabaseError',
    'InitializationError'
]