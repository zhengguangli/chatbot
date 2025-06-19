"""
聊天机器人核心逻辑模块
"""

from ..config.settings import (
    DEFAULT_MODEL,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TEMPERATURE,
    DEFAULT_TIMEOUT,
    SYSTEM_MESSAGE,
    MAX_CONVERSATION_HISTORY,
)
from ..utils.errors import handle_api_error


def get_chatbot_response(client, user_input, conversation_history):
    """获取聊天机器人响应"""
    if not client:
        return "❌ 客户端未初始化，请检查配置"

    if not user_input or not user_input.strip():
        return "请输入有效的问题"

    try:
        # 构建消息历史
        messages = [
            {
                "role": "system",
                "content": SYSTEM_MESSAGE,
            },
        ]

        # 添加对话历史
        for msg in conversation_history:
            if isinstance(msg, dict) and "role" in msg and "content" in msg:
                messages.append(msg)

        # 添加用户输入
        messages.append({"role": "user", "content": user_input.strip()})

        # 调用OpenAI API
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=messages,
            max_tokens=DEFAULT_MAX_TOKENS,
            temperature=DEFAULT_TEMPERATURE,
            timeout=DEFAULT_TIMEOUT,
        )

        if response.choices and len(response.choices) > 0:
            return response.choices[0].message.content
        else:
            return "❌ 未收到有效回复，请重试"

    except Exception as e:
        return handle_api_error(e)


def manage_conversation_history(history, new_user_msg, new_bot_msg, max_length=None):
    """管理对话历史"""
    if max_length is None:
        max_length = MAX_CONVERSATION_HISTORY

    history.append({"role": "user", "content": new_user_msg})
    history.append({"role": "assistant", "content": new_bot_msg})

    # 限制历史长度
    if len(history) > max_length:
        return history[-max_length:]
    return history
