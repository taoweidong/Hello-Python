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
from typing import Generator, Optional

# 创建基类
Base = declarative_base()

class DatabaseManager:
    """数据库管理器类"""
    
    def __init__(self, database_url: Optional[str] = None):
        """
        初始化数据库管理器
        
        Args:
            database_url: 数据库URL，如果未提供则从环境变量获取
        """
        if database_url is None:
            database_url = os.getenv("DATABASE_URL", "sqlite:///./app.db")
        
        self.database_url = database_url
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def create_tables(self):
        """创建所有表"""
        from . import models  # 确保导入所有模型
        Base.metadata.create_all(bind=self.engine)
    
    def drop_tables(self):
        """删除所有表"""
        Base.metadata.drop_all(bind=self.engine)
    
    def get_session(self) -> Session:
        """
        获取数据库会话
        
        Returns:
            Session: 数据库会话对象
        """
        return self.SessionLocal()
    
    @contextmanager
    def get_db_session(self) -> Generator[Session, None, None]:
        """
        获取数据库会话上下文管理器
        
        Yields:
            Session: 数据库会话对象
        """
        db = self.SessionLocal()
        try:
            yield db
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

# 创建全局数据库管理器实例
db_manager = DatabaseManager()

def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话依赖
    
    Yields:
        Session: 数据库会话对象
    """
    db = db_manager.get_session()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()