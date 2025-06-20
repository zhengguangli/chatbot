#!/usr/bin/env python3
"""
聊天机器人 - CLI启动代理
保持向后兼容性，将CLI启动请求转发到src/cli.py

这个文件是一个简单的代理，专门用于CLI启动。
所有CLI相关的优化和功能都在src/cli.py中实现。
"""

import sys
import os

# 确保可以导入src模块
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

if __name__ == "__main__":
    try:
        # 导入并运行src中的CLI程序
        from src.cli import main
        exit_code = main()
        sys.exit(exit_code)
        
    except ImportError as e:
        # 如果新架构不可用，回退到原始CLI实现
        print(f"⚠️ 新CLI架构不可用 ({e})，尝试回退...")
        
        try:
            # 回退到基本CLI功能
            from src.ui.cli_app import run_cli_interface
            run_cli_interface()
            
        except Exception as fallback_error:
            print(f"❌ CLI启动失败: {fallback_error}")
            print("📖 请检查项目文档或运行 'uv sync' 安装依赖")
            print("💡 或者尝试运行: python main.py --mode cli")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ CLI启动失败: {e}")
        print("💡 尝试运行 'python src/cli.py --help' 获取帮助")
        sys.exit(1) 