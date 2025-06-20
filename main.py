#!/usr/bin/env python3
"""
聊天机器人 - 主程序启动代理
保持向后兼容性，将启动请求转发到src/main.py

这个文件是一个简单的代理，所有实际的启动逻辑都在src/main.py中。
保持这个文件简洁，确保现有的启动方式（如make run）继续工作。
"""

import sys
import os

# 确保可以导入src模块
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

if __name__ == "__main__":
    try:
        # 导入并运行src中的主程序
        from src.main import main
        exit_code = main()
        sys.exit(exit_code)
        
    except ImportError as e:
        # 如果新架构不可用，回退到原始实现
        print(f"⚠️ 新架构不可用 ({e})，尝试回退到原始实现...")
        
        try:
            # 尝试回退到基本功能
            from src import run_streamlit_interface, run_cli_interface
            
            # 简单的环境检测
            if len(sys.argv) > 0 and 'streamlit' in sys.argv[0]:
                run_streamlit_interface()
            elif 'STREAMLIT_SERVER_PORT' in os.environ:
                run_streamlit_interface()
            else:
                print("🖥️ 运行CLI模式...")
                print("💡 要使用Web界面，请运行: uv run streamlit run main.py")
                run_cli_interface()
                
        except Exception as fallback_error:
            print(f"❌ 启动失败: {fallback_error}")
            print("📖 请检查项目文档或运行 'uv sync' 安装依赖")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print("💡 尝试运行 'python src/main.py --help' 获取帮助")
        sys.exit(1) 