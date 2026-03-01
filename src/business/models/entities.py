"""业务实体定义

使用Pydantic定义业务数据模型，提供数据验证和序列化功能。
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator, ValidationError
from enum import Enum


class DataStatus(str, Enum):
    """数据状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DataRecord(BaseModel):
    """原始数据记录模型"""
    
    id: Optional[str] = Field(None, description="记录ID")
    name: str = Field(..., description="记录名称")
    value: float = Field(..., description="数值")
    category: str = Field(..., description="分类")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")
    status: DataStatus = Field(default=DataStatus.PENDING, description="状态")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="元数据")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, value: str) -> str:
        """验证名称"""
        if not value or not value.strip():
            raise ValueError('名称不能为空')
        return value.strip()
    
    @field_validator('value')
    @classmethod
    def validate_value(cls, value: float) -> float:
        """验证数值"""
        if value < 0:
            raise ValueError('数值不能为负数')
        return value
    
    def __str__(self) -> str:
        return f"DataRecord(id={self.id}, name='{self.name}', value={self.value})"


class ProcessedData(BaseModel):
    """处理后的数据模型"""
    
    id: str = Field(..., description="处理后数据ID")
    original_id: str = Field(..., description="原始数据ID")
    name: str = Field(..., description="记录名称")
    original_value: float = Field(..., description="原始数值")
    processed_value: float = Field(..., description="处理后数值")
    category: str = Field(..., description="分类")
    processing_type: str = Field(..., description="处理类型")
    timestamp: datetime = Field(default_factory=datetime.now, description="处理时间")
    status: DataStatus = Field(default=DataStatus.COMPLETED, description="状态")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="处理元数据")
    
    def __str__(self) -> str:
        return (f"ProcessedData(id={self.id}, name='{self.name}', "
                f"processed_value={self.processed_value})")


class AnalysisResult(BaseModel):
    """分析结果模型"""
    
    id: str = Field(..., description="结果ID")
    analysis_type: str = Field(..., description="分析类型")
    input_data_ids: List[str] = Field(default_factory=list, description="输入数据ID列表")
    result_data: Dict[str, Any] = Field(default_factory=dict, description="分析结果数据")
    statistics: Optional[Dict[str, Any]] = Field(default=None, description="统计信息")
    timestamp: datetime = Field(default_factory=datetime.now, description="分析时间")
    duration: Optional[float] = Field(default=None, description="分析耗时(秒)")
    status: DataStatus = Field(default=DataStatus.COMPLETED, description="状态")
    
    def __str__(self) -> str:
        return (f"AnalysisResult(id={self.id}, type='{self.analysis_type}', "
                f"records={len(self.input_data_ids)})")


class ValidationResult:
    """数据验证结果"""
    
    def __init__(self, is_valid: bool, errors: Optional[List[str]] = None):
        self.is_valid = is_valid
        self.errors = errors or []
    
    def __bool__(self) -> bool:
        return self.is_valid
    
    def __str__(self) -> str:
        if self.is_valid:
            return "验证通过"
        return f"验证失败: {', '.join(self.errors)}"


class DataValidator:
    """数据验证器"""
    
    @staticmethod
    def validate_data_record(data: dict) -> ValidationResult:
        """验证数据记录"""
        try:
            DataRecord(**data)
            return ValidationResult(is_valid=True)
        except ValidationError as e:
            errors = [f"{error['loc'][0]}: {error['msg']}" for error in e.errors()]
            return ValidationResult(is_valid=False, errors=errors)
        except Exception as e:
            return ValidationResult(is_valid=False, errors=[str(e)])
    
    @staticmethod
    def validate_processed_data(data: dict) -> ValidationResult:
        """验证处理后的数据"""
        try:
            ProcessedData(**data)
            return ValidationResult(is_valid=True)
        except ValidationError as e:
            errors = [f"{error['loc'][0]}: {error['msg']}" for error in e.errors()]
            return ValidationResult(is_valid=False, errors=errors)
        except Exception as e:
            return ValidationResult(is_valid=False, errors=[str(e)])
    
    @staticmethod
    def validate_analysis_result(data: dict) -> ValidationResult:
        """验证分析结果"""
        try:
            AnalysisResult(**data)
            return ValidationResult(is_valid=True)
        except ValidationError as e:
            errors = [f"{error['loc'][0]}: {error['msg']}" for error in e.errors()]
            return ValidationResult(is_valid=False, errors=errors)
        except Exception as e:
            return ValidationResult(is_valid=False, errors=[str(e)])


#全局数据验证器实例
_data_validator = DataValidator()


def get_data_validator() -> DataValidator:
    """获取全局数据验证器实例
    
    Returns:
        DataValidator:数据验证器实例
    """
    return _data_validator