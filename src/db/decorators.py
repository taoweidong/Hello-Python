# src/db/decorators.py
"""
数据库装饰器
提供事务处理等装饰器功能
"""

from functools import wraps
from typing import Callable, Any, Optional
from sqlalchemy.orm import Session
from .database import get_db, db_manager

def transactional(db_name: Optional[str] = None):
    """
    事务处理装饰器
    自动处理数据库事务，包括提交和回滚
    
    Args:
        db_name: 数据库名称，如果为None则使用默认数据库
        
    Returns:
        Callable: 装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # 设置当前数据库
            if db_name:
                db_manager.set_current_db_name(db_name)
            
            # 查找参数中的数据库会话
            db_session = None
            for arg in args:
                if isinstance(arg, Session):
                    db_session = arg
                    break
            
            db_gen = None
            # 如果没有找到数据库会话，创建一个新的
            if db_session is None:
                db_gen = get_db(db_name)
                db_session = next(db_gen)
                # 将数据库会话添加到参数中
                args = (db_session,) + args
                close_session = True
            else:
                close_session = False
            
            try:
                result = func(*args, **kwargs)
                db_session.commit()
                return result
            except Exception as e:
                db_session.rollback()
                raise e
            finally:
                if close_session and db_gen:
                    db_session.close()
                    # 关闭生成器
                    try:
                        next(db_gen)
                    except StopIteration:
                        pass
        
        return wrapper
    return decorator

def with_db_session(db_name: Optional[str] = None):
    """
    数据库会话装饰器
    自动为函数提供数据库会话参数
    
    Args:
        db_name: 数据库名称，如果为None则使用默认数据库
        
    Returns:
        Callable: 装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # 设置当前数据库
            if db_name:
                db_manager.set_current_db_name(db_name)
            
            db_gen = get_db(db_name)
            db_session = next(db_gen)
            try:
                # 将数据库会话作为第一个参数传递
                result = func(db_session, *args, **kwargs)
                return result
            finally:
                db_session.close()
                # 关闭生成器
                try:
                    next(db_gen)
                except StopIteration:
                    pass
        
        return wrapper
    return decorator