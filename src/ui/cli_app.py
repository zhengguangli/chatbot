"""
命令行界面模块
"""

from ..core.client import initialize_openai_client
from ..core.chatbot import get_chatbot_response, manage_conversation_history
from ..config.environment import check_environment
from ..config.settings import CLI_HELP_MESSAGE, MAX_CONVERSATION_HISTORY


def run_cli_interface():
    """运行命令行界面"""
    print("🤖 聊天机器人启动中...")
    print("提示：运行 'uv run streamlit run main.py' 启动Web界面")

    # 环境检查
    env_issues, env_warnings = check_environment()
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

    # 初始化客户端
    client = initialize_openai_client()
    if not client:
        return

    conversation_history = []
    print("\n✅ 聊天机器人已启动！")
    print("💡 输入 'quit', 'exit' 或 '退出' 来结束对话")
    print("💡 输入 'clear' 或 '清空' 来清空对话历史\n")

    while True:
        try:
            user_input = input("👤 您: ").strip()

            if user_input.lower() in ["quit", "exit", "退出"]:
                print("👋 再见！")
                break

            if user_input.lower() in ["clear", "清空"]:
                conversation_history = []
                print("🗑️ 对话历史已清空\n")
                continue

            if not user_input:
                print("⚠️ 请输入有效的问题\n")
                continue

            print("🤖 AI正在思考...")
            response = get_chatbot_response(client, user_input, conversation_history)
            print(f"🤖 机器人: {response}\n")

            # 更新对话历史
            conversation_history = manage_conversation_history(
                conversation_history, user_input, response, MAX_CONVERSATION_HISTORY
            )

        except KeyboardInterrupt:
            print("\n👋 检测到中断，再见！")
            break
        except EOFError:
            print("\n👋 输入结束，再见！")
            break
        except Exception as e:
            print(f"❌ 意外错误：{str(e)}")
            print("🔄 请重试...\n")
