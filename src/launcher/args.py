"""
命令行参数处理模块
提供完整的argparse参数解析和配置生成功能
"""

import argparse
import sys
from typing import List, Optional

from .core import LaunchMode, LaunchConfig


def create_argument_parser() -> argparse.ArgumentParser:
    """
    创建命令行参数解析器
    
    Returns:
        argparse.ArgumentParser: 配置好的参数解析器
    """
    parser = argparse.ArgumentParser(
        prog="chatbot",
        description="🤖 智能聊天机器人 - 基于AI的对话系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py                     # 自动检测环境启动
  python main.py --mode web          # 强制启动Web界面
  python main.py --mode cli          # 强制启动CLI界面
  python main.py --mode validate     # 运行架构验证
  python main.py --debug             # 启用调试模式
  python main.py --port 8080         # 指定Web界面端口

更多信息:
  项目地址: https://github.com/your-username/chatbot
  文档地址: https://your-docs-site.com
        """
    )
    
    # 启动模式选项
    parser.add_argument(
        "--mode", "-m",
        type=str,
        choices=["auto", "web", "cli", "validate"],
        default="auto",
        help="启动模式选择 (默认: auto)"
    )
    
    # 调试和详细输出选项
    parser.add_argument(
        "--debug", "-d",
        action="store_true",
        help="启用调试模式，显示详细的错误信息和日志"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true", 
        help="启用详细输出模式"
    )
    
    # 配置文件选项
    parser.add_argument(
        "--config", "-c",
        type=str,
        help="指定配置文件路径"
    )
    
    # Web界面选项
    web_group = parser.add_argument_group("Web界面选项")
    web_group.add_argument(
        "--port", "-p",
        type=int,
        help="Web界面端口号 (默认: Streamlit默认端口)"
    )
    
    web_group.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="Web界面主机地址 (默认: localhost)"
    )
    
    # 高级选项
    advanced_group = parser.add_argument_group("高级选项")
    advanced_group.add_argument(
        "--skip-deps",
        action="store_true",
        help="跳过依赖检查（快速启动）"
    )
    
    advanced_group.add_argument(
        "--force",
        action="store_true",
        help="强制使用指定模式，忽略环境检测"
    )
    
    # 版本信息
    parser.add_argument(
        "--version",
        action="version",
        version="聊天机器人 v1.0.0 (重构版本)"
    )
    
    return parser


def parse_launch_arguments(args: Optional[List[str]] = None) -> LaunchConfig:
    """
    解析命令行参数并生成启动配置
    
    Args:
        args: 命令行参数列表，None表示使用sys.argv
        
    Returns:
        LaunchConfig: 解析后的启动配置
    """
    parser = create_argument_parser()
    
    # 解析参数
    if args is None:
        parsed_args = parser.parse_args()
    else:
        parsed_args = parser.parse_args(args)
    
    # 转换启动模式
    mode_map = {
        "auto": LaunchMode.AUTO,
        "web": LaunchMode.WEB,
        "cli": LaunchMode.CLI,
        "validate": LaunchMode.VALIDATE
    }
    
    # 创建配置对象
    config = LaunchConfig(
        mode=mode_map[parsed_args.mode],
        debug=parsed_args.debug,
        verbose=parsed_args.verbose,
        config_path=parsed_args.config,
        port=parsed_args.port,
        host=parsed_args.host,
        skip_dependency_check=parsed_args.skip_deps,
        force_mode=parsed_args.force
    )
    
    return config


def print_usage_help():
    """打印使用帮助信息"""
    parser = create_argument_parser()
    parser.print_help()


def print_quick_help():
    """打印快速帮助信息"""
    print("""
🤖 智能聊天机器人 - 快速帮助

基本使用:
  python main.py              # 自动启动 (推荐)
  python cli.py               # 直接启动CLI
  
常用选项:
  --mode web                  # Web界面
  --mode cli                  # 命令行界面  
  --debug                     # 调试模式
  --help                      # 完整帮助

快速启动:
  make run                    # Web界面 (推荐)
  make cli                    # 命令行界面
  
详细帮助: python main.py --help
    """)


def handle_special_commands() -> bool:
    """
    处理特殊命令（如help等），如果处理了特殊命令则返回True
    
    Returns:
        bool: 是否处理了特殊命令
    """
    if len(sys.argv) > 1:
        if sys.argv[1] in ['help', 'usage']:
            print_quick_help()
            return True
        elif sys.argv[1] == 'validate':
            # 快捷方式：直接运行验证
            sys.argv[1] = '--mode'
            sys.argv.insert(2, 'validate')
            return False
    
    return False 