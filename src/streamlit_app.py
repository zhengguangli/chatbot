#!/usr/bin/env python3
"""
Streamlit Web界面专用入口文件
避免与main.py的启动器逻辑冲突
"""

import sys
import os

# 添加src目录到Python路径
src_dir = os.path.dirname(os.path.abspath(__file__))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# 确保环境变量被加载
import config.environment  # 这会触发load_dotenv()执行

# 导入并运行Streamlit界面
from ui.streamlit import run_streamlit_interface

if __name__ == "__main__":
    # 直接运行Streamlit界面，不经过启动器
    run_streamlit_interface() 