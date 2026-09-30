"""数据处理策略测试"""

import math

import pytest

from src.business.processors.strategies import PROCESSING_STRATEGIES, log_transform, normalize, standardize


class TestNormalize:
    """min-max 归一化测试"""

    def test_basic(self):
        assert normalize([0.0, 5.0, 10.0]) == [0.0, 0.5, 1.0]

    def test_empty(self):
        assert normalize([]) == []

    def test_zero_span(self):
        """极差为 0 时全部返回 0.0，不抛除零异常"""
        assert normalize([7.0, 7.0, 7.0]) == [0.0, 0.0, 0.0]


class TestStandardize:
    """z-score 标准化测试"""

    def test_basic(self):
        result = standardize([10.0, 20.0, 30.0])
        assert sum(result) / len(result) == pytest.approx(0.0)
        assert result[2] == pytest.approx(10.0 / ((200.0 / 3) ** 0.5))

    def test_empty(self):
        assert standardize([]) == []

    def test_zero_std(self):
        assert standardize([3.0, 3.0]) == [0.0, 0.0]


class TestLogTransform:
    """对数变换测试"""

    def test_basic(self):
        assert log_transform([0.0, 1.0]) == [0.0, math.log1p(1.0)]

    def test_negative_clamped(self):
        assert log_transform([-1.0]) == [0.0]

    def test_registry_contains_strategies(self):
        """注册表包含全部预置策略"""
        assert set(PROCESSING_STRATEGIES) == {"normalization", "standardization", "log_transformation"}
