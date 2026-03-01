## 1. Skill 定义：Pythonic Architect Pro (PEP)

你可以将以下 Markdown 存入你的 Prompt 库中。这个 Skill 强制 AI 以软件工程的角度思考，而非单纯的脚本编写。

```markdown
# Role: Pythonic Architect Pro (PEP)

## 🎯 核心目标
设计并编写符合现代 Python 最佳实践的工业级代码。要求代码在兼容 Python 3.10 的前提下，采用最高版本的工程化思维（如 3.11/3.12 的性能优化与类型哲学）。

## 🏗️ 软件设计约束 (SOLID & Patterns)
1. **S (单一职责)**: 每个类或函数只做一件事。数据解析、数值计算、结果导出必须解耦。
2. **O (开闭原则)**: 核心逻辑对扩展开放，对修改关闭。优先使用“策略模式”处理不同的分析算法。
3. **L (里氏替换)**: 子类必须能替换掉基类，确保继承体系的逻辑一致性。
4. **I (接口隔离)**: 优先使用 `typing.Protocol` 定义轻量级、非侵入式的接口（结构化类型）。
5. **D (依赖倒置)**: 高层模块不依赖底层实现，通过抽象（接口）注入依赖。

## 🐍 Python 3.10+ 技术栈规范
- **类型系统**: 严格使用 `|` 联合类型，禁止 `Union/Optional`。使用 `Annotated` 增强语义。
- **数据建模**: 默认使用 `@dataclass(slots=True, frozen=True)` 确保数据不可变性与内存效率。
- **模式匹配**: 核心业务分支必须使用 `match-case` 实现解构。
- **异步支持**: 针对 I/O 密集型任务（如数据加载）提供 `asyncio` 接口封装。

## 📋 输出结构
1. **System Architecture**: 简述设计模式的选择逻辑。
2. **Implementation**: OOP 风格的完整代码。
3. **Design Principles Check**: 说明代码如何满足 SOLID 原则。
4. **Maintenance Tips**: 针对未来功能扩展的预留方案。

```

---

## 2. 针对 UV 项目的实战应用

假设你需要增加一个功能：**“多源 UV 数据导入并执行不同维度的分析（如峰值提取、日剂量计算）”**。

### 🛠️ 现代化 OOP 实现

```python
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, Annotated

# --- 1. 领域模型 (Domain Model) ---

@dataclass(slots=True, frozen=True)
class UVReading:
    """不可变的采样数据点"""
    timestamp: datetime
    value: float
    unit: str = "W/m²"

# --- 2. 接口定义 (Abstractions - DIP/ISP) ---

class UvDataSource(Protocol):
    """数据源接口：支持从不同来源（CSV, API）加载数据"""
    def load_data(self) -> list[UVReading]: ...

class AnalysisStrategy(Protocol):
    """分析策略接口：支持扩展不同的分析算法 (OCP)"""
    def execute(self, data: list[UVReading]) -> dict[str, float]: ...

# --- 3. 核心业务逻辑 (Implementation - SRP) ---

class UVAnalysisEngine:
    """高层分析引擎：负责协调流程 (DIP)"""
    def __init__(self, source: UvDataSource):
        self._source = source
        self._strategies: list[AnalysisStrategy] = []

    def add_strategy(self, strategy: AnalysisStrategy) -> None:
        self._strategies.append(strategy)

    def run_full_report(self) -> dict[str, any]:
        raw_data = self._source.load_data()
        
        # 使用 Python 3.10 match-case 处理空数据状态
        match raw_data:
            case []:
                return {"status": "error", "message": "No data available"}
            case _:
                results = {type(s).__name__: s.execute(raw_data) for s in self._strategies}
                return {"status": "success", "data": results}

# --- 4. 具体策略实现 (Concrete Strategies - LSP) ---

class PeakIntensityStrategy:
    """峰值分析逻辑"""
    def execute(self, data: list[UVReading]) -> dict[str, float]:
        max_reading = max(data, key=lambda x: x.value)
        return {"peak_value": max_reading.value, "at": max_reading.timestamp}

class DailyDoseStrategy:
    """曝露量累积计算逻辑"""
    def __init__(self, integration_window_minutes: int = 15):
        self.window = integration_window_minutes

    def execute(self, data: list[UVReading]) -> dict[str, float]:
        # 简化计算：求和后乘以时间窗口
        total_dose = sum(r.value for r in data) * (self.window / 60)
        return {"total_dose": round(total_dose, 4)}

# --- 5. 使用示例 ---

if __name__ == "__main__":
    # 模拟数据源
    class MockCsvSource:
        def load_data(self) -> list[UVReading]:
            return [
                UVReading(datetime.now(), 0.25),
                UVReading(datetime.now(), 0.42)
            ]

    # 依赖注入
    engine = UVAnalysisEngine(source=MockCsvSource())
    engine.add_strategy(PeakIntensityStrategy())
    engine.add_strategy(DailyDoseStrategy(integration_window_minutes=10))

    report = engine.run_full_report()
    print(report)

```

---

## 3. 该设计的“高质量”体现

### 🪐 满足软件设计原则

* **SRP (单一职责)**: `UVReading` 只管存数据，`AnalysisStrategy` 只管算法，`UVAnalysisEngine` 只管调度。
* **OCP (开闭原则)**: 如果要新增“紫外线等级分布统计”功能，只需新建一个类实现 `AnalysisStrategy` 接口，**完全不需要修改** `UVAnalysisEngine` 的代码。
* **DIP (依赖倒置)**: 引擎依赖于 `UvDataSource` 协议，而不是具体的 `CsvLoader`。你可以随时切换到 `SqliteSource` 或 `CloudApiSource`。

### 💎 Python 3.10+ 特性应用

1. **`Protocol` (结构化类型)**: 相比 `abc.ABC`，`Protocol` 是鸭子类型的静态检查版本。它不需要显式继承，只要类里有相应方法即可，代码更干净、更解耦。
2. **`slots=True`**: 在处理数十万行 UV 采样点时，相比普通类，`UVReading` 的内存占用会下降约 **40%-60%**。
3. **`match-case`**: 在 `run_full_report` 中优雅地处理了数据为空的情况，并可根据需求扩展对错误对象的匹配。

---