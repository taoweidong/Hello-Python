"""数据处理服务模块

提供数据加载、处理和验证功能。
"""

import pandas as pd
from pathlib import Path
from typing import Generator, List, Optional, Dict, Any
import logging
from datetime import datetime

from ..models import UserData, ProcessedUserData, get_data_validator
from ..config import get_logger


class DataProcessingError(Exception):
    """数据处理错误异常"""
    pass


class DataProcessor:
    """数据处理器
    
   数据的加载、处理、验证和转换。
    """
    
    def __init__(self) -> None:
        """初始化数据处理器"""
        self._logger = get_logger()
        self._validator = get_data_validator()
        self._processed_count: int = 0
        
    def load_data(self, file_path: str) -> pd.DataFrame:
        """加载数据文件
        
        Args:
            file_path: 数据文件路径
            
        Returns:
            pd.DataFrame: 加载的数据
            
        Raises:
            DataProcessingError: 数据加载或验证失败时
        """
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                raise DataProcessingError(f"数据文件不存在: {file_path}")
            
            self._logger.info(f"正在加载数据文件: {file_path}")
            df = pd.read_csv(file_path)
            
            #验证数据
            self._validate_dataframe(df)
            
            self._logger.info(f"成功加载 {len(df)}条")
            return df
            
        except pd.errors.EmptyDataError as e:
            raise DataProcessingError(f"数据文件为空: {e}")
        except pd.errors.ParserError as e:
            raise DataProcessingError(f"数据文件格式错误: {e}")
        except Exception as e:
            raise DataProcessingError(f"数据加载失败: {e}")
    
    def _validate_dataframe(self, df: pd.DataFrame) -> None:
        """验证DataFrame数据
        
        Args:
            df:要的DataFrame
            
        Raises:
            DataProcessingError: 数据验证失败时
        """
        required_columns = {'name', 'age', 'city'}
        missing_columns = required_columns - set(df.columns)
        
        if missing_columns:
            raise DataProcessingError(f"缺少必要列: {missing_columns}")
        
        #验证每行数据
        validation_errors = []
        for idx, row in df.iterrows():
            data_dict = {
                'name': str(row['name']),
                'age': int(row['age']),
                'city': str(row['city'])
            }
            
            result = self._validator.validate_user_data(data_dict)
            if not result:
                validation_errors.append(f"第{idx+1}行: {', '.join(result.errors)}")
        
        if validation_errors:
            error_msg = f"数据验证失败:\n" + "\n".join(validation_errors[:5])  # 只显示前5个错误
            if len(validation_errors) > 5:
                error_msg += f"\n...还 {len(validation_errors) - 5} 个错误"
            raise DataProcessingError(error_msg)
    
    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """处理数据
        
        Args:
            df:原数据始数据
            
        Returns:
            pd.DataFrame: 处理后的数据
            
        Raises:
            DataProcessingError: 数据处理失败时
        """
        try:
            self._logger.info("开始处理数据")
            
            # 添加处理状态列
            processed_df = df.copy()
            processed_df['processed'] = True
            processed_df['processed_at'] = datetime.now().isoformat()
            
            #验证处理后的数据
            self._validate_processed_dataframe(processed_df)
            
            self._processed_count += len(processed_df)
            self._logger.info(f"数据处理完成，共处理 {len(processed_df)}条")
            
            return processed_df
            
        except Exception as e:
            raise DataProcessingError(f"数据处理失败: {e}")
    
    def _validate_processed_dataframe(self, df: pd.DataFrame) -> None:
        """验证处理后的DataFrame数据
        
        Args:
            df:处理后的DataFrame
            
        Raises:
            DataProcessingError: 数据验证失败时
        """
        validation_errors = []
        for idx, row in df.iterrows():
            data_dict = {
                'name': str(row['name']),
                'age': int(row['age']),
                'city': str(row['city']),
                'processed': bool(row.get('processed', True)),
                'processed_at': datetime.fromisoformat(str(row.get('processed_at', datetime.now().isoformat())))
            }
            
            result = self._validator.validate_processed_data(data_dict)
            if not result:
                validation_errors.append(f"第{idx+1}行: {', '.join(result.errors)}")
        
        if validation_errors:
            error_msg = f"处理后数据验证失败:\n" + "\n".join(validation_errors[:5])
            if len(validation_errors) > 5:
                error_msg += f"\n... 还有 {len(validation_errors) - 5} 个错误"
            raise DataProcessingError(error_msg)
    
    def save_data(self, df: pd.DataFrame, output_path: str, **kwargs) -> None:
        """保存数据到文件
        
        Args:
            df:要的数据
            output_path: 输出文件路径
            **kwargs: 传递给to_csv的额外参数
            
        Raises:
            DataProcessingError: 数据保存失败时
        """
        try:
            output_path_obj = Path(output_path)
            output_path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            self._logger.info(f"正在保存数据到: {output_path}")
            
            default_kwargs = {
                'index': False,
                'encoding': 'utf-8'
            }
            default_kwargs.update(kwargs)
            
            df.to_csv(output_path, **default_kwargs)
            
            self._logger.info(f"数据保存成功，共 {len(df)} 条记录")
            
        except Exception as e:
            raise DataProcessingError(f"数据保存失败: {e}")
    
    def process_data_stream(self, data_stream: Generator[Dict[str, Any], None, None]) -> Generator[Dict[str, Any], None, None]:
        """流式处理数据
        
        Args:
            data_stream: 数据流生成器
            
        Yields:
            Dict[str, Any]:处理后的数据
            
        Raises:
            DataProcessingError: 数据处理失败时
        """
        try:
            for data in data_stream:
                # 验证原始数据
                validation_result = self._validator.validate_user_data(data)
                if not validation_result:
                    self._logger.warning(f"数据验证失败: {', '.join(validation_result.errors)}")
                    continue
                
                #处理数据
                processed_data = {
                    **data,
                    'processed': True,
                    'processed_at': datetime.now().isoformat()
                }
                
                #验证处理后的数据
                processed_validation = self._validator.validate_processed_data(processed_data)
                if not processed_validation:
                    self._logger.warning(f"处理后数据验证失败: {', '.join(processed_validation.errors)}")
                    continue
                
                yield processed_data
                self._processed_count += 1
                
        except Exception as e:
            raise DataProcessingError(f"流式数据处理失败: {e}")
    
    @property
    def processed_count(self) -> int:
        """获取已处理的记录数
        
        Returns:
            int:已处理的记录数
        """
        return self._processed_count
    
    def reset_counters(self) -> None:
        """重置计数器"""
        self._processed_count = 0
        self._logger.info("计数器已重置")


#全局数据处理器实例
_data_processor: Optional[DataProcessor] = None


def get_data_processor() -> DataProcessor:
    """获取全局数据处理器实例
    
    Returns:
        DataProcessor: 数据处理器实例
    """
    global _data_processor
    if _data_processor is None:
        _data_processor = DataProcessor()
    return _data_processor