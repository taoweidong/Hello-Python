"""应用主入口

提供简化的应用启动和初始化功能。
"""

import sys
from pathlib import Path

# 添加项目根目录到sys.path
CURRENT_DIR = Path.cwd()
PROJECT_ROOT = CURRENT_DIR.parent if CURRENT_DIR.name == "dist" else CURRENT_DIR
sys.path.insert(0, str(PROJECT_ROOT))

from .core.config import get_settings
from .core.database import initialize_database
from .core.exceptions import CoreException, InitializationError
from .core.logging import setup_logger


class Application:
    """应用主类"""

    def __init__(self) -> None:
        """初始化应用"""
        self._settings = None
        self._logger = None
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

            # 初始化数据库
            try:
                initialize_database(default_url=self._settings.DATABASE_URL, echo=self._settings.DATABASE_ECHO)
            except Exception as e:
                self._logger.warning(f"数据库初始化失败: {e}")

            self._is_initialized = True
            self._logger.info("应用初始化完成")

        except CoreException as e:
            raise InitializationError(f"应用初始化失败: {e}")
        except Exception as e:
            raise InitializationError(f"未知错误导致初始化失败: {e}")

    @property
    def settings(self):
        """获取配置对象"""
        if not self._is_initialized:
            raise InitializationError("应用未初始化")
        return self._settings

    @property
    def logger(self):
        """获取日志对象"""
        if not self._is_initialized:
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
    try:
        app = initialize_app()
        app.logger.info("应用启动成功！")
        print(f"欢迎使用 {app.settings.APP_NAME} v{app.settings.APP_VERSION}")
    except Exception as e:
        print(f"应用启动失败: {e}")
        sys.exit(1)
