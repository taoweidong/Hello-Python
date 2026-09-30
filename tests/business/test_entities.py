"""业务实体与验证器测试"""

import pytest
from pydantic import ValidationError

from src.business.models import (
    AnalysisResult,
    DataRecord,
    DataStatus,
    ProcessedData,
    ValidationResult,
    get_data_validator,
)


class TestDataRecord:
    """数据记录模型测试"""

    def test_name_is_stripped(self):
        record = DataRecord(name="  Alice  ", value=1.0, category="sales")
        assert record.name == "Alice"

    def test_blank_name_rejected(self):
        with pytest.raises(ValidationError):
            DataRecord(name="   ", value=1.0, category="sales")

    def test_negative_value_rejected(self):
        with pytest.raises(ValidationError):
            DataRecord(name="bad", value=-1.0, category="sales")

    def test_defaults(self):
        record = DataRecord(name="ok", value=1.0, category="sales")
        assert record.status == DataStatus.PENDING
        assert record.id is None
        assert record.timestamp is not None

    def test_str(self):
        record = DataRecord(name="ok", value=2.5, category="sales")
        assert "ok" in str(record)
        assert "2.5" in str(record)


class TestProcessedData:
    """处理后数据模型测试"""

    def test_defaults_and_str(self):
        data = ProcessedData(
            id="p1",
            original_id="o1",
            name="ok",
            original_value=10.0,
            processed_value=1.0,
            category="sales",
            processing_type="normalization",
        )
        assert data.status == DataStatus.COMPLETED
        assert "p1" in str(data)


class TestAnalysisResult:
    """分析结果模型测试"""

    def test_defaults_and_str(self):
        result = AnalysisResult(id="a1", analysis_type="statistical")
        assert result.status == DataStatus.COMPLETED
        assert result.input_data_ids == []
        assert result.result_data == {}
        assert "statistical" in str(result)


class TestValidationResult:
    """验证结果对象测试"""

    def test_bool_and_str(self):
        valid = ValidationResult(is_valid=True)
        assert bool(valid) is True
        assert str(valid) == "验证通过"

        invalid = ValidationResult(is_valid=False, errors=["name: 不能为空"])
        assert bool(invalid) is False
        assert "验证失败" in str(invalid)


class TestDataValidator:
    """数据验证器测试"""

    def setup_method(self):
        self.validator = get_data_validator()

    def test_valid_record(self):
        result = self.validator.validate_data_record({"name": "Alice", "value": 1.0, "category": "sales"})
        assert result.is_valid is True
        assert result.errors == []

    def test_invalid_record_reports_field_errors(self):
        result = self.validator.validate_data_record({"name": "", "value": -1.0, "category": "sales"})
        assert result.is_valid is False
        assert len(result.errors) >= 1

    def test_non_dict_input_rejected(self):
        """非字典输入走通用异常分支，返回失败结果而非抛异常"""
        result = self.validator.validate_data_record(None)  # type: ignore[arg-type]
        assert result.is_valid is False

    def test_valid_processed_data(self):
        data = {
            "id": "p1",
            "original_id": "o1",
            "name": "ok",
            "original_value": 10.0,
            "processed_value": 1.0,
            "category": "sales",
            "processing_type": "normalization",
        }
        assert self.validator.validate_processed_data(data).is_valid is True
        assert self.validator.validate_processed_data({"id": "p1"}).is_valid is False

    def test_valid_analysis_result(self):
        data = {"id": "a1", "analysis_type": "statistical"}
        assert self.validator.validate_analysis_result(data).is_valid is True
        assert self.validator.validate_analysis_result({"id": "a1"}).is_valid is False
