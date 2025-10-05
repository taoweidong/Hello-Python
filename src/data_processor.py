# src/data_processor.py
import pandas as pd
from src.models import UserData, ProcessedUserData
from typing import List
from datetime import datetime

def load_data(file_path):
    """加载数据并进行校验"""
    try:
        df = pd.read_csv(file_path)
        
        # 将DataFrame转换为用户数据模型列表进行校验
        user_data_list: List[UserData] = []
        for idx in range(len(df)):
            # 使用Pydantic模型进行数据校验
            user_data = UserData(
                name=str(df.iloc[idx]['name']),
                age=int(df.iloc[idx]['age']),
                city=str(df.iloc[idx]['city'])
            )
            user_data_list.append(user_data)
        
        return df
    except Exception as e:
        raise Exception(f"加载数据失败: {str(e)}")

def process_data(df):
    """处理数据并进行校验"""
    try:
        # 示例数据处理：添加一个新列
        df['processed'] = True
        
        # 使用Pydantic模型进行处理后数据校验
        processed_data_list: List[ProcessedUserData] = []
        for idx in range(len(df)):
            processed_data = ProcessedUserData(
                name=str(df.iloc[idx]['name']),
                age=int(df.iloc[idx]['age']),
                city=str(df.iloc[idx]['city']),
                processed=bool(df.iloc[idx]['processed']),
                processed_at=datetime.now()
            )
            processed_data_list.append(processed_data)
        
        return df
    except Exception as e:
        raise Exception(f"处理数据失败: {str(e)}")