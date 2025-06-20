"""
应用设置和常量
"""

# OpenAI配置
# DEFAULT_MODEL = "qwen3"
DEFAULT_MODEL = "qwen3:4b"
DEFAULT_MAX_TOKENS = 2048
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TIMEOUT = 30

# 对话配置
MAX_CONVERSATION_HISTORY = 20
SYSTEM_MESSAGE = (
    "你是一个友好的中文助手，可以回答各种问题并进行对话。请保持回答简洁明了。"
)

# 界面配置
APP_TITLE = "🤖 智能聊天机器人"
APP_DESCRIPTION = "欢迎使用基于OpenAI的智能聊天机器人！"

# CLI提示信息
CLI_HELP_MESSAGE = """
💡 解决方案：
   1. 创建 .env 文件并设置 OPENAI_API_KEY=your_api_key
   2. 或者运行: export OPENAI_API_KEY=your_api_key

📋 可选配置项：
   • OPENAI_API_BASE=https://api.openai.com/v1  # 自定义API端点
   • OPENAI_ORG_ID=your_organization_id        # 组织ID
   • OPENAI_PROJECT_ID=your_project_id          # 项目ID
   • OPENAI_TIMEOUT=30                          # 超时时间（秒）
"""
