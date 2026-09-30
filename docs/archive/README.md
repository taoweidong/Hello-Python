# 文档归档说明

本目录存放**历史过程文档与已失效的方案文档**，仅作参考，内容与当前代码结构可能不一致：

| 文档 | 归档原因 |
|------|----------|
| infrastructure_database_module.md | 独立 infrastructure 数据库模块已并入 `src/core/database`（2026-09 架构归一） |
| db_module_standalone_usage.md | 同上，描述的旧 `db` 包/独立模块已不存在 |
| auto_database_initialization.md | 描述的 `initialize_databases`/`example_models` API 已移除，建表现在由 `src/app.py` 统一完成 |
| multi_database_support.md | API 已变更，多数据库用法见 `examples/db_usage_example.py` |
| refactoring_summary.md | 2025 年过程性重构记录 |
| test_fix_summary.md | 过程性测试修复记录 |
| Elasticsearch (ES)分布式日志存储方案.md | 设计提案，未落地实施 |
| Pythonic Architect Pro (PEP).md | 编码规范参考，已由项目实际 lint/mypy 配置取代 |

当前有效文档见 [../README.md](../README.md) 的文档索引。
