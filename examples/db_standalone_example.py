# examples/db_standalone_example.py
"""
独立数据库模块使用示例
演示如何在其他项目中独立使用db模块
"""

import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.db import transactional, with_db_session, initialize_databases
from src.db.models import BaseModel
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import Session
from src.config.logging_config import setup_logger
from loguru import logger

# 设置日志
setup_logger()

# 自定义模型（在独立项目中，这将是你的项目模型）
class User(BaseModel):
    __tablename__ = 'users'
    
    name = Column(String(50), index=True)
    email = Column(String(100), unique=True, index=True)
    
    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at is not None else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at is not None else None
        }

# 数据库配置（在独立项目中，这将是你的项目配置）
DATABASE_CONFIG = {
    "default": "sqlite:///./standalone_example.db",
}

# 初始化数据库
initialize_databases(config=DATABASE_CONFIG)

@transactional("default")
def create_user(db: Session, name: str, email: str):
    """创建用户"""
    user = User.create(db, name=name, email=email)
    logger.info(f"创建用户: {user}")
    return user.id

@with_db_session("default")
def list_users(db: Session):
    """列出所有用户"""
    users = User.get_all(db)
    logger.info("所有用户:")
    for user in users:
        logger.info(f"  {user.to_dict()}")
    return users

def main():
    """主函数"""
    logger.info("=== 独立数据库模块使用示例 ===\n")
    
    # 创建用户
    logger.info("1. 创建用户:")
    try:
        user1_id = create_user("Alice", "alice@example.com")
        user2_id = create_user("Bob", "bob@example.com")
    except Exception as e:
        logger.error(f"创建用户时出错: {e}")
        return
    
    logger.info("")
    
    # 列出所有用户
    logger.info("2. 列出所有用户:")
    list_users()

if __name__ == "__main__":
    main()