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
from src.db.example_models import User, Product, Order
from src.config.logging_config import setup_logger
from loguru import logger
from sqlalchemy.orm import Session

# 设置日志
setup_logger()

# 创建数据库管理器实例
db_manager = DatabaseManager("sqlite:///./example.db")

def setup_database():
    """设置数据库"""
    # 创建表
    db_manager.create_tables()
    logger.info("数据库表已创建")

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
    logger.info(f"创建用户: {user}")
    
    # 创建产品
    product = Product.create(db, name=product_name, price=product_price, description="示例产品")
    logger.info(f"创建产品: {product}")
    
    return user.id, product.id

@transactional
def create_order(db: Session, user_id: int, product_id: int, quantity: int = 1):
    """
    创建订单
    
    Args:
        db: 数据库会话
        user_id: 用户ID
        product_id: 产品ID
        quantity: 数量
    """
    # 获取用户和产品
    user = User.get_by_id(db, user_id)
    product = Product.get_by_id(db, product_id)
    
    if not user or not product:
        logger.error("用户或产品不存在")
        return None
    
    # 计算总价
    total_price = product.price * quantity
    
    # 创建订单
    order = Order.create(db, user_id=user_id, product_id=product_id, quantity=quantity, total_price=total_price)
    logger.info(f"创建订单: {order}")
    
    return order.id

def list_users():
    """列出所有用户"""
    with db_manager.get_db_session() as db:
        users = User.get_all(db)
        logger.info("所有用户:")
        for user in users:
            logger.info(f"  {user.to_dict()}")
        return users

def list_products():
    """列出所有产品"""
    with db_manager.get_db_session() as db:
        products = Product.get_all(db)
        logger.info("所有产品:")
        for product in products:
            logger.info(f"  {product.to_dict()}")
        return products

def list_orders():
    """列出所有订单"""
    with db_manager.get_db_session() as db:
        orders = Order.get_all(db)
        logger.info("所有订单:")
        for order in orders:
            logger.info(f"  {order.to_dict()}")
        return orders

def update_user(user_id: int, **kwargs):
    """更新用户"""
    with db_manager.get_db_session() as db:
        user = User.update(db, user_id, **kwargs)
        if user:
            logger.info(f"更新用户: {user.to_dict()}")
        else:
            logger.warning(f"未找到ID为{user_id}的用户")
        return user

def delete_user(user_id: int):
    """删除用户"""
    with db_manager.get_db_session() as db:
        result = User.delete(db, user_id)
        if result:
            logger.info(f"已删除ID为{user_id}的用户")
        else:
            logger.warning(f"未找到ID为{user_id}的用户")
        return result

def find_users_by_email(email: str):
    """根据邮箱查找用户"""
    with db_manager.get_db_session() as db:
        users = User.filter(db, email=email)
        logger.info(f"邮箱为{email}的用户:")
        for user in users:
            logger.info(f"  {user.to_dict()}")
        return users

def demonstrate_joins():
    """演示关联查询"""
    logger.info("=== 关联查询示例 ===")
    
    with db_manager.get_db_session() as db:
        # 查询订单及其关联的用户和产品信息
        orders = db.query(Order).all()
        
        logger.info("订单详情（包含用户和产品信息）:")
        for order in orders:
            # 通过关系属性访问关联对象
            user = order.user
            product = order.product
            
            logger.info(f"  订单ID: {order.id}")
            logger.info(f"    用户: {user.name} ({user.email})")
            logger.info(f"    产品: {product.name} (¥{product.price/100:.2f})")
            logger.info(f"    数量: {order.quantity}")
            logger.info(f"    总价: ¥{order.total_price/100:.2f}")
            logger.info("")

def main():
    """主函数"""
    logger.info("=== 数据库操作库使用示例 ===\n")
    
    # 设置数据库
    setup_database()
    
    # 创建用户和产品
    logger.info("1. 创建用户和产品:")
    with db_manager.get_db_session() as db:
        try:
            user_id, product_id = create_user_and_product(db, "Alice", "alice@example.com", "Python书籍", 5999)
        except Exception as e:
            logger.error(f"创建用户和产品时出错: {e}")
            return
    
    logger.info("")
    
    # 创建订单
    logger.info("2. 创建订单:")
    with db_manager.get_db_session() as db:
        try:
            order_id = create_order(db, user_id, product_id, 2)
        except Exception as e:
            logger.error(f"创建订单时出错: {e}")
            return
    
    logger.info("")
    
    # 列出所有用户、产品和订单
    logger.info("3. 列出所有数据:")
    list_users()
    list_products()
    list_orders()
    
    logger.info("")
    
    # 演示关联查询
    logger.info("4. 演示关联查询:")
    demonstrate_joins()
    
    logger.info("")
    
    # 更新用户
    logger.info("5. 更新用户:")
    update_user(user_id, age=26, name="Alice Smith")
    
    logger.info("")
    
    # 根据邮箱查找用户
    logger.info("6. 根据邮箱查找用户:")
    find_users_by_email("alice@example.com")
    
    logger.info("")
    
    # 创建另一个用户
    logger.info("7. 创建另一个用户:")
    with db_manager.get_db_session() as db:
        try:
            user2_id, product2_id = create_user_and_product(db, "Bob", "bob@example.com", "Java书籍", 6999)
            # 为第二个用户创建订单
            create_order(db, user2_id, product2_id, 1)
        except Exception as e:
            logger.error(f"创建用户时出错: {e}")
            return
    
    logger.info("")
    
    # 列出所有数据
    logger.info("8. 列出所有数据:")
    list_users()
    list_products()
    list_orders()
    
    logger.info("")
    
    # 演示关联查询
    logger.info("9. 演示关联查询:")
    demonstrate_joins()

if __name__ == "__main__":
    main()