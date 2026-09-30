"""接口层测试

测试命令行接口和其他用户接口功能。
"""

from unittest.mock import Mock, patch

from click.testing import CliRunner

from src.interfaces.cli.commands import create_cli


class TestCLIInterface:
    """命令行接口测试"""

    def setup_method(self):
        """测试方法设置"""
        self.runner = CliRunner()
        self.cli = create_cli()

    def test_cli_help(self):
        """测试CLI帮助命令"""
        result = self.runner.invoke(self.cli, ["--help"])
        assert result.exit_code == 0
        assert "数据分析项目命令行接口" in result.output

    def test_status_command(self):
        """测试状态命令（数据库URL应脱敏输出）"""
        with patch("src.interfaces.cli.commands.initialize_app") as mock_init:
            mock_app = Mock()
            mock_app.settings.APP_NAME = "TestApp"
            mock_app.settings.APP_VERSION = "1.0.0"
            mock_app.settings.APP_ENV.value = "development"
            mock_app.settings.LOG_LEVEL = "INFO"
            mock_app.settings.DATABASE_URL = "postgresql://admin:secret@localhost:5432/db"
            mock_app.logger = Mock()
            mock_init.return_value = mock_app

            result = self.runner.invoke(self.cli, ["status"])
            assert result.exit_code == 0
            assert "secret" not in result.output
            assert "admin:***@localhost:5432/db" in result.output

    def test_process_csv_command_validation(self):
        """测试CSV处理命令参数验证"""
        result = self.runner.invoke(self.cli, ["process-csv"])
        assert result.exit_code != 0  # 应该失败，因为缺少必需参数

    def test_analyze_data_statistical(self, monkeypatch, tmp_path):
        """analyze-data 统计分析命令端到端（注入独立内存库）"""
        import src.business.models.tables  # noqa: F401
        from src.business.repositories import DataRepository
        from src.business.services import AnalysisService
        from src.core.database import DatabaseManager
        from src.core.database.base import Base

        csv_file = tmp_path / "data.csv"
        csv_file.write_text("name,value,category\na,1.0,sales\nb,3.0,sales\n", encoding="utf-8")

        manager = DatabaseManager(f"sqlite:///{tmp_path / 'cli.db'}")
        Base.metadata.create_all(bind=manager.get_engine())
        repository = DataRepository(db_manager=manager)

        monkeypatch.setattr("src.interfaces.cli.commands.initialize_app", lambda env_file=None: Mock())
        monkeypatch.setattr("src.interfaces.cli.commands.get_data_repository", lambda: repository)
        monkeypatch.setattr(
            "src.interfaces.cli.commands.get_analysis_service", lambda: AnalysisService(repository=repository)
        )

        result = self.runner.invoke(self.cli, ["analyze-data", "--input-file", str(csv_file)])
        assert result.exit_code == 0
        assert "统计分析完成" in result.output
        assert "平均值" in result.output

    def test_analyze_data_trend(self, monkeypatch, tmp_path):
        """analyze-data 趋势分析命令输出"""
        from datetime import datetime

        import src.business.models.tables  # noqa: F401
        from src.business.models import DataRecord
        from src.business.repositories import DataRepository
        from src.business.services import AnalysisService
        from src.core.database import DatabaseManager
        from src.core.database.base import Base

        manager = DatabaseManager(f"sqlite:///{tmp_path / 'cli.db'}")
        Base.metadata.create_all(bind=manager.get_engine())
        repository = DataRepository(db_manager=manager)
        records = [
            DataRecord(name="a", value=float(i), category="t", timestamp=datetime(2024, 1, i + 1)) for i in range(3)
        ]
        repository.save_data_records(records)
        # analyze-data 从 CSV 读取，这里通过临时 CSV 提供
        csv_file = tmp_path / "trend.csv"
        csv_file.write_text("name,value,category\na,1.0,t\nb,2.0,t\nc,3.0,t\n", encoding="utf-8")

        monkeypatch.setattr("src.interfaces.cli.commands.initialize_app", lambda env_file=None: Mock())
        monkeypatch.setattr("src.interfaces.cli.commands.get_data_repository", lambda: repository)
        monkeypatch.setattr(
            "src.interfaces.cli.commands.get_analysis_service", lambda: AnalysisService(repository=repository)
        )

        result = self.runner.invoke(
            self.cli, ["analyze-data", "--input-file", str(csv_file), "--analysis-type", "trend"]
        )
        assert result.exit_code == 0
        assert "趋势分析完成" in result.output
        assert "趋势方向" in result.output

    def test_reset_command(self, monkeypatch):
        """reset 命令调用处理器计数器重置"""
        mock_processor = Mock()
        monkeypatch.setattr("src.interfaces.cli.commands.initialize_app", lambda env_file=None: Mock())
        monkeypatch.setattr("src.interfaces.cli.commands.get_data_processor", lambda: mock_processor)

        result = self.runner.invoke(self.cli, ["reset"])
        assert result.exit_code == 0
        assert "计数器已重置" in result.output
        mock_processor.reset_counters.assert_called_once()
