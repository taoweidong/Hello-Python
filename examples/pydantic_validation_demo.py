# examples/pydantic_validation_demo.py
"""
Pydantic数据校验示例
演示如何使用Pydantic进行配置文件加载和数据校验
"""

from src.models import UserData, ProcessedUserData
from pydantic import ValidationError
import json

def demo_user_data_validation():
    """演示用户数据校验"""
    print("=== Pydantic数据校验示例 ===\n")
    
    # 1. 有效的用户数据
    print("1. 创建有效的用户数据:")
    try:
        user1 = UserData(
            name="Alice",
            age=25,
            city="New York"
        )
        print(f"   成功创建用户: {user1.name}, 年龄: {user1.age}, 城市: {user1.city}")
        print(f"   序列化为JSON: {user1.model_dump_json()}\n")
    except ValidationError as e:
        print(f"   错误: {e}\n")
    
    # 2. 无效的年龄
    print("2. 尝试创建年龄无效的用户数据:")
    try:
        user2 = UserData(
            name="Bob",
            age=-5,  # 无效年龄
            city="London"
        )
        print(f"   意外成功: {user2}")
    except ValidationError as e:
        print(f"   捕获到校验错误: {e}\n")
    
    # 3. 空姓名
    print("3. 尝试创建姓名为空的用户数据:")
    try:
        user3 = UserData(
            name="",  # 空姓名
            age=30,
            city="Paris"
        )
        print(f"   意外成功: {user3}")
    except ValidationError as e:
        print(f"   捕获到校验错误: {e}\n")
    
    # 4. 处理后的用户数据
    print("4. 创建处理后的用户数据:")
    try:
        processed_user = ProcessedUserData(
            name="Charlie",
            age=35,
            city="Tokyo"
        )
        print(f"   处理后的用户: {processed_user.name}")
        print(f"   已处理: {processed_user.processed}")
        print(f"   处理时间: {processed_user.processed_at}")
        print(f"   模型字典: {processed_user.model_dump()}\n")
    except ValidationError as e:
        print(f"   错误: {e}\n")

def demo_config_validation():
    """演示配置校验"""
    print("=== 配置校验示例 ===\n")
    
    # 从环境变量加载配置
    from src.config.settings import settings
    
    print("当前配置:")
    print(f"  应用名称: {settings.APP_NAME}")
    print(f"  日志级别: {settings.LOG_LEVEL}")
    print(f"  数据文件路径: {settings.DATA_FILE_PATH}")
    print(f"  配置字典: {settings.model_dump()}")

if __name__ == "__main__":
    demo_user_data_validation()
    demo_config_validation()