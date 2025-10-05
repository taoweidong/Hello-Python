# tests/test_database.py
import unittest
import tempfile
import os
from sqlalchemy.orm import Session
from src.database import User, engine, Base, get_db
from src.database_service import create_user, get_users, get_user_by_id, update_user, delete_user
from src.models import UserData

class TestDatabase(unittest.TestCase):
    def setUp(self):
        # 创建临时数据库用于测试
        self.test_db_url = "sqlite:///./test_db.db"
        self.test_engine = engine
        Base.metadata.create_all(bind=self.test_engine)
        
    def tearDown(self):
        # 清理测试数据
        Base.metadata.drop_all(bind=self.test_engine)
        # 删除测试数据库文件
        if os.path.exists("./test_db.db"):
            os.remove("./test_db.db")
    
    def test_create_user(self):
        """测试创建用户"""
        # 获取数据库会话
        db_gen = get_db()
        db = next(db_gen)
        
        # 创建用户数据
        user_data = UserData(
            name="Alice",
            age=25,
            city="New York"
        )
        
        # 创建用户
        user = create_user(db, user_data)
        
        # 验证用户创建成功
        self.assertIsNotNone(user.id)
        self.assertEqual(user.name, "Alice")
        self.assertEqual(user.age, 25)
        self.assertEqual(user.city, "New York")
        
    def test_get_users(self):
        """测试获取用户列表"""
        # 获取数据库会话
        db_gen = get_db()
        db = next(db_gen)
        
        # 创建几个用户
        user1 = UserData(name="Alice", age=25, city="New York")
        user2 = UserData(name="Bob", age=30, city="London")
        
        create_user(db, user1)
        create_user(db, user2)
        
        # 获取用户列表
        users = get_users(db)
        
        # 验证用户列表
        self.assertEqual(len(users), 2)
        self.assertEqual(users[0].name, "Alice")
        self.assertEqual(users[1].name, "Bob")
        
    def test_get_user_by_id(self):
        """测试根据ID获取用户"""
        # 获取数据库会话
        db_gen = get_db()
        db = next(db_gen)
        
        # 创建用户
        user_data = UserData(name="Charlie", age=35, city="Tokyo")
        created_user = create_user(db, user_data)
        
        # 根据ID获取用户
        user = get_user_by_id(db, int(created_user.id))
        
        # 验证用户
        self.assertIsNotNone(user)
        self.assertEqual(user.name, "Charlie")
        self.assertEqual(user.age, 35)
        self.assertEqual(user.city, "Tokyo")
        
    def test_update_user(self):
        """测试更新用户"""
        # 获取数据库会话
        db_gen = get_db()
        db = next(db_gen)
        
        # 创建用户
        user_data = UserData(name="David", age=40, city="Paris")
        created_user = create_user(db, user_data)
        
        # 更新用户数据
        updated_data = UserData(name="David Smith", age=41, city="Berlin")
        updated_user = update_user(db, int(created_user.id), updated_data)
        
        # 验证更新
        self.assertIsNotNone(updated_user)
        self.assertEqual(updated_user.name, "David Smith")
        self.assertEqual(updated_user.age, 41)
        self.assertEqual(updated_user.city, "Berlin")
        
    def test_delete_user(self):
        """测试删除用户"""
        # 获取数据库会话
        db_gen = get_db()
        db = next(db_gen)
        
        # 创建用户
        user_data = UserData(name="Eve", age=28, city="Sydney")
        created_user = create_user(db, user_data)
        
        # 删除用户
        deleted_user = delete_user(db, int(created_user.id))
        
        # 验证删除
        self.assertIsNotNone(deleted_user)
        
        # 确认用户已删除
        user = get_user_by_id(db, int(created_user.id))
        self.assertIsNone(user)

if __name__ == '__main__':
    unittest.main()