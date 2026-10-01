"""接口层端到端测试（零 mock）

CLI 测试走真实应用启动链路：真实 .env 加载 → 真实日志 → 真实 sqlite 落库。
monkeypatch 仅用于全局单例隔离（保证测试间互不污染），不替换任何被测逻辑。
"""

import sqlite3
from pathlib import Path
from types import SimpleNamespace

import pytest
from click.testing import CliRunner

import src.business.models.tables  # noqa: F401  确保业务表注册到 Base.metadata
from src.interfaces.cli.commands import create_cli

ANALYSIS_CSV = (
    "name,value,category\n"
    "alpha,10.0,sales\n"
    "beta,30.0,sales\n"
    "gamma,20.0,marketing\n"
    "delta,50.0,marketing\n"
    "echo,40.0,sales\n"
)


def _reset_singletons(monkeypatch) -> None:
    """重置全局单例，让每次 CLI 调用完成真实且隔离的应用启动"""
    monkeypatch.setattr("src.app._app", None)
    monkeypatch.setattr("src.core.config.settings._settings", None)
    monkeypatch.setattr("src.core.logging.logger._global_logger", None)
    monkeypatch.setattr("src.core.database.manager._database_manager", None)
    monkeypatch.setattr("src.business.repositories.data_repository._data_repository", None)
    monkeypatch.setattr("src.business.processors.data_processor._data_processor", None)
    monkeypatch.setattr("src.business.processors.data_processor._processing_pipeline", None)
    monkeypatch.setattr("src.business.services.analysis_service._analysis_service", None)
    monkeypatch.setattr("src.business.services.analysis_service._data_processing_service", None)


def write_env_file(tmp_path: Path, database_url: str) -> Path:
    """写入真实的 .env 配置文件"""
    env_file = tmp_path / ".env.test"
    env_file.write_text(
        f"APP_NAME=CliApp\nLOG_LEVEL=INFO\nLOG_DIR={(tmp_path / 'logs').as_posix()}\nDATABASE_URL={database_url}\n",
        encoding="utf-8",
    )
    return env_file


@pytest.fixture
def cli(tmp_path, monkeypatch):
    """真实 CLI 环境：独立 .env + 独立 sqlite，零 mock"""
    _reset_singletons(monkeypatch)
    env_file = write_env_file(tmp_path, f"sqlite:///{(tmp_path / 'cli.db').as_posix()}")
    return SimpleNamespace(
        runner=CliRunner(),
        cli=create_cli(),
        tmp_path=tmp_path,
        env_file=env_file,
        db_path=tmp_path / "cli.db",
    )


def invoke(harness, *args: str):
    """带 --env-file 的真实调用（应用由 CLI 自行启动）"""
    return harness.runner.invoke(harness.cli, ["--env-file", str(harness.env_file), *args])


def count_rows(db_path: Path, table: str) -> int:
    """直接查询真实落库的 sqlite 文件，验证持久化结果"""
    with sqlite3.connect(db_path) as conn:
        return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


class TestCliHelp:
    def test_cli_help(self, cli):
        """帮助信息可用且列出全部命令"""
        result = cli.runner.invoke(cli.cli, ["--help"])
        assert result.exit_code == 0
        assert "数据分析项目命令行接口" in result.output
        for command in ("process-csv", "analyze-data", "status", "reset"):
            assert command in result.output


class TestProcessCsvCommand:
    def test_missing_required_option_fails(self, cli):
        """缺少必填参数时被 click 拒绝"""
        result = cli.runner.invoke(cli.cli, ["process-csv"])
        assert result.exit_code != 0

    def test_process_csv_increments_real_counter(self, cli, tmp_path):
        """处理真实 CSV 后，处理器计数真实增加并可被 status 观测"""
        csv_file = tmp_path / "data.csv"
        csv_file.write_text(ANALYSIS_CSV, encoding="utf-8")

        result = invoke(cli, "process-csv", "--input-file", str(csv_file))
        assert result.exit_code == 0
        assert "共处理 5" in result.output

        status = invoke(cli, "status")
        assert status.exit_code == 0
        assert "已处理记录数: 5" in status.output

    def test_reset_clears_real_counter(self, cli, tmp_path):
        """reset 真实清零计数器（先处理产生计数，再重置并观测）"""
        csv_file = tmp_path / "data.csv"
        csv_file.write_text(ANALYSIS_CSV, encoding="utf-8")
        assert invoke(cli, "process-csv", "--input-file", str(csv_file)).exit_code == 0

        result = invoke(cli, "reset")
        assert result.exit_code == 0
        assert "计数器已重置" in result.output

        status = invoke(cli, "status")
        assert "已处理记录数: 0" in status.output


class TestStatusCommand:
    def test_status_shows_real_app_info(self, cli):
        """status 输出来自真实加载的配置"""
        result = invoke(cli, "status")
        assert result.exit_code == 0
        assert "应用名称: CliApp" in result.output
        assert "sqlite" in result.output

    def test_status_masks_db_credentials_and_survives_db_failure(self, tmp_path, monkeypatch):
        """数据库不可达（带密码的真实连接失败）时应用仍完成启动，且 URL 脱敏输出"""
        _reset_singletons(monkeypatch)
        env_file = write_env_file(tmp_path, "postgresql://admin:secret@127.0.0.1:1/unreachable")

        harness = SimpleNamespace(runner=CliRunner(), cli=create_cli())
        result = harness.runner.invoke(harness.cli, ["--env-file", str(env_file), "status"])

        assert result.exit_code == 0
        assert "admin:***@127.0.0.1:1/unreachable" in result.output
        assert "secret" not in result.output


class TestAnalyzeDataCommand:
    def test_statistical_analysis_persists_result(self, cli, tmp_path):
        """统计分析执行后结果真实落库（直接查询 sqlite 文件验证）"""
        csv_file = tmp_path / "data.csv"
        csv_file.write_text(ANALYSIS_CSV, encoding="utf-8")

        result = invoke(cli, "analyze-data", "--input-file", str(csv_file))

        assert result.exit_code == 0
        assert "统计分析完成" in result.output
        assert "平均值: 30.00" in result.output
        assert count_rows(cli.db_path, "analysis_results") == 1

    def test_trend_analysis_persists_result(self, cli, tmp_path):
        """趋势分析执行后结果真实落库"""
        csv_file = tmp_path / "trend.csv"
        csv_file.write_text("name,value,category\na,1.0,t\nb,2.0,t\nc,3.0,t\n", encoding="utf-8")

        result = invoke(cli, "analyze-data", "--input-file", str(csv_file), "--analysis-type", "trend")

        assert result.exit_code == 0
        assert "趋势分析完成" in result.output
        assert "趋势方向" in result.output
        assert count_rows(cli.db_path, "analysis_results") == 1

    def test_analyze_missing_file_fails(self, cli):
        """加载不存在的文件时命令失败并给出错误信息"""
        result = invoke(cli, "analyze-data", "--input-file", "no_such_file.csv")
        assert result.exit_code != 0
