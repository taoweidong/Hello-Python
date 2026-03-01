"""配置管理模块

提供统一的配置管理功能，包括环境变量加载、配置验证和类型转换。
"""

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from loguru import logger
from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigurationError(Exception):
    """配置错误异常"""

    pass


class EnvironmentConfig(BaseSettings):
    """环境配置模型"""

    model_config = SettingsConfigDict(env_file_encoding="utf-8")

    APP_NAME: str = Field(default="Hello-Python", description="应用名称")
    LOG_LEVEL: str = Field(default="INFO", description="日志级别")
    DATA_FILE_PATH: str = Field(default="data/input.csv", description="数据文件路径")
    DATABASE_URL: str = Field(default="sqlite:///./sql/app.db", description="数据库URL")
    APP_ENV: str = Field(default="development", description="应用环境")


class ConfigurationManager:
    """配置管理器

    加载、验证和管理应用程序配置。
    支持多环境配置文件和环境变量覆盖。
    """

    def __init__(self, env_file: str | None = None) -> None:
        """初始化配置管理器

        Args:
            env_file:环配置境配置文件路径，如果为None则自动检测
        """
        self._config: EnvironmentConfig | None = None
        self._env_file: str | None = env_file
        self._logger = logger.bind(module=__name__)

    def _detect_env_file(self) -> str:
        """检测环境配置文件

        Returns:
            str:配置文件路径

        Raises:
            ConfigurationError: 当找不到配置文件时
        """
        # 获取环境变量
        app_env = os.getenv("APP_ENV", "development")

        # 根据环境变量确定配置文件
        env_file = f".env.{app_env}" if app_env != "development" else ".env"

        # 检查文件是否存在
        if not Path(env_file).exists():
            if Path(".env").exists():
                env_file = ".env"
            else:
                raise ConfigurationError(f"配置文件不存在: {env_file}")

        return env_file

    def load_configuration(self) -> EnvironmentConfig:
        """加载配置

        Returns:
            EnvironmentConfig: 配置对象

        Raises:
            ConfigurationError: 配置加载失败时
        """
        try:
            # 确定配置文件
            if self._env_file is None:
                self._env_file = self._detect_env_file()

            # 加载环境变量
            if self._env_file:
                # 使用override=True来覆盖现有环境变量
                load_dotenv(self._env_file, override=True)
                self._logger.info(f"已加载配置文件: {self._env_file}")

            # 创建配置对象
            self._config = EnvironmentConfig()

            # 验证配置
            self._validate_configuration()

            self._logger.info("配置加载成功")
            return self._config

        except ValidationError as e:
            raise ConfigurationError(f"配置验证失败: {e}")
        except Exception as e:
            raise ConfigurationError(f"配置加载失败: {e}")

    def _validate_configuration(self) -> None:
        """验证配置

        Raises:
            ConfigurationError: 配置验证失败时
        """
        if self._config is None:
            raise ConfigurationError("配置未加载")

        # 验证日志级别
        valid_log_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if self._config.LOG_LEVEL not in valid_log_levels:
            raise ConfigurationError(f"无效的日志级别: {self._config.LOG_LEVEL}")

        # 验证数据文件路径
        if self._config.DATA_FILE_PATH:
            data_path = Path(self._config.DATA_FILE_PATH)
            if data_path.is_absolute() and not data_path.exists():
                self._logger.warning(f"数据文件路径不存在: {self._config.DATA_FILE_PATH}")

    @property
    def config(self) -> EnvironmentConfig:
        """获取配置对象

        Returns:
            EnvironmentConfig: 配置对象

        Raises:
            ConfigurationError: 配置未加载时
        """
        if self._config is None:
            raise ConfigurationError("配置未加载，请先调用 load_configuration()")
        return self._config

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值

        Args:
            key:配置键名
            default: 默认值

        Returns:
            Any: 配置值
        """
        if self._config is None:
            return default
        return getattr(self._config, key, default)

    def reload(self) -> EnvironmentConfig:
        """重新加载配置

        Returns:
            EnvironmentConfig: 重新加载的配置对象
        """
        self._logger.info("重新加载配置")
        # 清除现有配置以强制重新加载
        self._config = None
        return self.load_configuration()


# 全局配置管理器实例
_config_manager: ConfigurationManager | None = None


def get_config_manager(env_file: str | None = None) -> ConfigurationManager:
    """获取全局配置管理器实例

    Args:
        env_file:环境配置文件路径

    Returns:
        ConfigurationManager: 配置管理器实例
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigurationManager(env_file)
    return _config_manager


def get_config() -> EnvironmentConfig:
    """获取全局配置对象

    Returns:
        EnvironmentConfig: 配置对象

    Raises:
        ConfigurationError: 配置未加载时
    """
    manager = get_config_manager()
    return manager.config
