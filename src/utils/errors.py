"""
统一错误处理工具模块
"""

import logging


# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChatbotError(Exception):
    """聊天机器人基础异常类"""

    pass


class ConfigurationError(ChatbotError):
    """配置错误"""

    pass


class ClientError(ChatbotError):
    """客户端错误"""

    pass


class APIError(ChatbotError):
    """API调用错误"""

    pass


def handle_api_error(error):
    """处理API错误并返回用户友好的消息"""
    error_msg = str(error).lower()

    if "timeout" in error_msg:
        return "⏰ 请求超时，请稍后重试"
    elif "api" in error_msg or "unauthorized" in error_msg:
        return "🔑 API调用错误，请检查密钥设置"
    elif "rate" in error_msg or "limit" in error_msg:
        return "🚦 请求过于频繁，请稍后再试"
    elif "network" in error_msg or "connection" in error_msg:
        return "🌐 网络连接错误，请检查网络设置"
    else:
        logger.error(f"未知API错误: {str(error)}")
        return f"❌ 发生错误：{str(error)}"


def handle_client_error(error):
    """处理客户端错误"""
    logger.error(f"客户端错误: {str(error)}")
    return f"❌ 客户端错误：{str(error)}"


def handle_configuration_error(error):
    """处理配置错误"""
    logger.error(f"配置错误: {str(error)}")
    return f"⚙️ 配置错误：{str(error)}"


def safe_execute(func, *args, error_handler=None, **kwargs):
    """安全执行函数，统一处理异常"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if error_handler:
            return error_handler(e)
        else:
            logger.error(f"执行错误: {str(e)}")
            return f"❌ 执行错误：{str(e)}"
