"""测试配置"""

import sys
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# 加载公共 fixtures（csv_test_data, test_output_dir 等）
pytest_plugins = ["tests.fixtures.test_data"]
