# src/infrastructure/database/database.py
"""
数据库管理器
提供数据库连接和会话管理功能

这是独立的基础设施模块，可在其他项目中直接使用。
不依赖任何项目特定代码，确保完全独立性和可复用性。
"""

# 使用 loguru 作为统一日志方案
import os
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

logger = logger.bind(module=__name__)


# 如果项目使用loguru，可提供配置方法
def set_logger(external_logger):
    """
    设置外部日志器（如loguru）

    Args:
        external_logger:外日志器实例
    """
    global logger
    logger = external_logger


# 创建基类
Base = declarative_base()

# 线程本地存储，用于存储当前线程的数据库标识
try:
    from threading import local

    _thread_locals = local()
except ImportError:
    # 如果 threading 不可用，使用简单对象
    class Local:
        def __init__(self):
            self._current_db_name = "default"

    _thread_locals = Local()


class DatabaseConfig:
    """数据库配置类"""

    def __init__(self, url: str):
        self.url = url


class DatabaseManager:
    """数据库管理器类"""

    def __init__(self, default_url: str | None = None):
        """初始化数据库管理器"""
        # 存储多个数据库配置
        self._databases: dict[str, DatabaseConfig] = {}
        self._engines: dict[str, Any] = {}
        self._sessions: dict[str, Any] = {}

        # 添加默认数据库配置
        if default_url is None:
            default_url = os.getenv("DATABASE_URL", "sqlite:///./sql/app.db")
        self.add_database("default", default_url)

    def add_database(self, name: str, database_url: str):
        """
        添加数据库配置

        Args:
            name: 数据库名称
            database_url: 数据库URL
        """
        if name in self._databases:
            raise DatabaseConfigurationError(f"数据库 '{name}'已存在")

        self._databases[name] = DatabaseConfig(database_url)
        # 创建引擎和会话工厂
        engine = create_engine(database_url, echo=False)
        session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        self._engines[name] = engine
        self._sessions[name] = session_factory

    def get_current_db_name(self) -> str:
        """
        获取当前线程的数据库名称

        Returns:
            str: 数据库名称
        """
        if hasattr(_thread_locals, "_current_db_name"):
            db_name = getattr(_thread_locals, "_current_db_name", "default")
            # 确保返回的是字符串
            return str(db_name) if db_name else "default"
        return "default"

    def set_current_db_name(self, name: str):
        """
        设置当前线程的数据库名称

        Args:
            name: 数据库名称
        """
        if name not in self._databases:
            raise DatabaseConfigurationError(f"数据库 '{name}' 未配置")
        _thread_locals._current_db_name = name

    def get_engine(self, name: str | None = None):
        """
        获取数据库引擎

        Args:
            name: 数据库名称，如果为None则使用当前线程的数据库

        Returns:
            数据库引擎
        """
        if name is None:
            name = self.get_current_db_name()
        if name not in self._engines:
            raise DatabaseConfigurationError(f"数据库 '{name}' 的引擎未找到")
        return self._engines[name]

    def get_session_factory(self, name: str | None = None):
        """
        获取会话工厂

        Args:
            name: 数据库名称，如果为None则使用当前线程的数据库

        Returns:
            会话工厂
        """
        if name is None:
            name = self.get_current_db_name()
        if name not in self._sessions:
            raise DatabaseConfigurationError(f"数据库 '{name}' 的会话工厂未找到")
        return self._sessions[name]

    def create_tables(self, db_name: str | None = None):
        """
        创建所有表

        Args:
            db_name: 数据库名称，如果为None则使用当前线程的数据库
        """
        # 注意：在独立模块中，需要确保模型已被导入
        # 在实际使用中，应在调用此方法前导入所有模型
        if db_name is None:
            db_name = self.get_current_db_name()
        engine = self.get_engine(db_name)
        Base.metadata.create_all(bind=engine)

    def drop_tables(self, db_name: str | None = None):
        """
        删除所有表

        Args:
            db_name: 数据库名称，如果为None则使用当前线程的数据库
        """
        if db_name is None:
            db_name = self.get_current_db_name()
        engine = self.get_engine(db_name)
        Base.metadata.drop_all(bind=engine)

    def get_session(self, db_name: str | None = None) -> Session:
        """
        获取数据库会话

        Args:
            db_name: 数据库名称，如果为None则使用当前线程的数据库

        Returns:
            Session: 数据库会话对象
        """
        session_factory = self.get_session_factory(db_name)
        return session_factory()

    @contextmanager
    def get_db_session(self, db_name: str | None = None) -> Generator[Session, None, None]:
        """
        获取数据库会话上下文管理器

        Args:
            db_name: 数据库名称，如果为None则使用当前线程的数据库

        Yields:
            Session: 数据库会话对象
        """
        db = self.get_session(db_name)
        try:
            yield db
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def test_connection(self, db_name: str | None = None) -> bool:
        """测试数据库连接

        Args:
            db_name: 数据库名称，如果为None则使用当前线程的数据库

        Returns:
            bool:连接是否成功
        """
        try:
            engine = self.get_engine(db_name)
            with engine.connect() as connection:
                from sqlalchemy import text

                connection.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    def get_database_info(self, db_name: str | None = None) -> dict[str, Any]:
        """获取数据库信息

        Args:
            db_name: 数据库名称，如果为None则使用当前线程的数据库

        Returns:
            Dict[str, Any]: 数据库信息
        """
        if db_name is None:
            db_name = self.get_current_db_name()

        info = {
            "name": db_name,
            "url": self._databases.get(db_name, DatabaseConfig("")).url,
            "connected": self.test_connection(db_name),
            "tables": [],
        }

        return info

    @property
    def databases(self) -> list[str]:
        """获取所有数据库名称列表

        Returns:
            List[str]: 数据库名称列表
        """
        return list(self._databases.keys())


class DatabaseError(Exception):
    """数据库错误异常"""

    pass


class DatabaseConfigurationError(DatabaseError):
    """数据库配置错误异常"""

    pass


class DatabaseConnectionError(DatabaseError):
    """数据库连接错误异常"""

    pass


# 创建全局数据库管理器实例
db_manager = DatabaseManager()

# 全局数据库管理器实例
_database_manager: DatabaseManager | None = None


def get_database_manager(default_url: str | None = None) -> DatabaseManager:
    """获取全局数据库管理器实例

    Args:
        default_url: 默认数据库URL

    Returns:
        DatabaseManager: 数据库管理器实例
    """
    global _database_manager
    if _database_manager is None:
        _database_manager = DatabaseManager(default_url)
    return _database_manager


def initialize_database(config: dict[str, str] | None = None, default_url: str | None = None) -> None:
    """初始化数据库配置

    Args:
        config: 数据库配置字典，格式为 {name: database_url}
        default_url: 默认数据库URL

    Raises:
        DatabaseConfigurationError: 配置错误时
    """
    manager = get_database_manager(default_url)

    # 添加额外的数据库配置
    if config:
        for name, url in config.items():
            if name != "default":  # 避免重复添加默认数据库
                manager.add_database(name, url)

    # 测试所有数据库连接
    for db_name in manager.databases:
        if not manager.test_connection(db_name):
            logger.warning(f"数据库连接测试失败: {db_name}")


# 全局数据库管理器实例
_database_manager: DatabaseManager | None = None


def get_db(db_name: str | None = None) -> Generator[Session, None, None]:
    """
    获取数据库会话依赖

    Args:
        db_name: 数据库名称，如果为None则使用当前线程的数据库

    Yields:
        Session: 数据库会话对象
    """
    db = db_manager.get_session(db_name)
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def initialize_databases(config: dict[str, str] | None = None, default_url: str | None = None):
    """
    初始化数据库配置

    Args:
        config: 数据库配置字典，格式为 {name: database_url}
        default_url: 默认数据库URL
    """
    # 如果提供了默认URL，则重新初始化db_manager
    if default_url is not None:
        global db_manager
        db_manager = DatabaseManager(default_url)

    # 如果提供了配置，则添加数据库
    if config:
        for name, url in config.items():
            db_manager.add_database(name, url)

    # 创建所有已配置数据库的表
    for db_name in db_manager.databases:
        try:
            db_manager.create_tables(db_name)
        except Exception as e:
            # 使用 logger 输出警告，便于上层捕获和配置
            logger.warning(f"警告: 无法为数据库 '{db_name}' 创建表: {e}")
