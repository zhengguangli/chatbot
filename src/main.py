#!/usr/bin/env python3
"""
智能聊天机器人 - 主程序入口
使用现代化启动器架构，支持智能环境检测和丰富的命令行选项

重构版本特性:
- 智能环境检测 (Web/CLI自动选择)
- 完整的命令行参数支持
- 优化的错误处理和用户提示
- 模块化启动器架构
- 向后兼容性保证
"""

import sys
import os
import logging

# 添加src目录到Python路径
src_dir = os.path.dirname(os.path.abspath(__file__))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# 配置全局日志系统，确保OpenAI日志可见
def configure_application_logging():
    """配置应用程序的全局日志系统"""
    # 设置根日志级别
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # 特别配置OpenAI Provider的日志
    openai_logger = logging.getLogger('services.model_providers')
    openai_logger.setLevel(logging.DEBUG)
    
    # 确保在启动时显示日志状态
    logger = logging.getLogger(__name__)
    logger.info("🔍 应用程序日志系统已配置")
    logger.info("✅ OpenAI API请求日志已启用 (级别: DEBUG)")

# 在模块加载时立即配置日志
configure_application_logging()

# 全局状态控制，避免重复输出
_BANNER_PRINTED = False
_SESSION_INITIALIZED = False

# 确保环境变量被加载 - 导入environment模块会自动加载.env文件
import config.environment  # 这会触发load_dotenv()执行

from launcher import (
    parse_launch_arguments,
    launch_application, 
    handle_startup_error,
    format_startup_message,
    check_dependencies,
    validate_configuration,
    detect_environment,
    LaunchMode
)
from launcher.utils import print_system_info
from launcher.args import handle_special_commands


def print_welcome_banner():
    """打印欢迎横幅"""
    global _BANNER_PRINTED
    
    # 如果已经打印过，直接返回
    if _BANNER_PRINTED:
        return
    
    # 检测当前环境，在Streamlit环境中不输出横幅
    current_env = detect_environment()
    if current_env == LaunchMode.WEB:
        # 在Web环境中使用简化输出，但只输出一次
        # 使用Streamlit的会话状态来控制输出
        try:
            import streamlit as st
            if not hasattr(st.session_state, 'banner_printed'):
                print("🤖 智能启动检测")
                st.session_state.banner_printed = True
            _BANNER_PRINTED = True
        except:
            # 如果不在Streamlit环境中，使用全局状态
            if not _BANNER_PRINTED:
                print("🤖 智能启动检测")
            _BANNER_PRINTED = True
        return
    
    # 只在CLI环境中显示完整横幅
    print("""
🤖 智能聊天机器人 v1.0.0 (重构版本)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
基于AI的智能对话系统 | 现代化分层架构 | 异步优先设计
""")
    _BANNER_PRINTED = True


def perform_startup_checks(config):
    """执行启动前检查"""
    issues = []
    
    # 依赖检查
    if not config.skip_dependency_check:
        missing_deps, warnings = check_dependencies()
        if missing_deps:
            issues.extend([f"缺失依赖: {dep}" for dep in missing_deps])
        
        if warnings and (config.verbose or config.debug):
            for warning in warnings:
                print(f"⚠️ {warning}")
    
    # 配置验证
    config_valid, config_errors = validate_configuration(config.config_path)
    if not config_valid:
        issues.extend(config_errors)
    
    return issues


def main():
    """主函数 - 智能启动入口"""
    try:
        # 处理特殊命令
        if handle_special_commands():
            return 0
        
        # 解析命令行参数
        config = parse_launch_arguments()
        
        # 打印欢迎信息 - 只在非Web环境中
        current_env = detect_environment()
        if current_env != LaunchMode.WEB and not config.debug:  # 调试模式下保持简洁
            print_welcome_banner()
        
        # 显示启动信息
        startup_msg = format_startup_message(
            config.mode.value, 
            config.port, 
            config.debug
        )
        print(startup_msg)
        
        # 显示系统信息（调试或详细模式）
        if config.debug or config.verbose:
            print_system_info(verbose=config.debug)
        
        # 执行启动前检查
        issues = perform_startup_checks(config)
        
        # 处理检查结果
        if issues:
            print("\n⚠️ 启动检查发现问题:")
            for issue in issues:
                print(f"  • {issue}")
            
            # 如果有严重问题，询问是否继续
            critical_issues = [issue for issue in issues if "缺失依赖" in issue]
            if critical_issues and not config.force_mode:
                response = input("\n是否继续启动? (y/N): ").strip().lower()
                if response not in ['y', 'yes', '是']:
                    print("启动已取消")
                    return 1
            print()
        
        # 启动应用程序
        success = launch_application(config)
        
        if success:
            if config.debug:
                print("✅ 应用程序正常退出")
            return 0
        else:
            print("❌ 应用程序启动失败")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⚠️ 启动被用户中断")
        return 130  # 标准中断退出码
        
    except Exception as e:
        # 使用启动器的错误处理
        error_msg = handle_startup_error(e, debug='--debug' in sys.argv)
        print(f"\n{error_msg}")
        
        # 提供帮助建议
        print("\n💡 建议:")
        print("  1. 运行 'python main.py --help' 查看使用帮助")
        print("  2. 运行 'python main.py --debug' 获取详细错误信息")
        print("  3. 运行 'python main.py --mode validate' 验证环境配置")
        print("  4. 检查 README.md 文档获取更多帮助")
        
        return 1


def show_compatibility_info():
    """显示兼容性信息"""
    print("""
🔄 向后兼容性说明:
  所有原有的启动方式仍然完全支持:
  
  原有方式        新增功能
  ────────────    ────────────────────
  python main.py  + 智能环境检测
                  + 命令行参数支持  
                  + 增强错误处理
                  + 启动前检查
                  
  make run        (保持不变)
  make cli        (保持不变)
  
📖 新功能使用:
  python main.py --help          # 查看所有选项
  python main.py --mode cli      # 强制CLI模式
  python main.py --debug         # 调试模式
  python main.py --port 8080     # 自定义端口
    """)


if __name__ == "__main__":
    # 处理特殊参数
    if len(sys.argv) > 1 and sys.argv[1] in ['--compat', '--compatibility']:
        show_compatibility_info()
        sys.exit(0)
    
    # 运行主程序
    exit_code = main()
    sys.exit(exit_code) 