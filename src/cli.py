#!/usr/bin/env python3
"""
智能聊天机器人 - CLI专用启动器
直接启动命令行界面，针对CLI用户体验优化

特性:
- 快速启动，无Web环境检测开销
- CLI特有的参数和功能
- 优化的CLI错误处理
- 兼容原有cli.py接口
"""

import sys
import os

# 添加src目录到Python路径
src_dir = os.path.dirname(os.path.abspath(__file__))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from launcher import (
    LaunchMode,
    LaunchConfig,
    launch_application,
    handle_startup_error,
    check_dependencies,
    validate_configuration
)


def print_cli_banner():
    """打印CLI专用横幅"""
    print("""
💻 智能聊天机器人 - 命令行界面
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
快速、简洁的AI对话体验
""")


def create_cli_argument_parser():
    """创建CLI专用的参数解析器"""
    import argparse
    
    parser = argparse.ArgumentParser(
        prog="cli",
        description="🤖 智能聊天机器人 - 命令行界面",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
CLI使用示例:
  python cli.py                  # 直接启动CLI
  python cli.py --debug          # 调试模式
  python cli.py --quick          # 快速启动（跳过检查）
  python cli.py --config custom  # 使用自定义配置

CLI专用功能:
  --quick      快速启动，跳过依赖和配置检查
  --no-banner  不显示启动横幅
  --compact    紧凑模式，减少输出信息
        """
    )
    
    # CLI专用选项
    parser.add_argument(
        "--quick", "-q",
        action="store_true",
        help="快速启动模式，跳过所有检查"
    )
    
    parser.add_argument(
        "--no-banner",
        action="store_true",
        help="不显示启动横幅"
    )
    
    parser.add_argument(
        "--compact",
        action="store_true", 
        help="紧凑模式，减少输出信息"
    )
    
    # 通用选项
    parser.add_argument(
        "--debug", "-d",
        action="store_true",
        help="启用调试模式"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="启用详细输出"
    )
    
    parser.add_argument(
        "--config", "-c",
        type=str,
        help="指定配置文件路径"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="聊天机器人 CLI v1.0.0"
    )
    
    return parser


def parse_cli_arguments():
    """解析CLI专用参数"""
    parser = create_cli_argument_parser()
    args = parser.parse_args()
    
    # 创建CLI专用配置
    config = LaunchConfig(
        mode=LaunchMode.CLI,  # 强制CLI模式
        debug=args.debug,
        verbose=args.verbose and not args.compact,
        config_path=args.config,
        skip_dependency_check=args.quick,
        force_mode=True  # CLI启动器总是强制模式
    )
    
    # 添加CLI专用配置
    config.extra_args = {
        'quick': args.quick,
        'no_banner': args.no_banner,
        'compact': args.compact
    }
    
    return config


def perform_cli_checks(config):
    """执行CLI启动检查"""
    if (config.extra_args or {}).get('quick', False):
        if config.debug:
            print("⚡ 快速启动模式，跳过检查")
        return []
    
    issues = []
    
    # 依赖检查（只检查CLI必需的）
    cli_modules = ["dotenv", "openai"]
    missing_deps = []
    
    for module in cli_modules:
        try:
            __import__(module)
        except ImportError:
            missing_deps.append(module)
    
    if missing_deps:
        issues.extend([f"缺失CLI依赖: {dep}" for dep in missing_deps])
    
    # 配置检查（简化版）
    if not os.getenv("OPENAI_API_KEY"):
        issues.append("未设置 OPENAI_API_KEY，AI功能将不可用")
    
    return issues


def main():
    """CLI主函数"""
    try:
        # 解析CLI参数
        config = parse_cli_arguments()
        
        # 显示横幅（除非禁用）
        if not (config.extra_args or {}).get('no_banner', False):
            if not (config.extra_args or {}).get('compact', False):
                print_cli_banner()
            else:
                print("💻 启动CLI界面...")
        
        # 执行检查
        issues = perform_cli_checks(config)
        
        # 处理检查结果
        if issues and not (config.extra_args or {}).get('compact', False):
            print("⚠️ 发现问题:")
            for issue in issues:
                print(f"  • {issue}")
            
            # CLI模式下更宽松的处理
            critical_issues = [issue for issue in issues if "缺失CLI依赖" in issue]
            if critical_issues:
                print("🔧 建议运行: uv sync")
            print()
        
        # 启动CLI界面
        if config.debug or config.verbose:
            print("🚀 启动命令行界面...")
        
        success = launch_application(config)
        
        if success:
            return 0
        else:
            if not (config.extra_args or {}).get('compact', False):
                print("❌ CLI启动失败")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️ 启动被中断")
        return 130
        
    except Exception as e:
        error_msg = handle_startup_error(e, debug='--debug' in sys.argv)
        print(f"\n{error_msg}")
        
        # CLI专用帮助
        print("\n💡 CLI故障排查:")
        print("  1. 运行 'python cli.py --help' 查看选项")
        print("  2. 运行 'python cli.py --debug' 获取详细信息")
        print("  3. 运行 'python cli.py --quick' 尝试快速启动")
        print("  4. 使用 'python main.py' 尝试主程序启动")
        
        return 1


def show_quick_help():
    """显示快速帮助"""
    print("""
💻 CLI快速帮助

基本使用:
  python cli.py           # 标准启动
  python cli.py --quick   # 快速启动
  python cli.py --help    # 完整帮助

常用选项:
  --debug        调试模式
  --no-banner    不显示横幅
  --compact      紧凑模式
  
优势:
  ⚡ 专为CLI优化
  🚀 启动更快速
  💡 更简洁的输出
""")


if __name__ == "__main__":
    # 处理特殊命令
    if len(sys.argv) > 1 and sys.argv[1] in ['help', 'usage']:
        show_quick_help()
        sys.exit(0)
    
    # 运行CLI主程序
    exit_code = main()
    sys.exit(exit_code) 