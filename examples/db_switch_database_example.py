# examples/db_switch_database_example.py
"""
数据库切换示例
演示如何使用带参数的装饰器来切换不同的数据库
"""

import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.db import transactional, with_db_session, db_manager
from src.db.example_models import User
from src.config.logging_config import setup_logger
from loguru import logger
from sqlalchemy.orm import Session

# 设置日志
setup_logger()

# 使用装饰器参数指定数据库
@transactional("default")
def create_user_default_db(db: Session, name: str, email: str):
    """
    在默认数据库中创建用户
    
    Args:
        db: 数据库会话
        name: 用户名
        email: 用户邮箱
    """
    user = User.create(db, name=name, email=email, age=25)
    logger.info(f"在默认数据库中创建用户: {user}")
    return user.id

@transactional("secondary")
def create_user_secondary_db(db: Session, name: str, email: str):
    """
    在secondary数据库中创建用户
    
    Args:
        db: 数据库会话
        name: 用户名
        email: 用户邮箱
    """
    user = User.create(db, name=name, email=email, age=30)
    logger.info(f"在secondary数据库中创建用户: {user}")
    return user.id

@transactional("analytics")
def create_user_analytics_db(db: Session, name: str, email: str):
    """
    在analytics数据库中创建用户
    
    Args:
        db: 数据库会话
        name: 用户名
        email: 用户邮箱
    """
    user = User.create(db, name=name, email=email, age=35)
    logger.info(f"在analytics数据库中创建用户: {user}")
    return user.id

@with_db_session("default")
def list_users_default_db(db: Session):
    """列出默认数据库中的所有用户"""
    users = User.get_all(db)
    logger.info("默认数据库中的所有用户:")
    for user in users:
        logger.info(f"  {user.to_dict()}")
    return users

@with_db_session("secondary")
def list_users_secondary_db(db: Session):
    """列出secondary数据库中的所有用户"""
    users = User.get_all(db)
    logger.info("Secondary数据库中的所有用户:")
    for user in users:
        logger.info(f"  {user.to_dict()}")
    return users

@with_db_session("analytics")
def list_users_analytics_db(db: Session):
    """列出analytics数据库中的所有用户"""
    users = User.get_all(db)
    logger.info("Analytics数据库中的所有用户:")
    for user in users:
        logger.info(f"  {user.to_dict()}")
    return users

def demonstrate_database_isolation():
    """演示数据库隔离性"""
    logger.info("=== 数据库隔离性演示 ===")
    
    # 在不同数据库中创建同名用户
    with db_manager.get_db_session("default") as db:
        User.create(db, name="TestUser", email="test@default.com", age=20)
    
    with db_manager.get_db_session("secondary") as db:
        User.create(db, name="TestUser", email="test@secondary.com", age=21)
    
    with db_manager.get_db_session("analytics") as db:
        User.create(db, name="TestUser", email="test@analytics.com", age=22)
    
    # 查看各数据库中的用户
    list_users_default_db()
    list_users_secondary_db()
    list_users_analytics_db()

def main():
    """主函数"""
    logger.info("=== 数据库切换示例 ===\n")
    
    # 在默认数据库中创建用户
    logger.info("1. 在默认数据库中创建用户:")
    try:
        user1_id = create_user_default_db("Alice", "alice@default.com")
    except Exception as e:
        logger.error(f"创建用户时出错: {e}")
        return
    
    logger.info("")
    
    # 在secondary数据库中创建用户
    logger.info("2. 在secondary数据库中创建用户:")
    try:
        user2_id = create_user_secondary_db("Bob", "bob@secondary.com")
    except Exception as e:
        logger.error(f"创建用户时出错: {e}")
        return
    
    logger.info("")
    
    # 在analytics数据库中创建用户
    logger.info("3. 在analytics数据库中创建用户:")
    try:
        user3_id = create_user_analytics_db("Charlie", "charlie@analytics.com")
    except Exception as e:
        logger.error(f"创建用户时出错: {e}")
        return
    
    logger.info("")
    
    # 列出各数据库中的所有用户
    logger.info("4. 列出各数据库中的所有用户:")
    list_users_default_db()
    list_users_secondary_db()
    list_users_analytics_db()
    
    logger.info("")
    
    # 演示数据库隔离性
    logger.info("5. 演示数据库隔离性:")
    demonstrate_database_isolation()

if __name__ == "__main__":
    main()