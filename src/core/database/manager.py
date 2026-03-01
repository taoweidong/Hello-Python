"""数据库管理器

提供数据库连接管理、会话管理和多数据库支持功能。
"""

from typing import Optional, Dict, Any, Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import os
import threading

from .base import Base
from ..exceptions import DatabaseError, ConfigurationError


class DatabaseConfig:
    """数据库配置类"""
    
    def __init__(self, url: str, echo: bool = False):
        self.url = url
        self.echo = echo


class DatabaseManager:
    """数据库管理器类"""
    
    def __init__(self, default_url: Optional[str] = None, echo: bool = False):
        """初始化数据库管理器
        
        Args:
            default_url:默认数据库URL
            echo:是否输出SQL语句
        """
        self._databases: Dict[str, DatabaseConfig] = {}
        self._engines: Dict[str, Any] = {}
        self._sessions: Dict[str, Any] = {}
        self._echo = echo
        
        #线程本地存储
        self._thread_locals = threading.local()
        
        # 添加默认数据库配置
        if default_url is None:
            default_url = os.getenv("DATABASE_URL", "sqlite:///./sql/app.db")
        self.add_database("default", default_url, echo)
    
    def add_database(self, name: str, database_url: str, echo: Optional[bool] = None) -> None:
        """添加数据库配置
        
        Args:
            name:数据库名称
            database_url:数据库URL
            echo:是否输出SQL语句，如果为None则使用全局设置
            
        Raises:
            ConfigurationError:数据库已存在时
        """
        if name in self._databases:
            raise ConfigurationError(f"数据库 '{name}'已存在")
        
        echo_flag = echo if echo is not None else self._echo
        self._databases[name] = DatabaseConfig(database_url, echo_flag)
        
        # 创建引擎和会话工厂
        engine = create_engine(database_url, echo=echo_flag)
        session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        self._engines[name] = engine
        self._sessions[name] = session_factory
    
    def get_current_db_name(self) -> str:
        """获取当前线程的数据库名称
        
        Returns:
            str:数据库名称
        """
        return getattr(self._thread_locals, '_current_db_name', 'default')
    
    def set_current_db_name(self, name: str) -> None:
        """设置当前线程的数据库名称
        
        Args:
            name:数据库名称
            
        Raises:
            ConfigurationError:数据库未配置时
        """
        if name not in self._databases:
            raise ConfigurationError(f"数据库 '{name}' 未配置")
        self._thread_locals._current_db_name = name
    
    def get_engine(self, name: Optional[str] = None):
        """获取数据库引擎
        
        Args:
            name:数据库名称，如果为None则使用当前线程的数据库
            
        Returns:
            数据库引擎
            
        Raises:
            DatabaseError:引擎未找到时
        """
        if name is None:
            name = self.get_current_db_name()
        if name not in self._engines:
            raise DatabaseError(f"数据库 '{name}' 的引擎未找到")
        return self._engines[name]
    
    def get_session_factory(self, name: Optional[str] = None):
        """获取会话工厂
        
        Args:
            name:数据库名称，如果为None则使用当前线程的数据库
            
        Returns:
            会话工厂
            
        Raises:
            DatabaseError:会话工厂未找到时
        """
        if name is None:
            name = self.get_current_db_name()
        if name not in self._sessions:
            raise DatabaseError(f"数据库 '{name}' 的会话工厂未找到")
        return self._sessions[name]
    
    def create_tables(self, db_name: Optional[str] = None) -> None:
        """创建所有表
        
        Args:
            db_name:数据库名称，如果为None则使用当前线程的数据库
        """
        engine = self.get_engine(db_name)
        Base.metadata.create_all(bind=engine)
    
    def drop_tables(self, db_name: Optional[str] = None) -> None:
        """删除所有表
        
        Args:
            db_name:数据库名称，如果为None则使用当前线程的数据库
        """
        engine = self.get_engine(db_name)
        Base.metadata.drop_all(bind=engine)
    
    def get_session(self, db_name: Optional[str] = None) -> Session:
        """获取数据库会话
        
        Args:
            db_name:数据库名称，如果为None则使用当前线程的数据库
            
        Returns:
            Session:数据库会话对象
        """
        session_factory = self.get_session_factory(db_name)
        return session_factory()
    
    @contextmanager
    def get_db_session(self, db_name: Optional[str] = None) -> Generator[Session, None, None]:
        """获取数据库会话上下文管理器
        
        Args:
            db_name:数据库名称，如果为None则使用当前线程的数据库
            
        Yields:
            Session:数据库会话对象
        """
        db = self.get_session(db_name)
        try:
            yield db
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
    
    def test_connection(self, db_name: Optional[str] = None) -> bool:
        """测试数据库连接
        
        Args:
            db_name:数据库名称，如果为None则使用当前线程的数据库
            
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
    
    def get_database_info(self, db_name: Optional[str] = None) -> Dict[str, Any]:
        """获取数据库信息
        
        Args:
            db_name:数据库名称，如果为None则使用当前线程的数据库
            
        Returns:
            Dict[str, Any]:数据库信息
        """
        if db_name is None:
            db_name = self.get_current_db_name()
        
        return {
            'name': db_name,
            'url': self._databases.get(db_name, DatabaseConfig('')).url,
            'echo': self._databases.get(db_name, DatabaseConfig('')).echo,
            'connected': self.test_connection(db_name)
        }
    
    @property
    def databases(self) -> list:
        """获取所有数据库名称列表
        
        Returns:
            list:数据库名称列表
        """
        return list(self._databases.keys())


#全局数据库管理器实例
_database_manager: Optional[DatabaseManager] = None


def get_database_manager(default_url: Optional[str] = None, echo: bool = False) -> DatabaseManager:
    """获取全局数据库管理器实例
    
    Args:
        default_url:默认数据库URL
        echo:是否输出SQL语句
        
    Returns:
        DatabaseManager:数据库管理器实例
    """
    global _database_manager
    if _database_manager is None:
        _database_manager = DatabaseManager(default_url, echo)
    return _database_manager


def initialize_database(config: Optional[Dict[str, str]] = None, 
                      default_url: Optional[str] = None,
                      echo: bool = False) -> None:
    """初始化数据库配置
    
    Args:
        config:数据库配置字典，格式为 {name: database_url}
        default_url:默认数据库URL
        echo:是否输出SQL语句
        
    Raises:
        ConfigurationError:配置错误时
    """
    manager = get_database_manager(default_url, echo)
    
    # 添加额外的数据库配置
    if config:
        for name, url in config.items():
            if name != "default":  #避免重复添加默认数据库
                manager.add_database(name, url, echo)
    
    #测试所有数据库连接
    for db_name in manager.databases:
        if not manager.test_connection(db_name):
            print(f"警告: 数据库连接测试失败: {db_name}")


def get_db(db_name: Optional[str] = None) -> Generator[Session, None, None]:
    """获取数据库会话依赖（用于FastAPI等框架）
    
    Args:
        db_name:数据库名称，如果为None则使用当前线程的数据库
        
    Yields:
        Session:数据库会话对象
    """
    manager = get_database_manager()
    db = manager.get_session(db_name)
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()