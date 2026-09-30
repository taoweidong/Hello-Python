"""核心基础设施测试（配置 / 日志 / 异常）

所有测试与仓库内 .env 文件、进程环境变量完全隔离：
配置测试在 tmp 目录中进行，日志测试验证真实文件写入。
"""

import pytest

from src.core.config import Settings, detect_environment
from src.core.config.environment import Environment, get_env_file
from src.core.exceptions import (
    ConfigurationError,
    CoreException,
    DatabaseError,
    InitializationError,
    ValidationError,
)
from src.core.logging import Logger

# Settings 会读取的字段对应的环境变量（测试需隔离，避免 .env 污染断言）
ENV_KEYS = [
    "APP_NAME",
    "APP_VERSION",
    "APP_ENV",
    "LOG_LEVEL",
    "LOG_DIR",
    "DATABASE_URL",
    "DATABASE_ECHO",
    "DEBUG",
    "DATA_INPUT_PATH",
    "DATA_OUTPUT_PATH",
    "DATA_SAMPLES_PATH",
]


@pytest.fixture
def clean_env(tmp_path, monkeypatch):
    """清空相关环境变量并切换到空目录，隔离仓库内 .env 与进程环境"""
    for key in ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture(autouse=True)
def _reset_loguru_sinks():
    """日志测试会增删全局 loguru sink，测试结束后清空避免影响其他用例"""
    yield
    from loguru import logger as loguru_logger

    loguru_logger.remove()


class TestSettings:
    """配置加载测试（真实文件 + 环境变量优先级）"""

    def test_defaults_and_auto_created_env_file(self, clean_env):
        """无任何配置文件时使用真实默认值，并自动创建 .env"""
        settings = Settings()

        assert settings.APP_NAME == "Hello-Python"
        assert settings.APP_VERSION == "1.0.0"
        assert settings.LOG_LEVEL == "INFO"
        assert settings.LOG_DIR == "logs"
        assert settings.DATABASE_URL == "sqlite:///./data/app.db"
        assert settings.DATABASE_ECHO is False
        assert settings.DEBUG is False
        assert (clean_env / ".env").exists(), "缺少配置文件时应自动创建默认 .env"

    def test_loads_values_from_env_file(self, clean_env):
        """.env 文件中的值被实际读取"""
        (clean_env / ".env").write_text("APP_NAME=FileApp\nLOG_LEVEL=DEBUG\n", encoding="utf-8")

        settings = Settings()

        assert settings.APP_NAME == "FileApp"
        assert settings.LOG_LEVEL == "DEBUG"

    def test_env_file_overrides_process_environment(self, clean_env, monkeypatch):
        """当前实现为 load_dotenv(override=True)：文件值覆盖同名进程环境变量"""
        (clean_env / ".env").write_text("APP_NAME=FromFile\n", encoding="utf-8")
        monkeypatch.setenv("APP_NAME", "FromProcessEnv")

        assert Settings().APP_NAME == "FromFile"

    def test_explicit_kwargs_win_over_env_file(self, clean_env):
        """构造参数优先于配置文件"""
        (clean_env / ".env").write_text("APP_NAME=FromFile\n", encoding="utf-8")

        assert Settings(APP_NAME="Explicit").APP_NAME == "Explicit"

    def test_production_falls_back_to_dotenv(self, clean_env, monkeypatch):
        """APP_ENV=production 缺少 .env.production 时回退到 .env"""
        monkeypatch.setenv("APP_ENV", "production")
        (clean_env / ".env").write_text("APP_NAME=FallbackApp\n", encoding="utf-8")

        assert Settings().APP_NAME == "FallbackApp"

    def test_missing_production_env_file_autocreated_with_defaults(self, clean_env, monkeypatch):
        """APP_ENV=production 且两个配置文件都不存在时，创建 .env.production 并用默认值"""
        monkeypatch.setenv("APP_ENV", "production")

        settings = Settings()

        assert (clean_env / ".env.production").exists()
        assert settings.APP_NAME == "Hello-Python"


class TestEnvironment:
    """环境检测测试"""

    def test_detect_from_env_var(self, monkeypatch):
        monkeypatch.setenv("APP_ENV", "staging")
        assert detect_environment() == Environment.STAGING

    def test_invalid_value_falls_back_to_development(self, monkeypatch):
        monkeypatch.setenv("APP_ENV", "not-a-real-env")
        assert detect_environment() == Environment.DEVELOPMENT

    def test_default_is_development(self, monkeypatch):
        monkeypatch.delenv("APP_ENV", raising=False)
        assert detect_environment() == Environment.DEVELOPMENT

    def test_env_file_mapping(self):
        assert get_env_file(Environment.DEVELOPMENT) == ".env"
        assert get_env_file(Environment.TESTING) == ".env.testing"
        assert get_env_file(Environment.STAGING) == ".env.staging"
        assert get_env_file(Environment.PRODUCTION) == ".env.production"


class TestLogger:
    """日志测试（验证真实文件输出）"""

    def make_logger(self, tmp_path) -> Logger:
        settings = Settings(APP_NAME="TestApp", LOG_DIR=str(tmp_path / "logs"))
        return Logger(settings)

    def test_setup_writes_to_log_file(self, tmp_path):
        """setup 后日志真正写入 LOG_DIR 下的文件"""
        logger = self.make_logger(tmp_path)
        logger.setup()
        logger.warning("hello-file-sink")

        log_files = list((tmp_path / "logs").glob("*.log"))
        assert len(log_files) == 1
        assert "hello-file-sink" in log_files[0].read_text(encoding="utf-8")
        assert "WARNING" in log_files[0].read_text(encoding="utf-8")

    def test_lazy_setup_on_first_log(self, tmp_path):
        """首次写日志时自动完成配置（惰性初始化契约）"""
        logger = self.make_logger(tmp_path)
        assert logger.is_configured is False

        logger.error("trigger")

        assert logger.is_configured is True

    def test_get_logger_returns_global_loguru_instance(self, tmp_path):
        from loguru import logger as loguru_logger

        logger = self.make_logger(tmp_path)
        assert logger.get_logger() is loguru_logger


class TestExceptions:
    """异常体系测试"""

    def test_inheritance_chain(self):
        """全部业务异常可被 CoreException 统一捕获"""
        for exc_class in (ConfigurationError, ValidationError, DatabaseError, InitializationError):
            assert issubclass(exc_class, CoreException)
        assert issubclass(CoreException, Exception)

    def test_str_with_error_code(self):
        assert str(CoreException("boom", "E001")) == "[E001] boom"

    def test_str_without_error_code(self):
        assert str(CoreException("boom")) == "boom"

    def test_default_error_codes(self):
        assert ConfigurationError("x").error_code == "CONFIG_ERROR"
        assert ValidationError("x").error_code == "VALIDATION_ERROR"
        assert DatabaseError("x").error_code == "DATABASE_ERROR"
        assert InitializationError("x").error_code == "INIT_ERROR"

    def test_exception_catchable_as_core_exception(self):
        """按层捕获语义：调用方用 except CoreException 即可拦截全部业务异常"""
        with pytest.raises(CoreException):
            raise DatabaseError("db down")
