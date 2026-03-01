"""数据处理器实现

提供数据处理的核心逻辑和管道功能。
"""

import time
from collections.abc import Callable
from datetime import datetime
from typing import Any

from ...core.exceptions import CoreException
from ...core.logging import get_logger
from ..models import DataRecord, ProcessedData, get_data_validator
from ..repositories import get_data_repository


class ProcessingError(CoreException):
    """数据处理错误异常"""

    pass


class DataProcessor:
    """数据处理器"""

    def __init__(self) -> None:
        self._logger = get_logger()
        self._repository = get_data_repository()
        self._validator = get_data_validator()
        self._processed_count = 0

    def load_and_process_csv(
        self, file_path: str, processing_steps: list[Callable[..., Any]] | None = None
    ) -> list[ProcessedData]:
        """加载CSV文件并处理数据

        Args:
            file_path:CSV文件路径
            processing_steps:处理步骤列表

        Returns:
            List[ProcessedData]:处理后的数据列表

        Raises:
            ProcessingError:处理失败时
        """
        try:
            start_time = time.time()
            self._logger.info(f"开始处理CSV文件: {file_path}")

            # 加载数据
            data_records = self._repository.load_data_from_csv(file_path)

            if not data_records:
                self._logger.warning("未加载到任何数据记录")
                return []

            # 应用处理步骤
            if processing_steps:
                for step in processing_steps:
                    data_records = step(data_records)

            # 默认处理步骤
            processed_data = self._apply_default_processing(data_records)

            self._processed_count += len(processed_data)
            duration = time.time() - start_time

            self._logger.info(f"CSV文件处理完成，共处理 {len(processed_data)}条记录，耗时: {duration:.2f}秒")
            return processed_data

        except Exception as e:
            self._logger.error(f"CSV文件处理失败: {e}")
            raise ProcessingError(f"CSV文件处理失败: {e}")

    def _apply_default_processing(self, data_records: list[DataRecord]) -> list[ProcessedData]:
        """应用默认处理步骤

        Args:
            data_records:数据记录列表

        Returns:
            List[ProcessedData]:处理后的数据列表
        """
        processed_data: list[ProcessedData] = []

        for record in data_records:
            # 验证数据
            validation_result = self._validator.validate_data_record(record.model_dump())
            if not validation_result:
                self._logger.warning(f"数据验证失败: {', '.join(validation_result.errors)}")
                continue

            # 简单处理：数值标准化
            processed_value = record.value / 100.0 if record.value != 0 else 0

            # 创建处理后的数据
            processed_record = ProcessedData(
                id=f"processed_{int(time.time() * 1000000)}_{len(processed_data)}",
                original_id=record.id or str(int(time.time())),
                name=record.name,
                original_value=record.value,
                processed_value=processed_value,
                category=record.category,
                processing_type="normalization",
                metadata={
                    "processing_method": "normalization",
                    "original_status": record.status.value,
                    "processing_time": datetime.now().isoformat(),
                },
            )

            processed_data.append(processed_record)

        return processed_data

    @property
    def processed_count(self) -> int:
        """获取已处理的记录数"""
        return self._processed_count

    def reset_counters(self) -> None:
        """重置计数器"""
        self._processed_count = 0
        self._logger.info("计数器已重置")


class DataProcessingPipeline:
    """数据处理管道"""

    def __init__(self) -> None:
        self._logger = get_logger()
        self._steps: list[Callable[..., Any]] = []

    def add_step(self, step: Callable[..., Any]) -> "DataProcessingPipeline":
        """添加处理步骤

        Args:
            step:处理函数

        Returns:
            DataProcessingPipeline:当前实例（支持链式调用）
        """
        self._steps.append(step)
        self._logger.debug(f"添加处理步骤，当前步骤数: {len(self._steps)}")
        return self

    def process(self, data_records: list[DataRecord]) -> list[DataRecord]:
        """执行处理管道

        Args:
            data_records:输入数据记录列表

        Returns:
            List[DataRecord]:处理后的数据记录列表
        """
        if not self._steps:
            self._logger.warning("处理管道为空，返回原始数据")
            return data_records

        self._logger.info(f"开始执行处理管道，步骤数: {len(self._steps)}")

        result = data_records
        for i, step in enumerate(self._steps):
            try:
                self._logger.debug(f"执行处理步骤 {i + 1}")
                result = step(result)
            except Exception as e:
                self._logger.error(f"处理步骤 {i + 1}执行失败: {e}")
                raise ProcessingError(f"处理步骤 {i + 1}执行失败: {e}")

        self._logger.info(f"处理管道执行完成，输出记录数: {len(result)}")
        return result

    def clear(self) -> None:
        """清空处理步骤"""
        self._steps.clear()
        self._logger.debug("处理管道已清空")


# 全局实例
_data_processor: DataProcessor | None = None
_processing_pipeline: DataProcessingPipeline | None = None


def get_data_processor() -> DataProcessor:
    """获取全局数据处理器实例

    Returns:
        DataProcessor:数据处理器实例
    """
    global _data_processor
    if _data_processor is None:
        _data_processor = DataProcessor()
    return _data_processor


def get_processing_pipeline() -> DataProcessingPipeline:
    """获取全局处理管道实例

    Returns:
        DataProcessingPipeline:处理管道实例
    """
    global _processing_pipeline
    if _processing_pipeline is None:
        _processing_pipeline = DataProcessingPipeline()
    return _processing_pipeline
