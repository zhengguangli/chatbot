"""
聊天机器人核心逻辑模块
"""
from config import global_config_manager
from utils.errors import handle_api_error


def get_chatbot_response(client, user_input, conversation_history):
    """获取聊天机器人响应"""
    if not client:
        return "❌ 客户端未初始化，请检查配置"

    if not user_input or not user_input.strip():
        return "请输入有效的问题"

    try:
        # 从配置管理器获取参数
        model_name = global_config_manager.get_config_value("model.model_name")
        max_tokens = global_config_manager.get_config_value("model.max_tokens")
        temperature = global_config_manager.get_config_value("model.temperature")
        timeout = global_config_manager.get_config_value("model.timeout")
        system_message = global_config_manager.get_config_value("conversation.system_message")

        # 构建消息历史
        messages = [
            {
                "role": "system",
                "content": system_message,
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
            model=model_name,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            timeout=timeout,
        )

        if response.choices and len(response.choices) > 0:
            return response.choices[0].message.content
        else:
            return "❌ 未收到有效回复，请重试"

    except Exception as e:
        return handle_api_error(e)


def manage_conversation_history(history, new_user_msg, new_bot_msg):
    """管理对话历史"""
    max_length = global_config_manager.get_config_value("conversation.max_history")

    history.append({"role": "user", "content": new_user_msg})
    history.append({"role": "assistant", "content": new_bot_msg})

    # 限制历史长度
    if len(history) > max_length:
        return history[-max_length:]
    return history
