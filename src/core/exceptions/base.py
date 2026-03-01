"""核心异常基类定义

提供项目中使用的核心异常类型，便于统一异常处理。
"""


class CoreException(Exception):
    """核心异常基类

    有项目中所有自定义异常的基类。
    """

    def __init__(self, message: str, error_code: str | None = None):
        """初始化核心异常

        Args:
            message:异常消息
            error_code:错误码（可选）
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code

    def __str__(self) -> str:
        """返回异常的字符串表示"""
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class ConfigurationError(CoreException):
    """配置错误异常"""

    def __init__(self, message: str, error_code: str = "CONFIG_ERROR"):
        super().__init__(message, error_code)


class ValidationError(CoreException):
    """数据验证错误异常"""

    def __init__(self, message: str, error_code: str = "VALIDATION_ERROR"):
        super().__init__(message, error_code)


class DatabaseError(CoreException):
    """数据库错误异常"""

    def __init__(self, message: str, error_code: str = "DATABASE_ERROR"):
        super().__init__(message, error_code)


class InitializationError(CoreException):
    """初始化错误异常"""

    def __init__(self, message: str, error_code: str = "INIT_ERROR"):
        super().__init__(message, error_code)
