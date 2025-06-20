"""
启动器模块
提供统一的应用启动逻辑、命令行参数处理和环境检测功能
"""

from .core import (
    LaunchMode,
    LaunchConfig,
    ApplicationLauncher,
    detect_environment,
    launch_application
)

from .args import (
    create_argument_parser,
    parse_launch_arguments
)

from .utils import (
    check_dependencies,
    validate_configuration,
    format_startup_message,
    handle_startup_error
)

__all__ = [
    # 核心启动功能
    'LaunchMode',
    'LaunchConfig',
    'ApplicationLauncher', 
    'detect_environment',
    'launch_application',
    
    # 命令行参数处理
    'create_argument_parser',
    'parse_launch_arguments',
    
    # 启动工具函数
    'check_dependencies',
    'validate_configuration',
    'format_startup_message',
    'handle_startup_error'
] 