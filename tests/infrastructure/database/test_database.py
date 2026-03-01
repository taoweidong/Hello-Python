# tests/infrastructure/database/test_database.py
"""
数据库基础设施模块测试
测试独立的数据库操作库功能
"""

import unittest
import tempfile
import os
from sqlalchemy.orm import Session
from src.infrastructure.database import DatabaseManager, transactional, with_db_session
from src.infrastructure.database.example_models import User, Product

class TestDatabaseInfrastructure(unittest.TestCase):
    """数据库基础设施功能测试"""
    
    def setUp(self):
        """测试前准备"""
        # 创建临时数据库
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()
        self.db_url = f"sqlite:///{self.temp_db.name}"
        
        # 创建数据库管理器
        self.db_manager = DatabaseManager(self.db_url)
        
        # 创建表
        self.db_manager.create_tables()
    
    def tearDown(self):
        """测试后清理"""
        #确关闭所有数据库连接
        self.db_manager.get_engine().dispose()
        #等待一段时间让文件解锁
        import time
        time.sleep(0.1)
        # 删除临时数据库文件
        if os.path.exists(self.temp_db.name):
            try:
                os.unlink(self.temp_db.name)
            except PermissionError:
                # 如果删除失败，标记文件在下次重启时删除
                pass
    
    def test_database_manager_creation(self):
        """测试数据库管理器创建"""
        db_manager = DatabaseManager()
        self.assertIsNotNone(db_manager.get_engine())
        self.assertIsNotNone(db_manager.get_session_factory())
    
    def test_create_user(self):
        """测试创建用户"""
        with self.db_manager.get_db_session() as db:
            user = User.create(db, name="Alice", email="alice@example.com", age=25)
            self.assertIsNotNone(user.id)
            self.assertEqual(user.name, "Alice")
            self.assertEqual(user.email, "alice@example.com")
            self.assertEqual(user.age, 25)
    
    def test_get_user_by_id(self):
        """测试根据ID获取用户"""
        with self.db_manager.get_db_session() as db:
            #先创建用户
            created_user = User.create(db, name="Bob", email="bob@example.com", age=30)
            
            # 获取用户ID
            user_id = created_user.id
            
            #再获取用户
            user = User.get_by_id(db, user_id)
            self.assertIsNotNone(user)
            self.assertEqual(user.name, "Bob")
            self.assertEqual(user.email, "bob@example.com")
            self.assertEqual(user.age, 30)
    
    def test_get_all_users(self):
        """测试获取所有用户"""
        with self.db_manager.get_db_session() as db:
            # 创建多个用户
            User.create(db, name="Alice", email="alice@example.com", age=25)
            User.create(db, name="Bob", email="bob@example.com", age=30)
            User.create(db, name="Charlie", email="charlie@example.com", age=35)
            
            # 获取所有用户
            users = User.get_all(db)
            self.assertEqual(len(users), 3)
    
    def test_update_user(self):
        """测试更新用户"""
        with self.db_manager.get_db_session() as db:
            #先创建用户
            user = User.create(db, name="Alice", email="alice@example.com", age=25)
            
            # 获取用户ID
            user_id = user.id
            
            # 更新用户
            updated_user = User.update(db, user_id, name="Alice Smith", age=26)
            self.assertIsNotNone(updated_user)
            self.assertEqual(updated_user.name, "Alice Smith")
            self.assertEqual(updated_user.age, 26)
    
    def test_delete_user(self):
        """测试删除用户"""
        with self.db_manager.get_db_session() as db:
            # 先创建用户
            user = User.create(db, name="Alice", email="alice@example.com", age=25)
            
            # 获取用户ID
            user_id = user.id
            
            # 删除用户
            result = User.delete(db, user_id)
            self.assertTrue(result)
            
            #确用户已删除
            deleted_user = User.get_by_id(db, user_id)
            self.assertIsNone(deleted_user)
    
    def test_filter_users(self):
        """测试过滤用户"""
        with self.db_manager.get_db_session() as db:
            # 创建多个用户
            User.create(db, name="Alice", email="alice@example.com", age=25)
            User.create(db, name="Bob", email="bob@example.com", age=30)
            User.create(db, name="Alice2", email="alice2@example.com", age=28)
            
            #过滤用户
            users = User.filter(db, name="Alice")
            self.assertEqual(len(users), 1)
            self.assertEqual(users[0].name, "Alice")
            
            #根据年龄过滤
            users = User.filter(db, age=25)
            self.assertEqual(len(users), 1)
            self.assertEqual(users[0].age, 25)
    
    def test_database_connection_failure(self):
        """测试数据库连接失败"""
        # 使用无效的数据库URL
        invalid_db_manager = DatabaseManager("sqlite:///invalid_path/does_not_exist.db")
        
        # 测试连接失败
        result = invalid_db_manager.test_connection()
        self.assertFalse(result)
    
    def test_database_session_exception_handling(self):
        """测试数据库会话异常处理"""
        with self.db_manager.get_db_session() as db:
            # 创建一个用户
            user = User.create(db, name="Test", email="test@example.com", age=25)
            user_id = user.id
        
        # 测试获取不存在的用户（应该返回None而不是抛出异常）
        with self.db_manager.get_db_session() as db:
            non_existent_user = User.get_by_id(db, 999999)
            self.assertIsNone(non_existent_user)
    
    def test_database_transaction_rollback(self):
        """测试数据库事务回滚"""
        # 测试装饰器的事务回滚功能
        @transactional()
        def failing_operation(db: Session):
            # 创建一个用户
            user = User.create(db, name="WillFail", email="fail@example.com", age=25)
            # 故意引发异常
            raise Exception("测试事务回滚")
            return user
        
        # 执行会失败的操作
        with self.assertRaises(Exception):
            with self.db_manager.get_db_session() as db:
                failing_operation(db)
        
        # 验证用户没有被创建（事务已回滚）
        with self.db_manager.get_db_session() as db:
            users = User.filter(db, name="WillFail")
            self.assertEqual(len(users), 0)

if __name__ == '__main__':
    unittest.main()
