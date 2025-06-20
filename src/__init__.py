"""
聊天机器人模块化架构
"""

from .ui import run_streamlit_interface, run_cli_interface

__version__ = "2.0.0"
__all__ = ["run_streamlit_interface", "run_cli_interface"]
