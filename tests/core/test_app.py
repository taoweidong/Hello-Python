"""应用入口测试"""

from pathlib import Path

import pytest

from src.app import Application
from src.core.exceptions import ConfigurationError, InitializationError

ENV_TEMPLATE = """APP_NAME=ItApp
LOG_LEVEL=INFO
LOG_DIR={log_dir}
DATABASE_URL=sqlite:///{db_path}
"""


class TestApplicationLifecycle:
    """应用生命周期测试"""

    def test_properties_require_initialization(self):
        """未初始化时访问配置/日志应抛出 InitializationError"""
        app = Application()
        assert app.is_initialized is False
        with pytest.raises(InitializationError):
            _ = app.settings
        with pytest.raises(InitializationError):
            _ = app.logger

    def test_initialize_success(self, tmp_path: Path, monkeypatch):
        """正常初始化：配置、日志、数据库表全部就绪"""
        # 重置配置/日志/数据库全局单例，保证本测试用自己的环境
        monkeypatch.setattr("src.core.config.settings._settings", None)
        monkeypatch.setattr("src.core.logging.logger._global_logger", None)
        monkeypatch.setattr("src.core.database.manager._database_manager", None)
        env_file = tmp_path / ".env.test"
        env_file.write_text(
            ENV_TEMPLATE.format(log_dir=(tmp_path / "logs").as_posix(), db_path=(tmp_path / "app.db").as_posix()),
            encoding="utf-8",
        )

        app = Application()
        app.initialize(str(env_file))

        assert app.is_initialized is True
        assert app.settings.APP_NAME == "ItApp"
        assert app.logger is not None
        assert (tmp_path / "app.db").exists(), "启动时应自动建库"
        assert (tmp_path / "logs").is_dir()

    def test_db_failure_does_not_block_startup(self, tmp_path: Path, monkeypatch):
        """数据库初始化失败仅告警，不阻断应用启动"""
        monkeypatch.setattr("src.core.config.settings._settings", None)
        monkeypatch.setattr("src.core.logging.logger._global_logger", None)

        def broken_init(*args, **kwargs):
            raise RuntimeError("connection refused")

        monkeypatch.setattr("src.app.initialize_database", broken_init)
        env_file = tmp_path / ".env.test"
        env_file.write_text(
            ENV_TEMPLATE.format(log_dir=(tmp_path / "logs").as_posix(), db_path=(tmp_path / "app.db").as_posix()),
            encoding="utf-8",
        )

        app = Application()
        app.initialize(str(env_file))
        assert app.is_initialized is True

    def test_config_error_wrapped_as_initialization_error(self, tmp_path: Path, monkeypatch):
        """配置异常统一包装为 InitializationError 并保留异常链"""
        monkeypatch.setattr("src.core.config.settings._settings", None)

        def broken_settings(env_file=None):
            raise ConfigurationError("bad env file")

        monkeypatch.setattr("src.app.get_settings", broken_settings)

        app = Application()
        with pytest.raises(InitializationError, match="应用初始化失败"):
            app.initialize(str(tmp_path / ".env.test"))

    def test_ensure_sqlite_parent_dir(self, tmp_path: Path):
        """sqlite 父目录会被提前创建"""
        target = tmp_path / "sub" / "dir" / "app.db"
        Application._ensure_sqlite_parent_dir(f"sqlite:///{target}")
        assert target.parent.is_dir()
