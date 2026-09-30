"""数据库装饰器

提供事务处理和会话管理的装饰器功能。
"""

from __future__ import annotations

import random
import time
from collections.abc import Callable
from functools import wraps
from typing import Concatenate, ParamSpec, TypeVar

from sqlalchemy.exc import InterfaceError, OperationalError
from sqlalchemy.orm import Session

from ..exceptions import DatabaseError
from .manager import get_database_manager

P = ParamSpec("P")
R = TypeVar("R")

# 允许重试的数据库异常：连接类故障（超时、锁定、断连）。
# 注意：IntegrityError 等确定性错误重试无意义，不在此列。
RETRYABLE_DB_ERRORS: tuple[type[Exception], ...] = (OperationalError, InterfaceError)


def transactional(
    db_name: str | None = None, auto_commit: bool = True
) -> Callable[[Callable[Concatenate[Session, P], R]], Callable[P, R]]:
    """事务处理装饰器
    自动处理数据库事务，包括提交和回滚

    Args:
        db_name:数据库名称，如果为None则使用默认数据库
        auto_commit:是否自动提交，默认为True

    Returns:
        Callable:装饰器函数
    """

    def decorator(func: Callable[Concatenate[Session, P], R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            manager = get_database_manager()

            # 设置当前数据库
            if db_name:
                manager.set_current_db_name(db_name)

            # 查找参数中已有的数据库会话（外部管理事务时不重复创建）
            existing_session = next((arg for arg in args if isinstance(arg, Session)), None)
            session_owner = existing_session is None

            if existing_session is None:
                db_session = manager.get_session(db_name)
                # 将数据库会话作为第一个参数传入
                call_args = (db_session, *args)
            else:
                db_session = existing_session
                call_args = args

            try:
                # 会话注入是动态行为，Concatenate 类型无法静态表达
                result = func(*call_args, **kwargs)  # type: ignore[arg-type]

                # 只有在自动提交且会话由本装饰器创建时才提交
                if auto_commit and session_owner:
                    db_session.commit()

                return result
            except Exception:
                # 发生异常时总是回滚
                db_session.rollback()
                raise
            finally:
                if session_owner:
                    db_session.close()

        return wrapper

    return decorator


class TransactionError(DatabaseError):
    """事务处理错误异常"""


def retry_on_db_error(
    max_retries: int = 3, delay: float = 1.0, backoff_factor: float = 2.0, jitter: bool = True
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """数据库错误重试装饰器
    仅对 RETRYABLE_DB_ERRORS 中的连接类异常自动重试，
    其他异常（如约束冲突、程序错误）直接抛出。

    Args:
        max_retries:最大重试次数
        delay:初始延迟时间（秒）
        backoff_factor:退避因子
        jitter:是否添加随机抖动

    Returns:
        Callable:装饰器函数
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            retries = 0
            current_delay = delay

            while True:
                try:
                    return func(*args, **kwargs)
                except RETRYABLE_DB_ERRORS as e:
                    retries += 1
                    if retries > max_retries:
                        raise TransactionError(f"操作在 {max_retries} 次重试后仍失败: {e}") from e

                    # 计算下次重试的延迟时间（指数退避 + 可选抖动）
                    sleep_time = current_delay
                    if jitter:
                        sleep_time += current_delay * 0.5 * (random.random() - 0.5)

                    time.sleep(sleep_time)
                    current_delay *= backoff_factor

        return wrapper

    return decorator


def with_db_session(db_name: str | None = None) -> Callable[[Callable[Concatenate[Session, P], R]], Callable[P, R]]:
    """数据库会话装饰器
    自动为函数提供数据库会话参数（作为第一个位置参数注入）。

    Args:
        db_name:数据库名称，如果为None则使用默认数据库

    Returns:
        Callable:装饰器函数
    """

    def decorator(func: Callable[Concatenate[Session, P], R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            manager = get_database_manager()

            # 设置当前数据库
            if db_name:
                manager.set_current_db_name(db_name)

            db_session = manager.get_session(db_name)
            try:
                # 将数据库会话作为第一个参数传递
                return func(db_session, *args, **kwargs)
            finally:
                db_session.close()

        return wrapper

    return decorator
