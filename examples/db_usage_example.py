"""数据库模块使用示例

演示 src/core/database 的核心能力（二次开发时的标准用法）：
1. 定义业务表：继承 BaseModel 即自动获得 CRUD 能力（见 src/business/models/tables.py）
2. 事务装饰器 @transactional：自动提交/回滚
3. 会话装饰器 @with_db_session：自动注入 Session
4. 多数据库：add_database + set_current_db_name 按线程切换
5. 建表：Base.metadata.create_all（应用启动时由 src/app.py 自动完成）

运行方式：项目根目录下执行 python examples/db_usage_example.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from loguru import logger
from sqlalchemy import Column, String

from src.core.database import (
    BaseModel,
    DatabaseManager,
    transactional,
    with_db_session,
)


# 1) 定义业务表：继承 BaseModel 即拥有 create/get_by_id/update/delete/filter 等 CRUD 方法
class User(BaseModel):
    """示例用户表"""

    __tablename__ = "example_users"

    name = Column(String(50), nullable=False)
    email = Column(String(120), unique=True)


def main() -> None:
    # 2) 创建管理器（生产环境默认读 DATABASE_URL 环境变量，应用启动时由 app.py 完成初始化）
    manager = DatabaseManager("sqlite:///./data/db_usage_example.db")

    # 将 manager 注册为全局实例，装饰器内部通过 get_database_manager() 获取
    import src.core.database.manager as manager_module

    manager_module._database_manager = manager

    # 3) 建表
    manager.create_tables()

    # 4) 事务装饰器：函数正常返回自动提交，抛异常自动回滚
    # 注意：ORM 对象在会话关闭后不可再访问其属性，应在会话内取值后返回普通数据
    @transactional()
    def create_user(session, name: str, email: str) -> str:
        user = User.create(session, name=name, email=email)
        return str(user.id)

    uid = create_user(name="张三", email="zhangsan@example.com")
    logger.info(f"已创建用户: {uid}")

    # 5) 会话装饰器：自动注入 Session 作为第一个参数
    @with_db_session()
    def list_users(session):
        return User.get_all(session)

    logger.info(f"用户总数: {len(list_users())}")

    # 6) 事务回滚演示：插入后抛异常，数据不会落库
    @transactional()
    def broken_insert(session):
        User.create(session, name="李四", email="lisi@example.com")
        raise RuntimeError("模拟业务异常，触发回滚")

    try:
        broken_insert()
    except RuntimeError as e:
        logger.warning(f"捕获预期异常: {e}")

    @with_db_session()
    def count_users(session):
        return User.count(session)

    logger.info(f"回滚后用户总数（应为 1）: {count_users()}")

    # 7) 多数据库：按名称注册并在当前线程切换
    manager.add_database("analytics", "sqlite:///./data/db_usage_example_analytics.db")
    manager.set_current_db_name("analytics")
    logger.info(f"当前线程数据库: {manager.get_current_db_name()}")
    manager.set_current_db_name("default")

    # 8) 上下文管理器方式（不使用装饰器时）
    with manager.get_db_session() as session:
        found = User.filter(session, name="张三")
        logger.info(f"按条件查询到 {len(found)} 条记录")


if __name__ == "__main__":
    main()
