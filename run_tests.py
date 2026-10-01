"""一键质量门禁入口

每次代码变更后、每次 AI 会话结束前必须运行并通过（规则见 AGENTS.md）：

    uv run python run_tests.py              # 完整门禁：lint + 格式 + 类型 + 单元测试
    uv run python run_tests.py --tests-only # 仅单元测试（含覆盖率门禁 80%）

任一步骤失败则整体退出码为 1。
"""

from __future__ import annotations

import argparse
import subprocess
import sys

COV_GATE = "80"

TEST_CMD = [
    sys.executable,
    "-m",
    "pytest",
    "tests/",
    "-q",
    "--cov=src",
    "--cov-report=term-missing",
    f"--cov-fail-under={COV_GATE}",
]

FULL_STEPS: list[tuple[str, list[str]]] = [
    ("ruff lint", [sys.executable, "-m", "ruff", "check", "."]),
    ("ruff format", [sys.executable, "-m", "ruff", "format", "--check", "."]),
    ("mypy 类型检查", [sys.executable, "-m", "mypy", "src"]),
    (f"单元测试（覆盖率门禁 {COV_GATE}%）", TEST_CMD),
]

TESTS_ONLY_STEPS: list[tuple[str, list[str]]] = [
    (f"单元测试（覆盖率门禁 {COV_GATE}%）", TEST_CMD),
]


def main() -> int:
    parser = argparse.ArgumentParser(description="一键质量门禁：单元测试 + 静态检查")
    parser.add_argument("--tests-only", action="store_true", help="仅运行单元测试，跳过 lint/格式/类型检查")
    args = parser.parse_args()

    steps = TESTS_ONLY_STEPS if args.tests_only else FULL_STEPS
    failed: list[str] = []

    for index, (name, cmd) in enumerate(steps, start=1):
        print(f"\n===== [{index}/{len(steps)}] {name} =====", flush=True)
        result = subprocess.run(cmd)
        if result.returncode != 0:
            failed.append(name)

    print("\n===== 门禁结果 =====", flush=True)
    if failed:
        print(f"❌ 未通过：{', '.join(failed)}")
        return 1
    print(f"✅ 全部通过（{len(steps)} 项）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
