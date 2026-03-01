"""服务模块

提供应用程序的核心业务服务。
"""

from .data_service import DataProcessingError, DataProcessor, get_data_processor

__all__ = ["DataProcessor", "DataProcessingError", "get_data_processor"]
