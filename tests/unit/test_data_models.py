"""数据模型测试"""

import pytest
from datetime import datetime
import sys
import os

# 添加fixtures路径
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "fixtures"))

from src.models.data_models import (
    UserData,
    ProcessedUserData,
    DataValidationError,
    DataValidationResult,
    DataValidator,
    get_data_validator
)

#导入fixtures
try:
    from test_data import sample_user_data, sample_processed_user_data, invalid_user_data
except ImportError:
    # 如果fixtures导入失败，创建本地fixtures
    @pytest.fixture
    def sample_user_data():
        return {
            'name': 'Alice',
            'age': 25,
            'city': 'New York'
        }
    
    @pytest.fixture
    def sample_processed_user_data():
        return {
            'name': 'Alice',
            'age': 25,
            'city': 'New York',
            'processed': True,
            'processed_at': '2024-01-01T12:00:00'
        }
    
    @pytest.fixture
    def invalid_user_data():
        return {
            'name': '',
            'age': -5,
            'city': '   '
        }


class TestDataModels:
    """数据模型测试"""
    
    def test_user_data_creation(self, sample_user_data):
        """测试用户数据创建"""
        user = UserData(**sample_user_data)
        assert user.name == "Alice"
        assert user.age == 25
        assert user.city == "New York"
        assert user.processed is False
    
    def test_user_data_validation_name_empty(self):
        """测试用户数据姓名验证 - 空值"""
        with pytest.raises(ValueError, match="姓名不能为空"):
            UserData(name="", age=25, city="New York")
    
    def test_user_data_validation_name_whitespace(self):
        """测试用户数据姓名验证 - 空白字符"""
        with pytest.raises(ValueError, match="姓名不能为空"):
            UserData(name="   ", age=25, city="New York")
    
    def test_user_data_validation_city_empty(self):
        """测试用户数据城市验证 -空值"""
        with pytest.raises(ValueError, match="城市不能为空"):
            UserData(name="Alice", age=25, city="")
    
    def test_user_data_validation_age_invalid(self):
        """测试用户数据年龄验证 - 无效值"""
        #年过小
        with pytest.raises(Exception):
            UserData(name="Alice", age=-1, city="New York")
        
        #年过大
        with pytest.raises(Exception):
            UserData(name="Alice", age=200, city="New York")
    
    def test_user_data_str_representation(self, sample_user_data):
        """测试用户数据字符串表示"""
        user = UserData(**sample_user_data)
        str_repr = str(user)
        assert "UserData" in str_repr
        assert "Alice" in str_repr
        assert "25" in str_repr
        assert "New York" in str_repr
    
    def test_processed_user_data_creation(self, sample_processed_user_data):
        """测试处理后用户数据创建"""
        processed_user = ProcessedUserData(**sample_processed_user_data)
        assert processed_user.name == "Alice"
        assert processed_user.age == 25
        assert processed_user.city == "New York"
        assert processed_user.processed is True
        assert processed_user.processed_at is not None
    
    def test_processed_user_data_default_processed(self, sample_user_data):
        """测试处理后用户数据默认processed值"""
        processed_user = ProcessedUserData(**sample_user_data)
        assert processed_user.processed is True  # 默认值应为True
    
    def test_processed_user_data_str_representation(self, sample_processed_user_data):
        """测试处理后用户数据字符串表示"""
        processed_user = ProcessedUserData(**sample_processed_user_data)
        str_repr = str(processed_user)
        assert "ProcessedUserData" in str_repr
        assert "Alice" in str_repr
        assert "25" in str_repr
        assert "New York" in str_repr


class TestDataValidationResult:
    """数据验证结果测试"""
    
    def test_validation_result_valid(self):
        """测试有效的验证结果"""
        result = DataValidationResult(is_valid=True)
        assert result.is_valid is True
        assert result.errors == []
        assert bool(result) is True
        assert str(result) == "验证通过"
    
    def test_validation_result_invalid(self):
        """测试无效的验证结果"""
        errors = ["姓名不能为空", "年龄无效"]
        result = DataValidationResult(is_valid=False, errors=errors)
        assert result.is_valid is False
        assert result.errors == errors
        assert bool(result) is False
        assert "验证失败" in str(result)
        assert "姓名不能为空" in str(result)
    
    def test_validation_result_empty_errors(self):
        """测试空错误列表的验证结果"""
        result = DataValidationResult(is_valid=False)
        assert result.is_valid is False
        assert result.errors == []
        assert bool(result) is False


class TestDataValidator:
    """数据验证器测试"""
    
    def test_validate_user_data_valid(self, sample_user_data):
        """测试验证有效的用户数据"""
        validator = DataValidator()
        result = validator.validate_user_data(sample_user_data)
        assert result.is_valid is True
        assert result.errors == []
    
    def test_validate_user_data_invalid(self, invalid_user_data):
        """测试验证无效的用户数据"""
        validator = DataValidator()
        result = validator.validate_user_data(invalid_user_data)
        assert result.is_valid is False
        assert len(result.errors) > 0
    
    def test_validate_processed_data_valid(self, sample_processed_user_data):
        """测试验证有效的处理后数据"""
        validator = DataValidator()
        result = validator.validate_processed_data(sample_processed_user_data)
        assert result.is_valid is True
        assert result.errors == []
    
    def test_validate_processed_data_invalid_datetime(self):
        """测试验证包含无效时间戳的处理后数据"""
        invalid_data = {
            'name': 'Alice',
            'age': 25,
            'city': 'New York',
            'processed': True,
            'processed_at': 'invalid_datetime'
        }
        validator = DataValidator()
        result = validator.validate_processed_data(invalid_data)
        assert result.is_valid is False
    
    def test_global_data_validator(self):
        """测试全局数据验证器"""
        validator1 = get_data_validator()
        validator2 = get_data_validator()
        assert validator1 is validator2
        assert isinstance(validator1, DataValidator)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])