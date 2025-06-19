#!/usr/bin/env python3
"""
命令行启动器 - 避免Streamlit导入
"""

if __name__ == "__main__":
    from src.ui.cli_app import run_cli_interface

    run_cli_interface()
