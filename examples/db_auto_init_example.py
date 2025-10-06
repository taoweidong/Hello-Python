# examples/db_auto_init_example.py
"""
自动初始化数据库示例
演示如何使用自动初始化的数据库功能
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

# 数据库已自动初始化，可直接使用

@transactional("default")
def create_user_default(db: Session, name: str, email: str):
    """在默认数据库中创建用户"""
    user = User.create(db, name=name, email=email, age=25)
    logger.info(f"在默认数据库中创建用户: {user}")
    return user.id

@transactional("analytics")
def create_user_analytics(db: Session, name: str, email: str):
    """在分析数据库中创建用户"""
    user = User.create(db, name=name, email=email, age=30)
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
    
    # 直接使用数据库功能，无需手动初始化
    logger.info("1. 在默认数据库中创建用户:")
    try:
        user1_id = create_user_default("Alice", "alice@default.com")
    except Exception as e:
        logger.error(f"创建用户时出错: {e}")
        return
    
    logger.info("")
    
    # 在分析数据库中创建用户
    logger.info("2. 在分析数据库中创建用户:")
    try:
        user2_id = create_user_analytics("Bob", "bob@analytics.com")
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