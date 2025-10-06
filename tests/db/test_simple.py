# tests/db/test_simple.py
"""
数据库操作库简单测试
测试封装的数据库基本功能
"""

import unittest
import tempfile
import os
from src.db import DatabaseManager
from src.db.example_models import User, Product

class TestDatabaseSimple(unittest.TestCase):
    """数据库功能简单测试"""
    
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
        # 确保关闭所有数据库连接
        self.db_manager.get_engine().dispose()
        # 删除临时数据库文件
        if os.path.exists(self.temp_db.name):
            try:
                os.unlink(self.temp_db.name)
            except PermissionError:
                pass
    
    def test_database_manager_creation(self):
        """测试数据库管理器创建"""
        db_manager = DatabaseManager()
        self.assertIsNotNone(db_manager.get_engine())
        self.assertIsNotNone(db_manager.get_session_factory())
    
    def test_create_and_query_user(self):
        """测试创建和查询用户"""
        with self.db_manager.get_db_session() as db:
            # 创建用户
            user = User.create(db, name="Alice", email="alice@example.com", age=25)
            
            self.assertIsNotNone(user.id)
            self.assertEqual(user.name, "Alice")
            self.assertEqual(user.email, "alice@example.com")
            self.assertEqual(user.age, 25)
            
            # 查询用户
            user_id = int(user.id)
            queried_user = User.get_by_id(db, user_id)
            self.assertIsNotNone(queried_user)
            self.assertEqual(queried_user.name, "Alice")
            self.assertEqual(queried_user.email, "alice@example.com")
            self.assertEqual(queried_user.age, 25)

if __name__ == '__main__':
    unittest.main()