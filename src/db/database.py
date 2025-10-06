# src/db/database.py
"""
数据库管理器
提供数据库连接和会话管理功能
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager
import os
from typing import Generator, Optional, Dict, Any

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
            self.db_name = 'default'
    _thread_locals = Local()

class DatabaseManager:
    """数据库管理器类"""
    
    def __init__(self, default_url: Optional[str] = None):
        """初始化数据库管理器"""
        # 存储多个数据库配置
        self.databases: Dict[str, dict] = {}
        self.engines: Dict[str, Any] = {}
        self.sessions: Dict[str, Any] = {}
        
        # 添加默认数据库配置
        if default_url is None:
            default_url = os.getenv("DATABASE_URL", "sqlite:///./app.db")
        self.add_database("default", default_url)
    
    def add_database(self, name: str, database_url: str):
        """
        添加数据库配置
        
        Args:
            name: 数据库名称
            database_url: 数据库URL
        """
        self.databases[name] = {
            "url": database_url
        }
        # 创建引擎和会话工厂
        engine = create_engine(database_url, echo=False)
        session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        self.engines[name] = engine
        self.sessions[name] = session_factory
    
    def get_current_db_name(self) -> str:
        """
        获取当前线程的数据库名称
        
        Returns:
            str: 数据库名称
        """
        if hasattr(_thread_locals, 'db_name'):
            db_name = _thread_locals.db_name
            # 确保返回的是字符串
            return str(db_name) if db_name else 'default'
        return 'default'
    
    def set_current_db_name(self, name: str):
        """
        设置当前线程的数据库名称
        
        Args:
            name: 数据库名称
        """
        if name not in self.databases:
            raise ValueError(f"Database '{name}' not configured")
        _thread_locals.db_name = name
    
    def get_engine(self, name: Optional[str] = None):
        """
        获取数据库引擎
        
        Args:
            name: 数据库名称，如果为None则使用当前线程的数据库
            
        Returns:
            数据库引擎
        """
        if name is None:
            name = self.get_current_db_name()
        return self.engines[name]
    
    def get_session_factory(self, name: Optional[str] = None):
        """
        获取会话工厂
        
        Args:
            name: 数据库名称，如果为None则使用当前线程的数据库
            
        Returns:
            会话工厂
        """
        if name is None:
            name = self.get_current_db_name()
        return self.sessions[name]
    
    def create_tables(self, db_name: Optional[str] = None):
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
    
    def drop_tables(self, db_name: Optional[str] = None):
        """
        删除所有表
        
        Args:
            db_name: 数据库名称，如果为None则使用当前线程的数据库
        """
        if db_name is None:
            db_name = self.get_current_db_name()
        engine = self.get_engine(db_name)
        Base.metadata.drop_all(bind=engine)
    
    def get_session(self, db_name: Optional[str] = None) -> Session:
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
    def get_db_session(self, db_name: Optional[str] = None) -> Generator[Session, None, None]:
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

# 创建全局数据库管理器实例
db_manager = DatabaseManager()

def get_db(db_name: Optional[str] = None) -> Generator[Session, None, None]:
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

def initialize_databases(config: Optional[Dict[str, str]] = None, default_url: Optional[str] = None):
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
            print(f"警告: 无法为数据库 '{db_name}' 创建表: {e}")