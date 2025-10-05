# examples/db_example.py
"""
数据库操作库使用示例
演示如何使用封装的数据库功能
"""

import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.db import DatabaseManager, transactional, with_db_session, CRUDMixin
from src.db.example_models import User, Product
from sqlalchemy.orm import Session

# 创建数据库管理器实例
db_manager = DatabaseManager("sqlite:///./example.db")

def setup_database():
    """设置数据库"""
    # 创建表
    db_manager.create_tables()
    print("数据库表已创建")

@transactional
def create_user_and_product(db: Session, user_name: str, user_email: str, product_name: str, product_price: int):
    """
    创建用户和产品（在同一个事务中）
    
    Args:
        db: 数据库会话
        user_name: 用户名
        user_email: 用户邮箱
        product_name: 产品名
        product_price: 产品价格
    """
    # 创建用户
    user = User.create(db, name=user_name, email=user_email, age=25)
    print(f"创建用户: {user}")
    
    # 创建产品
    product = Product.create(db, name=product_name, price=product_price, description="示例产品")
    print(f"创建产品: {product}")
    
    return user.id, product.id

def list_users():
    """列出所有用户"""
    with db_manager.get_db_session() as db:
        users = User.get_all(db)
        print("所有用户:")
        for user in users:
            print(f"  {user.to_dict()}")
        return users

def list_products():
    """列出所有产品"""
    with db_manager.get_db_session() as db:
        products = Product.get_all(db)
        print("所有产品:")
        for product in products:
            print(f"  {product.to_dict()}")
        return products

def update_user(user_id: int, **kwargs):
    """更新用户"""
    with db_manager.get_db_session() as db:
        user = User.update(db, user_id, **kwargs)
        if user:
            print(f"更新用户: {user.to_dict()}")
        else:
            print(f"未找到ID为{user_id}的用户")
        return user

def delete_user(user_id: int):
    """删除用户"""
    with db_manager.get_db_session() as db:
        result = User.delete(db, user_id)
        if result:
            print(f"已删除ID为{user_id}的用户")
        else:
            print(f"未找到ID为{user_id}的用户")
        return result

def find_users_by_email(email: str):
    """根据邮箱查找用户"""
    with db_manager.get_db_session() as db:
        users = User.filter(db, email=email)
        print(f"邮箱为{email}的用户:")
        for user in users:
            print(f"  {user.to_dict()}")
        return users

def main():
    """主函数"""
    print("=== 数据库操作库使用示例 ===\n")
    
    # 设置数据库
    setup_database()
    
    # 创建用户和产品
    print("1. 创建用户和产品:")
    with db_manager.get_db_session() as db:
        try:
            user_id, product_id = create_user_and_product(db, "Alice", "alice@example.com", "Python书籍", 5999)
        except Exception as e:
            print(f"创建用户和产品时出错: {e}")
            return
    
    print()
    
    # 列出所有用户和产品
    print("2. 列出所有用户和产品:")
    list_users()
    list_products()
    
    print()
    
    # 更新用户
    print("3. 更新用户:")
    update_user(user_id, age=26, name="Alice Smith")
    
    print()
    
    # 根据邮箱查找用户
    print("4. 根据邮箱查找用户:")
    find_users_by_email("alice@example.com")
    
    print()
    
    # 创建另一个用户
    print("5. 创建另一个用户:")
    with db_manager.get_db_session() as db:
        try:
            user2_id, _ = create_user_and_product(db, "Bob", "bob@example.com", "Java书籍", 6999)
        except Exception as e:
            print(f"创建用户时出错: {e}")
            return
    
    print()
    
    # 列出所有用户
    print("6. 列出所有用户:")
    list_users()
    
    print()
    
    # 删除用户
    print("7. 删除用户:")
    delete_user(user2_id)
    
    print()
    
    # 最终列出所有用户
    print("8. 最终用户列表:")
    list_users()

if __name__ == "__main__":
    main()