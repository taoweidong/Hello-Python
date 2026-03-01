"""业务逻辑测试

测试业务逻辑层的功能。
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from src.business.models import DataRecord, ProcessedData, AnalysisResult, get_data_validator
from src.business.services import get_analysis_service, get_data_processing_service
from src.business.repositories import get_data_repository
from src.business.processors import get_data_processor, get_processing_pipeline


class TestBusinessModels:
    """业务模型测试"""
    
    def test_data_record_creation(self):
        """测试数据记录创建"""
        record = DataRecord(
            name="测试记录",
            value=100.0,
            category="测试分类"
        )
        assert record.name == "测试记录"
        assert record.value == 100.0
        assert record.category == "测试分类"
    
    def test_data_record_validation(self):
        """测试数据记录验证"""
        validator = get_data_validator()
        
        # 有效数据
        valid_data = {
            "name": "测试",
            "value": 50.0,
            "category": "测试"
        }
        result = validator.validate_data_record(valid_data)
        assert result.is_valid
        
        # 无效数据
        invalid_data = {
            "name": "",
            "value": -10.0,
            "category": "测试"
        }
        result = validator.validate_data_record(invalid_data)
        assert not result.is_valid


class TestBusinessServices:
    """业务服务测试"""
    
    def test_analysis_service_creation(self):
        """测试分析服务创建"""
        service = get_analysis_service()
        assert service is not None
    
    def test_data_processing_service_creation(self):
        """测试数据处理服务创建"""
        service = get_data_processing_service()
        assert service is not None


class TestBusinessRepositories:
    """业务仓库测试"""
    
    def test_data_repository_creation(self):
        """测试数据仓库创建"""
        repository = get_data_repository()
        assert repository is not None


class TestBusinessProcessors:
    """业务处理器测试"""
    
    def test_data_processor_creation(self):
        """测试数据处理器创建"""
        processor = get_data_processor()
        assert processor is not None
    
    def test_processing_pipeline_creation(self):
        """测试处理管道创建"""
        pipeline = get_processing_pipeline()
        assert pipeline is not None