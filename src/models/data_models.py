"""数据模型模块

定义应用程序使用的数据模型，包括用户数据和处理后的数据。
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ValidationError


class DataValidationError(Exception):
    """数据验证错误异常"""
    pass


class UserData(BaseModel):
    """用户数据模型"""
    
    name: str = Field(..., description="用户姓名")
    age: int = Field(..., ge=0, le=150, description="用户年龄")
    city: str = Field(..., description="用户所在城市")
    processed: Optional[bool] = Field(default=False, description="是否已处理")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, value: str) -> str:
        """验证用户姓名
        
        Args:
            value:值
            
        Returns:
            str: 验证后的姓名
            
        Raises:
            ValueError:为空时
        """
        if not value or not value.strip():
            raise ValueError('姓名不能为空')
        return value.strip()
    
    @field_validator('city')
    @classmethod
    def validate_city(cls, value: str) -> str:
        """验证城市
        
        Args:
            value:值
            
        Returns:
            str:验证后的城市
            
        Raises:
            ValueError:为空时
        """
        if not value or not value.strip():
            raise ValueError('城市不能为空')
        return value.strip()
    
    def __str__(self) -> str:
        """返回用户数据的字符串表示
        
        Returns:
            str: 用户数据字符串
        """
        return f"UserData(name='{self.name}', age={self.age}, city='{self.city}')"


class ProcessedUserData(UserData):
    """处理后的用户数据模型"""
    
    processed: Optional[bool] = Field(default=True, description="是否已处理")
    processed_at: datetime = Field(default_factory=datetime.now, description="处理时间")
    
    def __str__(self) -> str:
        """返回处理后用户数据的字符串表示
        
        Returns:
            str:处理后用户数据字符串
        """
        return (f"ProcessedUserData(name='{self.name}', age={self.age}, "
                f"city='{self.city}', processed_at='{self.processed_at}')")


class DataValidationResult:
    """数据验证结果"""
    
    def __init__(self, is_valid: bool, errors: Optional[list] = None) -> None:
        """初始化验证结果
        
        Args:
            is_valid: 是否有效
            errors:错误列表
        """
        self.is_valid: bool = is_valid
        self.errors: list = errors or []
    
    def __bool__(self) -> bool:
        """返回验证结果的布尔值
        
        Returns:
            bool:验证是否通过
        """
        return self.is_valid
    
    def __str__(self) -> str:
        """返回验证结果的字符串表示
        
        Returns:
            str:验证结果字符串
        """
        if self.is_valid:
            return "验证通过"
        return f"验证失败: {', '.join(self.errors)}"


class DataValidator:
    """数据验证器
    
   验证用户数据的完整性和正确性。
    """
    
    @staticmethod
    def validate_user_data(data: dict) -> DataValidationResult:
        """验证用户数据
        
        Args:
            data: 用户数据字典
            
        Returns:
            DataValidationResult: 验证结果
        """
        try:
            user_data = UserData(**data)
            return DataValidationResult(is_valid=True)
        except ValidationError as e:
            errors = [f"{error['loc'][0]}: {error['msg']}" for error in e.errors()]
            return DataValidationResult(is_valid=False, errors=errors)
        except Exception as e:
            return DataValidationResult(is_valid=False, errors=[str(e)])
    
    @staticmethod
    def validate_processed_data(data: dict) -> DataValidationResult:
        """验证处理后的数据
        
        Args:
            data:处理后的数据字典
            
        Returns:
            DataValidationResult: 验证结果
        """
        try:
            processed_data = ProcessedUserData(**data)
            return DataValidationResult(is_valid=True)
        except ValidationError as e:
            errors = [f"{error['loc'][0]}: {error['msg']}" for error in e.errors()]
            return DataValidationResult(is_valid=False, errors=errors)
        except Exception as e:
            return DataValidationResult(is_valid=False, errors=[str(e)])


# 创建全局数据验证器实例
_data_validator = DataValidator()


def get_data_validator() -> DataValidator:
    """获取全局数据验证器实例
    
    Returns:
        DataValidator: 数据验证器实例
    """
    return _data_validator