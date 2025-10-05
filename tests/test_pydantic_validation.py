# tests/test_pydantic_validation.py
import unittest
from pydantic import ValidationError
from src.models import UserData, ProcessedUserData

class TestPydanticValidation(unittest.TestCase):
    """测试Pydantic数据校验功能"""
    
    def test_valid_user_data(self):
        """测试有效的用户数据"""
        user_data = UserData(
            name="Alice",
            age=25,
            city="New York"
        )
        self.assertEqual(user_data.name, "Alice")
        self.assertEqual(user_data.age, 25)
        self.assertEqual(user_data.city, "New York")
        self.assertFalse(user_data.processed)
    
    def test_invalid_age(self):
        """测试无效的年龄"""
        with self.assertRaises(ValidationError):
            UserData(
                name="Bob",
                age=-5,  # 无效年龄
                city="London"
            )
        
        with self.assertRaises(ValidationError):
            UserData(
                name="Charlie",
                age=200,  # 超出最大年龄
                city="Tokyo"
            )
    
    def test_empty_name(self):
        """测试空姓名"""
        with self.assertRaises(ValidationError):
            UserData(
                name="",  # 空姓名
                age=30,
                city="Paris"
            )
    
    def test_empty_city(self):
        """测试空城市"""
        with self.assertRaises(ValidationError):
            UserData(
                name="David",
                age=35,
                city=""  # 空城市
            )
    
    def test_processed_user_data(self):
        """测试处理后的用户数据"""
        processed_user = ProcessedUserData(
            name="Eve",
            age=28,
            city="Berlin"
        )
        self.assertEqual(processed_user.name, "Eve")
        self.assertEqual(processed_user.age, 28)
        self.assertEqual(processed_user.city, "Berlin")
        self.assertTrue(processed_user.processed)
        # 检查是否自动设置了处理时间
        self.assertIsNotNone(processed_user.processed_at)

if __name__ == '__main__':
    unittest.main()