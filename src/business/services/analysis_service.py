"""核心分析服务

提供数据分析和处理的核心业务逻辑。
依赖通过构造函数注入（默认使用全局工厂），便于测试时替换实现。
"""

from __future__ import annotations

import statistics
import time
from collections.abc import Callable

from ...core.exceptions import CoreException
from ...core.logging import get_logger
from ..models import AnalysisResult, DataRecord, DataValidator, ProcessedData, get_data_validator
from ..processors.strategies import PROCESSING_STRATEGIES
from ..repositories import DataRepositoryProtocol, get_data_repository


class AnalysisError(CoreException):
    """分析错误异常"""


class AnalysisService:
    """数据分析服务"""

    def __init__(
        self,
        repository: DataRepositoryProtocol | None = None,
        validator: DataValidator | None = None,
    ) -> None:
        """
        Args:
            repository:数据仓库，默认使用全局实例；测试时可注入内存实现
            validator:数据验证器，默认使用全局实例
        """
        self._logger = get_logger()
        self._repository = repository or get_data_repository()
        self._validator = validator or get_data_validator()

    def perform_statistical_analysis(self, data_records: list[DataRecord]) -> AnalysisResult:
        """执行统计分析

        Args:
            data_records:数据记录列表

        Returns:
            AnalysisResult:分析结果

        Raises:
            AnalysisError:分析失败时
        """
        if not data_records:
            self._logger.warning("统计分析收到空数据")
            raise AnalysisError("数据记录为空，无法进行分析")

        start_time = time.time()
        self._logger.info(f"开始统计分析，数据记录数: {len(data_records)}")

        try:
            # 提取数值数据
            values = [record.value for record in data_records]

            # 计算统计指标
            stats = {
                "count": len(values),
                "mean": statistics.mean(values),
                "median": statistics.median(values),
                "min": min(values),
                "max": max(values),
                "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
            }

            # 按分类统计
            category_stats: dict[str, list[float]] = {}
            for record in data_records:
                category_stats.setdefault(record.category, []).append(record.value)

            # 计算各类别统计
            category_summary = {
                category: {
                    "count": len(cat_values),
                    "mean": statistics.mean(cat_values),
                    "min": min(cat_values),
                    "max": max(cat_values),
                }
                for category, cat_values in category_stats.items()
            }

            result = AnalysisResult(
                id=f"analysis_{int(time.time())}",
                analysis_type="statistical",
                input_data_ids=[record.id for record in data_records if record.id],
                result_data={"statistics": stats, "category_summary": category_summary},
                statistics=stats,
                duration=time.time() - start_time,
            )

            # 保存分析结果
            self._repository.save_analysis_result(result)

            self._logger.info(f"统计分析完成，耗时: {result.duration:.2f}秒")
            return result

        except AnalysisError:
            raise
        except Exception as e:
            self._logger.exception("统计分析失败")
            raise AnalysisError("统计分析失败") from e

    def perform_trend_analysis(self, data_records: list[DataRecord]) -> AnalysisResult:
        """执行趋势分析

        Args:
            data_records:数据记录列表（需要按时间排序）

        Returns:
            AnalysisResult:分析结果

        Raises:
            AnalysisError:分析失败时
        """
        if not data_records:
            self._logger.warning("趋势分析收到空数据")
            raise AnalysisError("数据记录为空，无法进行分析")

        if len(data_records) < 2:
            raise AnalysisError("数据记录不足，无法进行趋势分析")

        start_time = time.time()
        self._logger.info(f"开始趋势分析，数据记录数: {len(data_records)}")

        try:
            # 按时间排序
            sorted_records = sorted(data_records, key=lambda x: x.timestamp)

            # 计算趋势指标
            values = [record.value for record in sorted_records]
            timestamps = [record.timestamp.timestamp() for record in sorted_records]

            # 简单线性回归计算趋势
            n = len(values)
            sum_x = sum(timestamps)
            sum_y = sum(values)
            sum_xy = sum(x * y for x, y in zip(timestamps, values))
            sum_xx = sum(x * x for x in timestamps)

            # 计算斜率和截距
            denominator_xx = n * sum_xx - sum_x * sum_x
            slope = (n * sum_xy - sum_x * sum_y) / denominator_xx if denominator_xx != 0 else 0
            intercept = (sum_y - slope * sum_x) / n

            # 计算相关系数
            mean_x = sum_x / n
            mean_y = sum_y / n
            numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(timestamps, values))
            denominator_x = sum((x - mean_x) ** 2 for x in timestamps)
            denominator_y = sum((y - mean_y) ** 2 for y in values)

            correlation = (
                numerator / (denominator_x * denominator_y) ** 0.5 if denominator_x * denominator_y != 0 else 0
            )

            trend_result = {
                "slope": slope,
                "intercept": intercept,
                "correlation": correlation,
                "trend_direction": "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable",
                "trend_strength": abs(correlation),
            }

            result = AnalysisResult(
                id=f"trend_{int(time.time())}",
                analysis_type="trend",
                input_data_ids=[record.id for record in data_records if record.id],
                result_data={"trend_analysis": trend_result, "data_points": n},
                statistics=trend_result,
                duration=time.time() - start_time,
            )

            # 保存分析结果
            self._repository.save_analysis_result(result)

            self._logger.info(f"趋势分析完成，趋势方向: {trend_result['trend_direction']}")
            return result

        except AnalysisError:
            raise
        except Exception as e:
            self._logger.exception("趋势分析失败")
            raise AnalysisError("趋势分析失败") from e


class DataProcessingService:
    """数据处理服务"""

    def __init__(
        self,
        repository: DataRepositoryProtocol | None = None,
        validator: DataValidator | None = None,
    ) -> None:
        """
        Args:
            repository:数据仓库，默认使用全局实例；测试时可注入内存实现
            validator:数据验证器，默认使用全局实例
        """
        self._logger = get_logger()
        self._repository = repository or get_data_repository()
        self._validator = validator or get_data_validator()

    def process_data_records(
        self, data_records: list[DataRecord], processing_type: str = "normalization"
    ) -> list[ProcessedData]:
        """处理数据记录

        Args:
            data_records:原始数据记录列表
            processing_type:处理类型，见 strategies.PROCESSING_STRATEGIES

        Returns:
            List[ProcessedData]:处理后的数据列表

        Raises:
            AnalysisError:处理失败或处理类型不支持时
        """
        strategy: Callable[[list[float]], list[float]] | None = PROCESSING_STRATEGIES.get(processing_type)
        if strategy is None:
            raise AnalysisError(f"不支持的处理类型: {processing_type}，可选: {', '.join(PROCESSING_STRATEGIES)}")

        self._logger.info(f"开始数据处理，记录数: {len(data_records)}, 处理类型: {processing_type}")

        try:
            # 逐条验证，无效记录跳过并告警
            valid_records: list[DataRecord] = []
            for record in data_records:
                validation_result = self._validator.validate_data_record(record.model_dump())
                if not validation_result:
                    self._logger.warning(f"数据验证失败，已跳过: {', '.join(validation_result.errors)}")
                    continue
                valid_records.append(record)

            processed_values = strategy([record.value for record in valid_records])

            processed_data_list = [
                ProcessedData(
                    id=f"processed_{record.id or int(time.time())}",
                    original_id=record.id or str(int(time.time())),
                    name=record.name,
                    original_value=record.value,
                    processed_value=processed_value,
                    category=record.category,
                    processing_type=processing_type,
                    metadata={"processing_method": processing_type, "original_status": record.status.value},
                )
                for record, processed_value in zip(valid_records, processed_values)
            ]

            # 批量保存处理后的数据
            self._repository.save_processed_data_batch(processed_data_list)

            self._logger.info(f"数据处理完成，成功处理 {len(processed_data_list)} 条")
            return processed_data_list

        except AnalysisError:
            raise
        except Exception as e:
            self._logger.exception("数据处理失败")
            raise AnalysisError("数据处理失败") from e


# 全局服务实例
_analysis_service: AnalysisService | None = None
_data_processing_service: DataProcessingService | None = None


def get_analysis_service() -> AnalysisService:
    """获取全局分析服务实例

    Returns:
        AnalysisService:分析服务实例
    """
    global _analysis_service
    if _analysis_service is None:
        _analysis_service = AnalysisService()
    return _analysis_service


def get_data_processing_service() -> DataProcessingService:
    """获取全局数据处理服务实例

    Returns:
        DataProcessingService:数据处理服务实例
    """
    global _data_processing_service
    if _data_processing_service is None:
        _data_processing_service = DataProcessingService()
    return _data_processing_service
