# 项目优化记录（2026-09-30）

依据 [项目质量报告](project_quality_report.md) 的 P0~P3 路线逐步执行，目标：作为数据分析基础项目支撑快速二次开发。

## 总体效果

| 指标 | 优化前 | 优化后 |
|------|--------|--------|
| 测试 | 141 个通过，但 1/3 测的是已废弃的旧架构 | **107 个全部通过**，全部针对当前架构 |
| 测试覆盖率 | 57%（含 0% 的死代码） | **84%**，CI 门禁 ≥80% |
| mypy | 配置禁用 6 类错误码、不查未注解函数，"全绿"无意义 | **`disallow_untyped_defs=true` + Pydantic 插件，真实全绿** |
| 运行时缺陷 | core 事务装饰器完全无法工作（无测试暴露） | 已修复并补齐边界测试 |
| 架构 | 新旧两套并存（config/services/models/core vs infrastructure 重复实现） | **单一架构**：core / business / interfaces / app |
| 仓储层 | 空壳（`try: pass`），分析结果不落任何存储 | **真实 SQLAlchemy 持久化**，含 ORM 表模型与双向转换 |
| 依赖 | 混乱（pyinstaller 在运行时依赖） | 全部升级至最新稳定版并归位（uv.lock 锁定） |
| CI | 无 | GitHub Actions：ruff + mypy + pytest（覆盖率门禁） |

## 主要变更

### P0 正确性与卫生
- **仓库卫生**：`.env.development/.production/.staging`、`.coverage` 解除 git 跟踪；`.gitignore` 增加 `.env.*`（保留 `.env.example`）；build 脚本与 `build/` 忽略规则的冲突已消除
- **core 事务装饰器运行时 bug 修复**：旧代码对 `@contextmanager` 返回值调用 `next()` 必然抛 `TypeError`，因 core 版几乎无测试（17%）而从未暴露；改为直接管理 Session 生命周期
- **异常链修复**：全部 `raise XxxError(...) from e`；消除"自捕获再二次包裹"；`raise e` → 裸 `raise`；静默吞错处（连接测试失败）补日志
- **数据库错误判断**：删除错误消息字符串关键词匹配，改为捕获 `OperationalError`/`InterfaceError`（`RETRYABLE_DB_ERRORS`）
- **文案**：修复乱码/脱字（"平值"→"平均值"、"趋方向"→"趋势方向"、"试重试"等）；删除死代码与 4 处 `sys.path` hack

### P1 架构与可维护性
- **架构归一**：删除旧层 `src/config`、`src/services`、`src/models`、`src/main.py`、`src/db_example.py`、`src/click_demo.py` 与重复的 `src/infrastructure/database`；`db_example` 等演示代码移出 src
- **依赖注入**：服务/处理器通过构造函数注入依赖（默认工厂兜底）；新增 `DataRepositoryProtocol` 接口，仓储可整体替换
- **真实持久化**：`business/models/tables.py` 定义业务表（`Mapped[]` 类型化 ORM），仓储实现 加载→入库→处理→分析→回读 完整链路；应用启动自动建表
- **类型系统**：补齐全部函数注解；全仓库启用 `from __future__ import annotations`；CRUDMixin 泛型化；装饰器用 `ParamSpec`/`Concatenate` 保留签名
- **CI**：`.github/workflows/ci.yml`，Python 3.10/3.12 双矩阵，四道门禁

### P2 体验与性能
- 配置归一：ruff/pytest 配置统一进 `pyproject.toml`（删除 `.ruff.toml`、`pytest.ini`）
- 依赖归类：pyinstaller 移入 develop 组；删除重复/损坏的脚本入口（`analysis-tool`、指向不存在函数的 `build-dist`）
- CSV 加载：`iterrows()` → `to_dict("records")` + **NaN 显式拒绝**（NaN 可绕过常规比较的缺陷已封堵）；无效行跳过并告警而非整体失败
- 处理算法：if/elif 魔法数字分支 → 策略注册表（归一化/标准化使用数据自身统计量，语义正确）
- 安全：新增 `mask_database_url`，`status` 命令与 `get_database_info` 输出脱敏；`LOG_DIR` 可配置

### 文档
- 重写 README、使用入门（原文件乱码）、开发指南、tests 说明
- 过程性/已失效文档移入 `docs/archive/` 并说明归档原因

## 验证

```text
ruff check .            All checks passed
ruff format --check .   all formatted
mypy src                Success: no issues found in 32 source files
pytest tests/           107 passed, coverage 84%
```

## 测试真实性治理（同日第二轮）

用 AST 扫描对全部测试做"无效测试"甄别（无断言 / 仅 `is not None`、`hasattr` 等永真断言 / 断言内容来自自身输入 / 依赖仓库内 .env 内容的假测试），随后重写：

| 文件 | 问题 | 处理 |
|------|------|------|
| test_business_logic.py | 5 个纯创建测试（`assert X is not None`，类内部全坏也能过）；2 个与 test_entities.py 重复 | 重写为工厂单例契约、DI 默认装配、仓储真实读写边界测试 |
| test_core_modules.py | "默认值"测试实际断言的是仓库内 `.env` 文件内容（文件一改测试即变）；Logger 测试只翻转内存标志 | 重写为 tmp 目录隔离的配置加载/优先级/自动建文件测试、真实文件写入的日志测试 |
| test_database.py | 个别弱断言；fixture 误用 test_ 前缀命名 | 引擎/会话工厂改为类型与同一性断言；fixture 更名 |
| test_data_processor.py | 管道测试断言私有属性 | 改为真实多步骤变换的顺序与结果验证 |

新测试立即揪出 3 个真实代码缺陷并修复：
1. `processed_data_to_table` 丢弃调用方传入的 `id`（落库后静默变成新 UUID，破坏 ID 引用）
2. `Settings._create_default_env_file` 模板残留旧 `sql/app.db` 路径，与字段默认值不一致
3. production 模式缺配置文件时，自动创建的是 `.env` 而非 `.env.production`，下次启动仍读不到

最终：**123 个测试全部通过，覆盖率 86.03%**（门禁 80%），ruff/mypy 全绿；AST 复扫无"无真实断言"用例。
