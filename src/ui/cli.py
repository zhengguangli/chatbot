"""
命令行界面模块 - 新架构版本
使用新的服务架构，但保持原有的用户体验
"""

import os
import sys
from .compatibility import (
    initialize_openai_client,
    get_chatbot_response,
    manage_conversation_history,
    check_environment,
    CLI_HELP_MESSAGE,
    MAX_CONVERSATION_HISTORY
)


def print_banner():
    """打印启动横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                    🤖 智能聊天助手                          ║
║                   重构架构版本 v2.0                         ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)


def print_help():
    """打印帮助信息"""
    help_text = """
📋 可用命令：
• quit, exit, 退出     - 结束对话
• clear, 清空          - 清空对话历史
• help, 帮助           - 显示此帮助信息
• status, 状态         - 显示系统状态
• sessions, 会话       - 会话管理（开发中）
• debug, 调试          - 显示调试信息

💡 提示：
• 直接输入文本开始对话
• 输入 'uv run streamlit run main.py' 启动Web界面
"""
    print(help_text)


def print_status(client):
    """打印系统状态"""
    print("\n📊 系统状态:")
    print(f"• AI客户端: {'✅ 已连接' if client else '❌ 未连接'}")
    print(f"• 架构版本: 重构架构 v2.0")
    print(f"• 服务状态: 使用新服务容器")
    print(f"• 数据存储: 文件存储系统")
    print()


def print_debug_info(conversation_history, client):
    """打印调试信息"""
    print("\n🔧 调试信息:")
    print(f"• 消息数量: {len(conversation_history)}")
    print(f"• 客户端状态: {type(client).__name__ if client else 'None'}")
    print(f"• 最大历史: {MAX_CONVERSATION_HISTORY}")
    
    if conversation_history:
        print(f"• 最后消息: {conversation_history[-1]['role']} - {conversation_history[-1]['content'][:50]}...")
    else:
        print("• 最后消息: 无")
    print()


def run_cli_interface():
    """运行命令行界面 - 新架构版本"""
    
    print_banner()
    print("🚀 启动中...")
    print("💡 提示：运行 'uv run streamlit run main.py' 启动Web界面\n")

    # 环境检查（使用兼容性包装器）
    print("🔍 正在检查环境...")
    import asyncio
    env_issues, env_warnings = asyncio.run(check_environment())
    
    if env_issues:
        print("❌ 环境配置问题：")
        for issue in env_issues:
            print(f"   • {issue}")
        print(CLI_HELP_MESSAGE)
        return

    if env_warnings:
        print("⚠️ 配置警告：")
        for warning in env_warnings:
            print(f"   • {warning}")
        print()

    # 初始化客户端（使用兼容性包装器）
    print("🔧 正在初始化AI服务...")
    client = asyncio.run(initialize_openai_client())
    if not client:
        print("❌ AI服务初始化失败")
        return

    # 初始化对话历史
    conversation_history = []
    
    print("✅ 聊天机器人已启动！")
    print("📝 输入 'help' 或 '帮助' 查看可用命令")
    print("🚪 输入 'quit', 'exit' 或 '退出' 来结束对话\n")

    # 主对话循环
    while True:
        try:
            # 获取用户输入
            user_input = input("👤 您: ").strip()

            # 处理退出命令
            if user_input.lower() in ["quit", "exit", "退出", "q"]:
                print("👋 再见！感谢使用智能聊天助手！")
                break

            # 处理清空命令
            if user_input.lower() in ["clear", "清空", "c"]:
                conversation_history = []
                print("🗑️ 对话历史已清空\n")
                continue

            # 处理帮助命令
            if user_input.lower() in ["help", "帮助", "h"]:
                print_help()
                continue

            # 处理状态命令
            if user_input.lower() in ["status", "状态", "s"]:
                print_status(client)
                continue

            # 处理调试命令
            if user_input.lower() in ["debug", "调试", "d"]:
                print_debug_info(conversation_history, client)
                continue

            # 处理会话管理命令
            if user_input.lower() in ["sessions", "会话"]:
                print("📋 会话管理功能正在开发中...")
                print("   • 会话列表")
                print("   • 会话切换")
                print("   • 会话删除")
                print("   敬请期待！\n")
                continue

            # 处理空输入
            if not user_input:
                print("⚠️ 请输入有效的问题或命令\n")
                continue

            # 获取AI响应
            print("🤖 AI正在思考...")
            
            try:
                response = asyncio.run(get_chatbot_response(client, user_input, conversation_history))
                
                # 检查响应是否是错误消息
                if response.startswith("抱歉，发生了错误：") or response.startswith("获取响应失败:"):
                    print(f"❌ {response}")
                else:
                    print(f"🤖 助手: {response}")
                    
                    # 更新对话历史
                    conversation_history = manage_conversation_history(
                        conversation_history, user_input, response, MAX_CONVERSATION_HISTORY
                    )
                
                print()  # 添加空行

            except Exception as e:
                print(f"❌ 获取响应时发生错误: {str(e)}")
                print("🔄 请重试...\n")

        except KeyboardInterrupt:
            print("\n👋 检测到中断信号，正在退出...")
            break
            
        except EOFError:
            print("\n👋 输入结束，再见！")
            break
            
        except Exception as e:
            print(f"❌ 意外错误: {str(e)}")
            print("🔄 请重试...\n")


def run_enhanced_cli_interface():
    """
    运行增强版CLI界面
    提供更多交互功能和更好的用户体验
    """
    
    print_banner()
    print("🚀 增强版CLI启动中...")
    
    # 检查是否有命令行参数
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command in ["--help", "-h", "help"]:
            print_help()
            return
            
        elif command in ["--version", "-v", "version"]:
            print("版本: 重构架构 v2.0")
            return
            
        elif command in ["--status", "status"]:
            import asyncio
            client = asyncio.run(initialize_openai_client())
            print_status(client)
            return
    
    # 运行标准CLI界面
    run_cli_interface()


def run_interactive_setup():
    """
    运行交互式设置向导
    帮助用户配置环境和API密钥
    """
    print("🛠️ 交互式设置向导")
    print("=" * 50)
    
    # 检查API密钥
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ 未检测到OpenAI API密钥")
        print("请按以下步骤设置：")
        print("1. 访问 https://platform.openai.com/api-keys")
        print("2. 创建新的API密钥")
        print("3. 设置环境变量: export OPENAI_API_KEY='your-key-here'")
        print("4. 或创建 .env 文件并添加: OPENAI_API_KEY=your-key-here")
        
        # 询问是否要临时设置
        temp_key = input("\n🔑 输入临时API密钥（回车跳过）: ").strip()
        if temp_key:
            os.environ["OPENAI_API_KEY"] = temp_key
            print("✅ 临时API密钥已设置")
    else:
        print(f"✅ API密钥已配置: {api_key[:8]}...")
    
    print("\n🎯 设置完成！现在可以开始使用聊天机器人了。")
    print("运行 'python main.py' 启动CLI界面")
    print("运行 'uv run streamlit run main.py' 启动Web界面")


if __name__ == "__main__":
    # 检查特殊命令
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        run_interactive_setup()
    else:
        run_enhanced_cli_interface() 