# src/infrastructure/database/decorators.py
"""
数据库装饰器
提供事务处理等装饰器功能

这是独立的基础设施模块，可在其他项目中直接使用。
不依赖任何项目特定代码，确保完全独立性和可复用性。
"""

# 为确保独立性，移除loguru依赖
# 使用Python标准库logging作为备用方案
import contextlib
import logging
import random
import time
from collections.abc import Callable
from functools import wraps
from typing import Any

from sqlalchemy.orm import Session

from .database import db_manager, get_db

logger = logging.getLogger(__name__)


def transactional(db_name: str | None = None, auto_commit: bool = True):
    """
    事务处理装饰器
    自动处理数据库事务，包括提交和回滚

    Args:
        db_name: 数据库名称，如果为None则使用默认数据库
        auto_commit: 是否自动提交，默认为True

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
            for i, arg in enumerate(args):
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

                # 只有在需要自动提交且没有外部提供的会话时才提交
                if auto_commit and close_session:
                    db_session.commit()

                return result
            except Exception as e:
                # 发生异常时总是回滚
                db_session.rollback()
                logger.error(f"Transaction failed in {func.__name__}: {str(e)}")
                raise e
            finally:
                if close_session and db_gen:
                    db_session.close()
                    # 关闭生成器
                    with contextlib.suppress(StopIteration):
                        next(db_gen)

        return wrapper

    return decorator


class TransactionError(Exception):
    """事务处理错误异常"""

    pass


def retry_on_db_error(max_retries: int = 3, delay: float = 1.0, backoff_factor: float = 2.0, jitter: bool = True):
    """
    数据库错误重试装饰器
    当数据库操作失败时自动重试

    Args:
        max_retries: 最大重试次数
        delay:初始延迟时间（秒）
        backoff_factor: 退避因子
        jitter: 是否添加随机抖动

    Returns:
        Callable:器函数
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            retries = 0
            current_delay = delay

            while retries <= max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    # 检查是否是数据库相关的错误
                    if is_database_error(e):
                        retries += 1
                        if retries > max_retries:
                            logger.error(f"Function {func.__name__} failed after {max_retries} retries: {str(e)}")
                            raise TransactionError(f"Operation failed after {max_retries} retries: {str(e)}")

                        # 计算下次重试的延迟时间
                        if jitter:
                            # 添加随机抖动（±50%）
                            jitter_value = current_delay * 0.5 * (random.random() - 0.5)
                            sleep_time = current_delay + jitter_value
                        else:
                            sleep_time = current_delay

                        logger.warning(
                            "Database operation failed (attempt %s/%s), retrying in %.2fs: %s",
                            retries,
                            max_retries,
                            sleep_time,
                            str(e),
                        )
                        time.sleep(sleep_time)

                        # 延迟时间（指数退避）
                        current_delay *= backoff_factor
                    else:
                        # 错误，直接抛出
                        raise

        return wrapper

    return decorator


def is_database_error(exception: Exception) -> bool:
    """
    判断是否是数据库相关的错误

     Args:
         exception:异常对象

     Returns:
         bool: 是否是数据库错误
    """
    db_error_keywords = [
        "database",
        "db",
        "connection",
        "timeout",
        "locked",
        "constraint",
        "integrity",
        "foreign key",
        "unique",
        "duplicate",
        "no such table",
    ]

    error_str = str(exception).lower()
    return any(keyword in error_str for keyword in db_error_keywords)


def with_db_session(db_name: str | None = None):
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
            except Exception as e:
                logger.error(f"Database session error in {func.__name__}: {str(e)}")
                raise
            finally:
                db_session.close()
                # 关闭生成器
                with contextlib.suppress(StopIteration):
                    next(db_gen)

        return wrapper

    return decorator
