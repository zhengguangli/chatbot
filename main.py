"""
简单的聊天机器人主程序 - 重构版本
使用模块化架构，支持Web和CLI两种界面
"""

import sys
from src import run_streamlit_interface, run_cli_interface


def is_streamlit_context():
    """检查是否在Streamlit运行环境中"""
    # 检查是否通过 streamlit run 启动
    # 方法1: 检查命令行参数
    if len(sys.argv) > 0 and 'streamlit' in sys.argv[0]:
        return True
    
    # 方法2: 检查环境变量（当通过streamlit run时设置）
    import os
    if 'STREAMLIT_SERVER_PORT' in os.environ:
        return True
        
    # 方法3: 检查调用堆栈是否包含streamlit
    import inspect
    for frame_info in inspect.stack():
        if 'streamlit' in frame_info.filename:
            return True
    
    return False


def main():
    """主函数 - 智能检测运行环境"""
    if is_streamlit_context():
        # 在Streamlit环境中，运行Web界面
        print("🌐 检测到Streamlit环境，启动Web界面...")
        run_streamlit_interface()
    else:
        # 不在Streamlit环境中，运行CLI界面
        print("🖥️  运行CLI模式...")
        print("💡 提示：要使用Web界面，请运行: uv run streamlit run main.py")
        run_cli_interface()


if __name__ == "__main__":
    main()
