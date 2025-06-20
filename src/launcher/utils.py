"""
启动工具模块
提供依赖检查、配置验证、错误处理和用户友好消息格式化功能
"""

import os
import sys
import importlib
import subprocess
from typing import List, Tuple, Dict, Any, Optional
from pathlib import Path


def check_dependencies() -> Tuple[List[str], List[str]]:
    """
    检查核心依赖是否安装
    
    Returns:
        Tuple[List[str], List[str]]: (缺失依赖列表, 警告消息列表)
    """
    required_modules = [
        "streamlit",
        "openai", 
        "dotenv",
        "langchain"
    ]
    
    missing_deps = []
    warnings = []
    
    for module in required_modules:
        try:
            importlib.import_module(module)
        except ImportError:
            missing_deps.append(module)
    
    # 检查可选依赖
    optional_modules = {
        "watchdog": "文件监控功能可能不可用",
        "pytest": "测试功能不可用"
    }
    
    for module, warning_msg in optional_modules.items():
        try:
            importlib.import_module(module)
        except ImportError:
            warnings.append(warning_msg)
    
    return missing_deps, warnings


def validate_configuration(config_path: Optional[str] = None) -> Tuple[bool, List[str]]:
    """
    验证配置文件和环境变量
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        Tuple[bool, List[str]]: (是否有效, 错误消息列表)
    """
    errors = []
    
    # 检查环境变量文件
    env_files = [".env", ".env.local", ".env.production"]
    env_file_found = False
    
    for env_file in env_files:
        if os.path.exists(env_file):
            env_file_found = True
            break
    
    if not env_file_found:
        errors.append("未找到环境配置文件 (.env)，某些功能可能不可用")
    
    # 检查API密钥
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        errors.append("未设置 OPENAI_API_KEY 环境变量，AI功能将不可用")
    elif not api_key.startswith(('sk-', 'pk-')):
        errors.append("OPENAI_API_KEY 格式可能不正确")
    
    # 检查自定义配置文件
    if config_path and not os.path.exists(config_path):
        errors.append(f"指定的配置文件不存在: {config_path}")
    
    # 检查data目录权限
    data_dir = Path("data")
    if data_dir.exists() and not os.access(data_dir, os.W_OK):
        errors.append("data目录不可写，数据持久化功能可能失败")
    
    return len(errors) == 0, errors


def format_startup_message(mode: str, port: Optional[int] = None, debug: bool = False) -> str:
    """
    格式化启动消息
    
    Args:
        mode: 启动模式
        port: 端口号
        debug: 是否调试模式
        
    Returns:
        str: 格式化的启动消息
    """
    messages = {
        "web": "🌐 启动Web界面",
        "cli": "💻 启动命令行界面", 
        "validate": "🔍 运行架构验证",
        "auto": "🤖 智能启动检测"
    }
    
    base_msg = messages.get(mode, f"🚀 启动{mode}模式")
    
    if port:
        base_msg += f" (端口: {port})"
    
    if debug:
        base_msg += " [调试模式]"
    
    return base_msg


def handle_startup_error(error: Exception, debug: bool = False) -> str:
    """
    处理启动错误并生成用户友好的错误消息
    
    Args:
        error: 异常对象
        debug: 是否显示调试信息
        
    Returns:
        str: 格式化的错误消息
    """
    error_type = type(error).__name__
    error_msg = str(error)
    
    # 常见错误的友好提示
    friendly_messages = {
        "ModuleNotFoundError": {
            "streamlit": "请安装Streamlit: uv add streamlit",
            "openai": "请安装OpenAI: uv add openai",
            "dotenv": "请安装python-dotenv: uv add python-dotenv"
        },
        "FileNotFoundError": "指定的文件不存在，请检查路径",
        "PermissionError": "权限不足，请检查文件和目录权限",
        "ConnectionError": "网络连接失败，请检查网络设置",
        "ImportError": "模块导入失败，请检查依赖安装"
    }
    
    # 生成友好消息
    friendly_msg = "启动失败"
    
    if error_type in friendly_messages:
        if isinstance(friendly_messages[error_type], dict):
            # 根据错误消息内容匹配
            for key, msg in friendly_messages[error_type].items():
                if key.lower() in error_msg.lower():
                    friendly_msg = msg
                    break
        else:
            friendly_msg = friendly_messages[error_type]
    
    # 构建完整错误消息
    result = f"❌ {friendly_msg}"
    
    if debug:
        result += f"\n\n🔍 调试信息:\n错误类型: {error_type}\n错误详情: {error_msg}"
        
        # 添加调用堆栈
        import traceback
        result += f"\n\n调用堆栈:\n{traceback.format_exc()}"
    
    return result


def get_system_info() -> Dict[str, Any]:
    """
    获取系统信息
    
    Returns:
        Dict[str, Any]: 系统信息字典
    """
    return {
        "python_version": sys.version,
        "platform": sys.platform,
        "executable": sys.executable,
        "path": sys.path[:3],  # 只显示前3个路径
        "working_directory": os.getcwd(),
        "environment_variables": {
            key: value for key, value in os.environ.items() 
            if key.startswith(('OPENAI_', 'STREAMLIT_', 'PYTHON_'))
        }
    }


def print_system_info(verbose: bool = False):
    """
    打印系统信息
    
    Args:
        verbose: 是否显示详细信息
    """
    info = get_system_info()
    
    print("📋 系统信息:")
    print(f"  Python版本: {info['python_version'].split()[0]}")
    print(f"  运行平台: {info['platform']}")
    print(f"  工作目录: {info['working_directory']}")
    
    if verbose:
        print(f"  Python可执行文件: {info['executable']}")
        print("  环境变量:")
        for key, value in info['environment_variables'].items():
            # 隐藏敏感信息
            if 'key' in key.lower() or 'secret' in key.lower():
                value = f"{value[:8]}..." if len(value) > 8 else "***"
            print(f"    {key}: {value}")


def check_port_availability(port: int) -> bool:
    """
    检查端口是否可用
    
    Args:
        port: 端口号
        
    Returns:
        bool: 端口是否可用
    """
    import socket
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            return result != 0  # 连接失败说明端口可用
    except Exception:
        return False


def suggest_alternative_port(preferred_port: int) -> int:
    """
    建议可用的替代端口
    
    Args:
        preferred_port: 首选端口
        
    Returns:
        int: 建议的可用端口
    """
    # 尝试首选端口附近的端口
    for offset in range(1, 10):
        for port in [preferred_port + offset, preferred_port - offset]:
            if 1024 <= port <= 65535 and check_port_availability(port):
                return port
    
    # 如果找不到，返回一个随机可用端口
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(('localhost', 0))
        return sock.getsockname()[1]


def create_env_file_template():
    """创建环境变量文件模板"""
    template = """# 聊天机器人环境配置
# 复制此文件为 .env 并填写实际值

# OpenAI API配置
OPENAI_API_KEY=your_openai_api_key_here

# Streamlit配置
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost

# 应用配置
APP_DEBUG=false
APP_LOG_LEVEL=INFO

# 数据存储配置
DATA_PATH=./data
BACKUP_ENABLED=true
"""
    
    if not os.path.exists(".env"):
        with open(".env.example", "w", encoding="utf-8") as f:
            f.write(template)
        print("✅ 已创建 .env.example 文件")
        print("💡 请复制为 .env 并填写实际配置值")
    else:
        print("⚠️ .env 文件已存在，跳过创建") 