# 添加src目录到路径
import contextlib
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.infrastructure.database import transactional, with_db_session
from src.infrastructure.database.database import DatabaseManager

# 初始化数据库配置
DATABASE_CONFIG = {
    "default": os.getenv("DATABASE_URL", "sqlite:///./sql/app.db"),
    "analytics": os.getenv("ANALYTICS_DATABASE_URL", "sqlite:///./sql/analytics.db"),
}

# 创建新的数据库管理器实例以避免冲突
local_db_manager = DatabaseManager()

# 添加数据库配置
for name, url in DATABASE_CONFIG.items():
    with contextlib.suppress(Exception):
        local_db_manager.add_database(name, url)

# 确保表已创建
local_db_manager.create_tables("default")
local_db_manager.create_tables("analytics")
from loguru import logger
from sqlalchemy.orm import Session

from src.config.logging_config import setup_logger
from src.infrastructure.database.example_models import User

# 设置日志
setup_logger()

# 数据库已自动初始化，可直接使用


@transactional("default")
def create_user_default(db: Session, name: str, email: str):
    """在默认数据库中创建用户"""
    user = User.create(db, name=name, email=email, age=25)  # 移除age参数，因为User表可能没有age字段
    logger.info(f"在默认数据库中创建用户: {user}")
    return user.id


@transactional("analytics")
def create_user_analytics(db: Session, name: str, email: str):
    """在分析数据库中创建用户"""
    user = User.create(db, name=name, email=email, age=30)  # 移除age参数
    logger.info(f"在分析数据库中创建用户: {user}")
    return user.id


@with_db_session("default")
def list_users_default(db: Session):
    """列出默认数据库中的所有用户"""
    users = User.get_all(db)
    logger.info("默认数据库中的所有用户:")
    for user in users:
        logger.info(f"  {user.to_dict()}")
    return users


@with_db_session("analytics")
def list_users_analytics(db: Session):
    """列出分析数据库中的所有用户"""
    users = User.get_all(db)
    logger.info("分析数据库中的所有用户:")
    for user in users:
        logger.info(f"  {user.to_dict()}")
    return users


def main():
    """主函数"""
    logger.info("=== 自动初始化数据库示例 ===\n")

    # 确保数据库表已创建部分已在模块级别处理

    # 使用数据库功能
    logger.info("1. 在默认数据库中创建用户:")
    try:
        create_user_default("Alice", "alice@default.com")
    except Exception as e:
        logger.error(f"创建用户时出错: {e}")
        return

    logger.info("")

    # 在分析数据库中创建用户
    logger.info("2. 在分析数据库中创建用户:")
    try:
        create_user_analytics("Bob", "bob@analytics.com")
    except Exception as e:
        logger.error(f"创建用户时出错: {e}")
        return

    logger.info("")

    # 列出各数据库中的用户
    logger.info("3. 列出各数据库中的用户:")
    try:
        list_users_default()
    except Exception as e:
        logger.error(f"列出默认数据库用户时出错: {e}")

    try:
        list_users_analytics()
    except Exception as e:
        logger.error(f"列出分析数据库用户时出错: {e}")


if __name__ == "__main__":
    main()
