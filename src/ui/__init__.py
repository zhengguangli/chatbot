"""
用户界面模块
"""

# 新架构版本界面
from .streamlit import run_streamlit_interface
from .cli import run_cli_interface

# 兼容性包装器和适配器
from .compatibility import (
    initialize_openai_client,
    get_chatbot_response,
    manage_conversation_history,
    check_environment
)
from .adapters import UIAdapter, get_global_adapter

__all__ = [
    # 主要接口
    "run_streamlit_interface",
    "run_cli_interface",
    
    # 兼容性函数
    "initialize_openai_client",
    "get_chatbot_response",
    "manage_conversation_history",
    "check_environment",
    
    # 适配器
    "UIAdapter",
    "get_global_adapter"
]
