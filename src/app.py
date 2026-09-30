"""应用主入口

提供简化的应用启动和初始化功能。
"""

from __future__ import annotations

import sys
from pathlib import Path

from .business.models import tables  # noqa: F401  确保业务表注册到 Base.metadata，应用启动时统一建表
from .core.config import Settings, get_settings
from .core.database import get_database_manager, initialize_database
from .core.exceptions import CoreException, InitializationError
from .core.logging import Logger, setup_logger


class Application:
    """应用主类"""

    def __init__(self) -> None:
        """初始化应用"""
        self._settings: Settings | None = None
        self._logger: Logger | None = None
        self._is_initialized = False

    def initialize(self, env_file: str | None = None) -> None:
        """初始化应用

        Args:
            env_file:环境配置文件路径

        Raises:
            InitializationError:初始化失败时
        """
        try:
            # 加载配置
            self._settings = get_settings(env_file)

            # 设置日志
            self._logger = setup_logger(self._settings)
            self._logger.info(f"应用启动: {self._settings.APP_NAME}")
            self._logger.info(f"版本: {self._settings.APP_VERSION}")
            self._logger.info(f"环境: {self._settings.APP_ENV.value}")

            # 初始化数据库并创建业务表
            try:
                self._ensure_sqlite_parent_dir(self._settings.DATABASE_URL)
                initialize_database(default_url=self._settings.DATABASE_URL, echo=self._settings.DATABASE_ECHO)
                get_database_manager().create_tables()
            except Exception as e:
                self._logger.warning(f"数据库初始化失败: {e}")

            self._is_initialized = True
            self._logger.info("应用初始化完成")

        except CoreException as e:
            raise InitializationError(f"应用初始化失败: {e}") from e
        except Exception as e:
            raise InitializationError(f"未知错误导致初始化失败: {e}") from e

    @staticmethod
    def _ensure_sqlite_parent_dir(database_url: str) -> None:
        """sqlite 数据库文件不存在时会自动创建，但其父目录不会，这里提前确保存在"""
        if database_url.startswith("sqlite:///") and not database_url.endswith(":memory:"):
            db_path = Path(database_url.removeprefix("sqlite:///"))
            db_path.parent.mkdir(parents=True, exist_ok=True)

    @property
    def settings(self) -> Settings:
        """获取配置对象"""
        if not self._is_initialized or self._settings is None:
            raise InitializationError("应用未初始化")
        return self._settings

    @property
    def logger(self) -> Logger:
        """获取日志对象"""
        if not self._is_initialized or self._logger is None:
            raise InitializationError("应用未初始化")
        return self._logger

    @property
    def is_initialized(self) -> bool:
        """检查应用是否已初始化"""
        return self._is_initialized


# 全局应用实例
_app: Application | None = None


def get_application() -> Application:
    """获取全局应用实例

    Returns:
        Application:应用实例
    """
    global _app
    if _app is None:
        _app = Application()
    return _app


def initialize_app(env_file: str | None = None) -> Application:
    """初始化并获取应用实例

    Args:
        env_file:环境配置文件路径

    Returns:
        Application:初始化的应用实例
    """
    app = get_application()
    if not app.is_initialized:
        app.initialize(env_file)
    return app


if __name__ == "__main__":
    # 简单的应用启动示例
    from loguru import logger as loguru_logger

    try:
        app = initialize_app()
        app.logger.info("应用启动成功！")
        app.logger.info(f"欢迎使用 {app.settings.APP_NAME} v{app.settings.APP_VERSION}")
    except Exception:
        loguru_logger.exception("应用启动失败")
        sys.exit(1)
