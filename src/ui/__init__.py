"""
用户界面模块
支持原版和新架构版本的界面
"""

# 原版界面（保持兼容性）
from .streamlit_app import run_streamlit_interface as run_streamlit_interface_v1
from .cli_app import run_cli_interface as run_cli_interface_v1

# 新架构版本界面
from .streamlit_app_v2 import run_streamlit_interface as run_streamlit_interface_v2
from .cli_app_v2 import run_cli_interface as run_cli_interface_v2

# 兼容性包装器和适配器
from .compatibility import (
    initialize_openai_client,
    get_chatbot_response,
    manage_conversation_history,
    check_environment
)
from .adapters import UIAdapter, get_global_adapter

# 默认导出（新架构版本）
run_streamlit_interface = run_streamlit_interface_v2
run_cli_interface = run_cli_interface_v2

__all__ = [
    # 主要接口
    "run_streamlit_interface",
    "run_cli_interface",
    
    # 版本化接口
    "run_streamlit_interface_v1",
    "run_cli_interface_v1", 
    "run_streamlit_interface_v2",
    "run_cli_interface_v2",
    
    # 兼容性函数
    "initialize_openai_client",
    "get_chatbot_response",
    "manage_conversation_history",
    "check_environment",
    
    # 适配器
    "UIAdapter",
    "get_global_adapter"
]
