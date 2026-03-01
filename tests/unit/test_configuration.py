"""配置模块测试"""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from src.config.configuration import (
    ConfigurationError,
    ConfigurationManager,
    EnvironmentConfig,
    get_config_manager,
)
from src.config.logging import LoggerError, LoggerManager, get_logger_manager, setup_logger


class TestConfigurationManager:
    """配置管理器测试"""

    def test_init_with_custom_env_file(self):
        """测试使用自定义环境文件初始化"""
        manager = ConfigurationManager(".env.test")
        assert manager._env_file == ".env.test"

    def test_detect_env_file_development(self):
        """测试检测开发环境配置文件"""
        with patch.dict(os.environ, {"APP_ENV": "development"}):
            manager = ConfigurationManager()
            env_file = manager._detect_env_file()
            assert env_file == ".env"

    def test_detect_env_file_production(self):
        """测试检测生产环境配置文件"""
        with patch.dict(os.environ, {"APP_ENV": "production"}):
            manager = ConfigurationManager()
            env_file = manager._detect_env_file()
            assert env_file == ".env.production"

    def test_detect_env_file_missing(self, tmp_path):
        """测试检测不存在的配置文件"""
        # 创建临时目录并切换到该目录
        original_cwd = Path.cwd()
        os.chdir(tmp_path)

        try:
            with patch.dict(os.environ, {"APP_ENV": "staging"}):
                manager = ConfigurationManager()
                with pytest.raises(ConfigurationError, match="配置文件不存在"):
                    manager._detect_env_file()
        finally:
            os.chdir(original_cwd)

    def test_load_configuration_success(self, tmp_path):
        """测试成功加载配置"""
        # 创建临时.env文件
        env_content = """APP_NAME=TestApp
LOG_LEVEL=DEBUG
DATA_FILE_PATH=test/data.csv
DATABASE_URL=sqlite:///./sql/test.db
APP_ENV=test"""

        env_file = tmp_path / ".env"
        env_file.write_text(env_content)

        # 切换到临时目录
        original_cwd = Path.cwd()
        os.chdir(tmp_path)

        try:
            # 清除环境变量影响
            with patch.dict(os.environ, {"APP_ENV": "test"}, clear=True):
                manager = ConfigurationManager()
                config = manager.load_configuration()

                assert isinstance(config, EnvironmentConfig)
                assert config.APP_NAME == "TestApp"
                assert config.LOG_LEVEL == "DEBUG"
                assert config.DATA_FILE_PATH == "test/data.csv"
                assert config.DATABASE_URL == "sqlite:///./sql/test.db"
                assert config.APP_ENV == "test"
        finally:
            os.chdir(original_cwd)

    def test_load_configuration_validation_error(self, tmp_path):
        """测试配置验证错误"""
        # 创建包含无效日志级别的配置文件
        env_content = "APP_NAME=TestApp\nLOG_LEVEL=INVALID_LEVEL\nAPP_ENV=development"

        env_file = tmp_path / ".env"
        env_file.write_text(env_content)

        original_cwd = Path.cwd()
        os.chdir(tmp_path)

        try:
            # 清除环境变量影响
            with patch.dict(os.environ, {}, clear=True):
                manager = ConfigurationManager()
                # 应该会抛出验证错误（无效的日志级别）
                with pytest.raises(ConfigurationError, match="无效的日志级别"):
                    manager.load_configuration()
        finally:
            os.chdir(original_cwd)

    def test_config_property_not_loaded(self):
        """测试配置未加载时访问config属性"""
        manager = ConfigurationManager()
        with pytest.raises(ConfigurationError, match="配置未加载"):
            _ = manager.config

    def test_get_config_value(self):
        """测试获取配置值"""
        manager = ConfigurationManager()
        # 模拟已加载的配置
        manager._config = EnvironmentConfig(APP_NAME="TestApp", LOG_LEVEL="INFO")

        assert manager.get("APP_NAME") == "TestApp"
        assert manager.get("NON_EXISTENT", "default") == "default"

    def test_reload_configuration(self, tmp_path):
        """测试重新加载配置"""
        # 创建初始配置
        env_content1 = "APP_NAME=FirstApp\nLOG_LEVEL=INFO\nAPP_ENV=development"
        env_file = tmp_path / ".env"
        env_file.write_text(env_content1)

        original_cwd = Path.cwd()
        os.chdir(tmp_path)

        try:
            # 清除环境变量影响
            with patch.dict(os.environ, {}, clear=True):
                manager = ConfigurationManager(str(env_file))
                config1 = manager.load_configuration()
                assert config1.APP_NAME == "FirstApp"

                # 更新配置文件
                env_content2 = "APP_NAME=SecondApp\nLOG_LEVEL=INFO\nAPP_ENV=development"
                env_file.write_text(env_content2)

                # 强重新加载
                config2 = manager.reload()
                assert config2.APP_NAME == "SecondApp"
        finally:
            os.chdir(original_cwd)

    def test_global_config_manager(self):
        """测试全局配置管理器"""
        # 重置全局实例
        import src.config.configuration as config_module

        config_module._config_manager = None

        manager1 = get_config_manager()
        manager2 = get_config_manager()

        assert manager1 is manager2
        assert isinstance(manager1, ConfigurationManager)


class TestEnvironmentConfig:
    """环境配置模型测试"""

    def test_default_values(self):
        """测试默认配置值"""
        # 重置环境变量以确保使用默认值
        with patch.dict(os.environ, {}, clear=True):
            config = EnvironmentConfig()
            assert config.APP_NAME == "Hello-Python"
            assert config.LOG_LEVEL == "INFO"
            assert config.APP_ENV == "development"

    def test_custom_values(self):
        """测试自定义配置值"""
        config = EnvironmentConfig(APP_NAME="CustomApp", LOG_LEVEL="DEBUG", APP_ENV="production")
        assert config.APP_NAME == "CustomApp"
        assert config.LOG_LEVEL == "DEBUG"
        assert config.APP_ENV == "production"


class TestLoggerManager:
    """日志管理器测试"""

    def test_init(self):
        """测试初始化"""
        manager = LoggerManager()
        assert not manager.is_configured
        assert manager._logger is not None

    def test_setup_logger_success(self):
        """测试成功设置日志"""
        manager = LoggerManager()
        config = EnvironmentConfig(LOG_LEVEL="INFO")

        manager.setup_logger(config)
        assert manager.is_configured

    def test_setup_logger_configuration_error(self):
        """测试日志配置错误"""
        manager = LoggerManager()
        with (
            patch("src.config.logging.get_config", side_effect=ConfigurationError("Config error")),
            pytest.raises(LoggerError),
        ):
            manager.setup_logger()

    def test_get_logger(self):
        """测试获取日志记录器"""
        manager = LoggerManager()
        logger = manager.get_logger()
        assert logger is not None

    def test_global_logger_manager(self):
        """测试全局日志管理器"""
        # 重置全局实例
        import src.config.logging as logging_module

        logging_module._logger_manager = None

        manager1 = get_logger_manager()
        manager2 = get_logger_manager()

        assert manager1 is manager2
        assert isinstance(manager1, LoggerManager)

    def test_setup_logger_function(self):
        """测试setup_logger函数"""
        config = EnvironmentConfig()
        logger = setup_logger(config)
        assert logger is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
