"""数据处理服务测试"""

import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import Mock, patch
import sys
import os

# 添加fixtures路径
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "fixtures"))

from src.services.data_service import (
    DataProcessor,
    DataProcessingError,
    get_data_processor
)
from src.models.data_models import UserData, ProcessedUserData

#导入fixtures
try:
    from test_data import csv_test_data, empty_csv_file, malformed_csv_file, test_output_dir, sample_user_data
except ImportError:
    # 如果fixtures导入失败，创建本地fixtures
    import tempfile
    
    @pytest.fixture
    def csv_test_data():
        test_data = """name,age,city
Alice,25,New York
Bob,30,London
Charlie,35,Tokyo
Diana,28,Paris
Eve,32,Berlin"""
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8') as f:
            f.write(test_data)
            temp_file_path = f.name
        
        yield {
            'file_path': temp_file_path,
            'data': test_data,
            'row_count': 5
        }
        
        try:
            Path(temp_file_path).unlink()
        except FileNotFoundError:
            pass
    
    @pytest.fixture
    def empty_csv_file():
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8') as f:
            f.write("")
            temp_file_path = f.name
        
        yield temp_file_path
        
        try:
            Path(temp_file_path).unlink()
        except FileNotFoundError:
            pass
    
    @pytest.fixture
    def malformed_csv_file():
        malformed_data = """name,age,city
Alice,25,New York
Bob,30  #缺城市列
Charlie,35,Tokyo,extra"""  #多的列
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8') as f:
            f.write(malformed_data)
            temp_file_path = f.name
        
        yield temp_file_path
        
        try:
            Path(temp_file_path).unlink()
        except FileNotFoundError:
            pass
    
    @pytest.fixture
    def test_output_dir():
        output_dir = Path("tests/temp_output")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        yield output_dir
        
        import shutil
        try:
            shutil.rmtree(output_dir)
        except Exception:
            pass
    
    @pytest.fixture
    def sample_user_data():
        return {
            'name': 'Alice',
            'age': 25,
            'city': 'New York'
        }
    
@pytest.fixture
def invalid_user_data():
    return {
        'name': '',
        'age': -5,
        'city': '   '
    }


class TestDataProcessor:
    """数据处理器测试"""
    
    @pytest.fixture
    def processor(self):
        """创建数据处理器实例"""
        return DataProcessor()
    
    def test_init(self, processor):
        """测试初始化"""
        assert processor._processed_count == 0
        assert processor._logger is not None
        assert processor._validator is not None
    
    def test_load_data_success(self, processor, csv_test_data):
        """测试成功加载数据"""
        df = processor.load_data(csv_test_data['file_path'])
        assert isinstance(df, pd.DataFrame)
        assert len(df) == csv_test_data['row_count']
        assert list(df.columns) == ['name', 'age', 'city']
    
    def test_load_data_file_not_exists(self, processor):
        """测试加载不存在的文件"""
        with pytest.raises(DataProcessingError, match="数据文件不存在"):
            processor.load_data("nonexistent.csv")
    
    def test_load_data_empty_file(self, processor, empty_csv_file):
        """测试加载空文件"""
        with pytest.raises(DataProcessingError, match="数据文件为空"):
            processor.load_data(empty_csv_file)
    
    def test_load_data_malformed_file(self, processor, malformed_csv_file):
        """测试加载格式错误的文件"""
        with pytest.raises(DataProcessingError):
            processor.load_data(malformed_csv_file)
    
    def test_validate_dataframe_missing_columns(self, processor):
        """测试DataFrame列验证 - 缺少必要列"""
        df = pd.DataFrame({'name': ['Alice'], 'age': [25]})  #缺少city列
        with pytest.raises(DataProcessingError, match="缺少必要列"):
            processor._validate_dataframe(df)
    
    def test_validate_dataframe_invalid_data(self, processor):
        """测试DataFrame数据验证 - 无效数据"""
        df = pd.DataFrame({
            'name': ['', 'Bob'],  #空姓名
            'age': [-5, 30],      # 无效年龄
            'city': ['New York', '   ']  #空城市
        })
        with pytest.raises(DataProcessingError):
            processor._validate_dataframe(df)
    
    def test_process_data_success(self, processor, csv_test_data):
        """测试成功处理数据"""
        df = processor.load_data(csv_test_data['file_path'])
        processed_df = processor.process_data(df)
        
        assert 'processed' in processed_df.columns
        assert 'processed_at' in processed_df.columns
        assert processed_df['processed'].all()  #所有行都应标记为已处理
        assert processor.processed_count == len(processed_df)
    
    def test_process_data_validation_error(self, processor):
        """测试处理数据时的验证错误"""
        # 创建包含无效数据的DataFrame
        df = pd.DataFrame({
            'name': ['Alice', ''],  # 第二行有空姓名
            'age': [25, 30],
            'city': ['New York', 'London']
        })
        with pytest.raises(DataProcessingError):
            processor.process_data(df)
    
    def test_save_data_success(self, processor, csv_test_data, test_output_dir):
        """测试成功保存数据"""
        df = processor.load_data(csv_test_data['file_path'])
        output_path = test_output_dir / "output.csv"
        
        processor.save_data(df, str(output_path))
        
        assert output_path.exists()
        saved_df = pd.read_csv(output_path)
        assert len(saved_df) == len(df)
    
    def test_save_data_create_directory(self, processor, csv_test_data):
        """测试保存数据时创建目录"""
        df = processor.load_data(csv_test_data['file_path'])
        output_path = Path("tests/temp_output/nested/output.csv")
        
        try:
            processor.save_data(df, str(output_path))
            assert output_path.exists()
        finally:
            #清理
            import shutil
            if output_path.parent.exists():
                shutil.rmtree(output_path.parent.parent)
    
    def test_save_data_error(self, processor):
        """测试保存数据错误"""
        df = pd.DataFrame({'col': [1, 2, 3]})
        # 在Windows上测试权限错误，使用系统保留目录
        invalid_paths = [
            "CON/output.csv",  # Windows保留设备名
            "NUL/output.csv",  # Windows空设备
        ]
        
        error_raised = False
        for invalid_path in invalid_paths:
            try:
                processor.save_data(df, invalid_path)
            except DataProcessingError:
                error_raised = True
                break
            except Exception:
                error_raised = True
                break
        
        #如果都没有触发异常，手动创建一个会失败的情况
        if not error_raised:
            # 创建一个只读目录来测试权限错误
            import tempfile
            import stat
            temp_dir = tempfile.mkdtemp()
            try:
                # 设置目录为只读
                os.chmod(temp_dir, stat.S_IREAD | stat.S_IEXEC)
                readonly_path = os.path.join(temp_dir, "output.csv")
                with pytest.raises(DataProcessingError):
                    processor.save_data(df, readonly_path)
            finally:
                #清理
                try:
                    os.chmod(temp_dir, stat.S_IWRITE | stat.S_IREAD | stat.S_IEXEC)
                    os.rmdir(temp_dir)
                except:
                    pass
    
    def test_process_data_stream_success(self, processor, sample_user_data):
        """测试流式数据处理成功"""
        def data_generator():
            yield sample_user_data
            yield {'name': 'Bob', 'age': 30, 'city': 'London'}
        
        processed_data = list(processor.process_data_stream(data_generator()))
        
        assert len(processed_data) == 2
        assert all('processed' in data for data in processed_data)
        assert all('processed_at' in data for data in processed_data)
        assert processor.processed_count == 2
    
    def test_process_data_stream_validation_error(self, processor, invalid_user_data):
        """测试流式数据处理验证错误"""
        def data_generator():
            yield invalid_user_data  # 无效数据
            yield {'name': 'Bob', 'age': 30, 'city': 'London'}  # 有效数据
        
        processed_data = list(processor.process_data_stream(data_generator()))
        
        #应该只处理有效的数据
        assert len(processed_data) == 1
        assert processed_data[0]['name'] == 'Bob'
    
    def test_processed_count_property(self, processor):
        """测试已处理记录数属性"""
        assert processor.processed_count == 0
        
        #处理一些数据
        processor._processed_count = 5
        assert processor.processed_count == 5
    
    def test_reset_counters(self, processor):
        """测试重置计数器"""
        processor._processed_count = 10
        processor.reset_counters()
        assert processor.processed_count == 0
    
    def test_global_data_processor(self):
        """测试全局数据处理器"""
        processor1 = get_data_processor()
        processor2 = get_data_processor()
        assert processor1 is processor2
        assert isinstance(processor1, DataProcessor)


class TestDataProcessorIntegration:
    """数据处理器集成测试"""
    
    def test_full_data_processing_pipeline(self, csv_test_data, test_output_dir):
        """测试完整的数据处理流程"""
        processor = DataProcessor()
        
        # 1. 加载数据
        df = processor.load_data(csv_test_data['file_path'])
        assert len(df) == csv_test_data['row_count']
        
        # 2.处理数据
        processed_df = processor.process_data(df)
        assert len(processed_df) == csv_test_data['row_count']
        assert 'processed' in processed_df.columns
        assert 'processed_at' in processed_df.columns
        
        # 3. 保存数据
        output_path = test_output_dir / "processed_output.csv"
        processor.save_data(processed_df, str(output_path))
        assert output_path.exists()
        
        # 4.验证保存的数据
        saved_df = pd.read_csv(output_path)
        assert len(saved_df) == len(processed_df)
        assert 'processed' in saved_df.columns
        
        # 5.检查计数器
        assert processor.processed_count == len(processed_df)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])