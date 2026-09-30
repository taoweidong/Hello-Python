"""分析服务测试"""

from datetime import datetime, timedelta

import pytest

from src.business.models import DataRecord
from src.business.services import AnalysisError, AnalysisService, DataProcessingService


def make_records(values: list[float]) -> list[DataRecord]:
    """构造带递增时间戳的数据记录"""
    base = datetime(2024, 1, 1, 12, 0, 0)
    return [
        DataRecord(name=f"point_{i}", value=v, category="trend", timestamp=base + timedelta(minutes=i))
        for i, v in enumerate(values)
    ]


class TestTrendAnalysis:
    """趋势分析测试"""

    def test_increasing_trend(self, in_memory_repository):
        """递增序列识别为 increasing 且相关系数接近 1"""
        service = AnalysisService(repository=in_memory_repository)
        result = service.perform_trend_analysis(make_records([10.0, 20.0, 30.0, 40.0]))

        assert result.statistics is not None
        assert result.statistics["trend_direction"] == "increasing"
        assert result.statistics["correlation"] == pytest.approx(1.0)
        assert result.analysis_type == "trend"
        # 分析结果已通过仓储保存
        assert len(in_memory_repository.analysis_results) == 1

    def test_decreasing_trend(self, in_memory_repository):
        """递减序列识别为 decreasing"""
        service = AnalysisService(repository=in_memory_repository)
        result = service.perform_trend_analysis(make_records([40.0, 30.0, 20.0, 10.0]))

        assert result.statistics["trend_direction"] == "decreasing"

    def test_empty_input_raises_analysis_error(self, in_memory_repository):
        """空数据抛出 AnalysisError 且不被二次包裹"""
        service = AnalysisService(repository=in_memory_repository)
        with pytest.raises(AnalysisError, match="数据记录为空"):
            service.perform_trend_analysis([])

    def test_single_record_raises(self, in_memory_repository):
        """单条记录无法计算趋势"""
        service = AnalysisService(repository=in_memory_repository)
        with pytest.raises(AnalysisError, match="数据记录不足"):
            service.perform_trend_analysis(make_records([1.0]))


class TestStatisticalAnalysis:
    """统计分析测试"""

    def test_statistics_and_persistence(self, in_memory_repository):
        """统计指标正确并持久化到仓储"""
        service = AnalysisService(repository=in_memory_repository)
        result = service.perform_statistical_analysis(make_records([10.0, 20.0, 30.0]))

        assert result.statistics is not None
        assert result.statistics["count"] == 3
        assert result.statistics["mean"] == pytest.approx(20.0)
        assert result.statistics["min"] == 10.0
        assert result.statistics["max"] == 30.0
        assert len(in_memory_repository.analysis_results) == 1

    def test_empty_input_raises(self, in_memory_repository):
        service = AnalysisService(repository=in_memory_repository)
        with pytest.raises(AnalysisError, match="数据记录为空"):
            service.perform_statistical_analysis([])


class TestDataProcessingService:
    """数据处理服务测试"""

    def test_unknown_processing_type_raises(self, in_memory_repository):
        service = DataProcessingService(repository=in_memory_repository)
        with pytest.raises(AnalysisError, match="不支持的处理类型"):
            service.process_data_records(make_records([1.0]), "no_such_type")

    def test_log_transform(self, in_memory_repository):
        """对数变换按 log1p 处理，0 值安全"""
        import math

        service = DataProcessingService(repository=in_memory_repository)
        processed = service.process_data_records(make_records([1.0, 0.0]), "log_transformation")

        assert processed[0].processed_value == pytest.approx(math.log1p(1.0))
        assert processed[1].processed_value == 0.0
        # 处理结果已批量入库
        assert len(in_memory_repository.processed) == 2

    def test_standardization_zero_variance(self, in_memory_repository):
        """常数序列标准化全部为 0.0（不抛除零异常）"""
        service = DataProcessingService(repository=in_memory_repository)
        processed = service.process_data_records(make_records([5.0, 5.0, 5.0]), "standardization")

        assert all(item.processed_value == 0.0 for item in processed)
