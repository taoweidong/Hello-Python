"""数据处理策略

按"策略注册表"组织数值处理算法：新增处理方式时注册新函数即可，
调用方无需修改分支逻辑（开闭原则）。
"""

from __future__ import annotations

import math
from collections.abc import Callable


def normalize(values: list[float]) -> list[float]:
    """min-max 归一化到 [0, 1]；极差为 0 时全部返回 0.0"""
    if not values:
        return []
    vmin, vmax = min(values), max(values)
    span = vmax - vmin
    if span == 0:
        return [0.0 for _ in values]
    return [(v - vmin) / span for v in values]


def standardize(values: list[float]) -> list[float]:
    """z-score 标准化（基于数据自身的均值与标准差）；标准差为 0 时全部返回 0.0"""
    if not values:
        return []
    mean = sum(values) / len(values)
    variance = sum((v - mean) ** 2 for v in values) / len(values)
    std = variance**0.5
    if std == 0:
        return [0.0 for _ in values]
    return [(v - mean) / std for v in values]


def log_transform(values: list[float]) -> list[float]:
    """log1p 对数变换（兼容 0 值）；负值返回 0.0"""
    return [math.log1p(v) if v >= 0 else 0.0 for v in values]


PROCESSING_STRATEGIES: dict[str, Callable[[list[float]], list[float]]] = {
    "normalization": normalize,
    "standardization": standardize,
    "log_transformation": log_transform,
}
