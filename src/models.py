# src/models.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

class UserData(BaseModel):
    """用户数据模型"""
    name: str = Field(..., description="用户姓名")
    age: int = Field(..., ge=0, le=150, description="用户年龄")
    city: str = Field(..., description="用户所在城市")
    processed: Optional[bool] = Field(default=False, description="是否已处理")
    
    @field_validator('name')
    def name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('姓名不能为空')
        return v.strip()
    
    @field_validator('city')
    def city_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('城市不能为空')
        return v.strip()

class ProcessedUserData(UserData):
    """处理后的用户数据模型"""
    processed: Optional[bool] = Field(default=True, description="是否已处理")
    processed_at: datetime = Field(default_factory=datetime.now, description="处理时间")