"""
聊天机器人模块化架构
"""

from .ui.streamlit_app import run_streamlit_interface
from .ui.cli_app import run_cli_interface

__version__ = "2.0.0"
__all__ = ["run_streamlit_interface", "run_cli_interface"]
