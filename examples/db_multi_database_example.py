# examples/db_multi_database_example.py
"""
多数据库操作示例
演示如何使用带参数的装饰器来切换不同的数据库
"""

import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.db import transactional, with_db_session
from src.db.example_models import User
from src.config.logging_config import setup_logger
from loguru import logger
from sqlalchemy.orm import Session

# 设置日志
setup_logger()

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

@transactional("analytics")
def create_user_analytics_db(db: Session, name: str, email: str):
    """
    在analytics数据库中创建用户
    
    Args:
        db: 数据库会话
        name: 用户名
        email: 用户邮箱
    """
    user = User.create(db, name=name, email=email, age=30)
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

@with_db_session("analytics")
def list_users_analytics_db(db: Session):
    """列出analytics数据库中的所有用户"""
    users = User.get_all(db)
    logger.info("Analytics数据库中的所有用户:")
    for user in users:
        logger.info(f"  {user.to_dict()}")
    return users

def main():
    """主函数"""
    logger.info("=== 多数据库操作示例 ===\n")
    
    # 在默认数据库中创建用户
    logger.info("1. 在默认数据库中创建用户:")
    try:
        user1_id = create_user_default_db("Alice", "alice@example.com")
    except Exception as e:
        logger.error(f"创建用户时出错: {e}")
        return
    
    logger.info("")
    
    # 在analytics数据库中创建用户
    logger.info("2. 在analytics数据库中创建用户:")
    try:
        user2_id = create_user_analytics_db("Bob", "bob@example.com")
    except Exception as e:
        logger.error(f"创建用户时出错: {e}")
        return
    
    logger.info("")
    
    # 列出默认数据库中的所有用户
    logger.info("3. 列出默认数据库中的所有用户:")
    list_users_default_db()
    
    logger.info("")
    
    # 列出analytics数据库中的所有用户
    logger.info("4. 列出analytics数据库中的所有用户:")
    list_users_analytics_db()
    
    logger.info("")
    
    # 再次在默认数据库中创建用户以验证隔离性
    logger.info("5. 再次在默认数据库中创建用户:")
    try:
        user3_id = create_user_default_db("Charlie", "charlie@example.com")
    except Exception as e:
        logger.error(f"创建用户时出错: {e}")
        return
    
    logger.info("")
    
    # 再次列出两个数据库中的用户以验证隔离性
    logger.info("6. 验证数据库隔离性:")
    list_users_default_db()
    list_users_analytics_db()

if __name__ == "__main__":
    main()