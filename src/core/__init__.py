"""
核心业务逻辑模块
重构后的模块化架构，包含接口、模型、错误处理和配置管理
"""

# 向后兼容的导出将通过延迟导入处理
# from .client import initialize_openai_client
# from .chatbot import get_chatbot_response, manage_conversation_history

def initialize_openai_client(*args, **kwargs):
    """延迟导入以避免循环导入"""
    from .client import initialize_openai_client as _initialize_openai_client
    return _initialize_openai_client(*args, **kwargs)

def get_chatbot_response(*args, **kwargs):
    """延迟导入以避免循环导入"""
    from .chatbot import get_chatbot_response as _get_chatbot_response
    return _get_chatbot_response(*args, **kwargs)

def manage_conversation_history(*args, **kwargs):
    """延迟导入以避免循环导入"""
    from .chatbot import manage_conversation_history as _manage_conversation_history
    return _manage_conversation_history(*args, **kwargs)

# 新架构组件导出
from .models import (
    # 数据模型
    User, ChatSession, Message, ModelConfiguration, ConversationContext,
    ModelResponse, ProcessingResult,
    # 枚举类型
    UserRole, MessageRole, SessionStatus, ModelProvider,
    # 工厂函数
    create_default_user, create_new_session, 
    create_user_message, create_assistant_message
)

from .errors import (
    # 异常类
    ChatBotError, NetworkError, APIError, ValidationError, 
    BusinessError, SystemError, ConfigError,
    # 枚举和配置
    ErrorCategory, ErrorLevel, ErrorCode, ErrorContext,
    RetryConfig, RetryHandler, ErrorHandler,
    # 工具函数
    create_network_error, create_api_error, create_validation_error,
    create_business_error, create_system_error, create_config_error,
    # 全局实例
    global_error_handler, global_retry_handler
)

# 向后兼容的导出
__all__ = [
    # 原有API
    "initialize_openai_client",
    "get_chatbot_response", 
    "manage_conversation_history",
    
    # 数据模型
    "User", "ChatSession", "Message", "ModelConfiguration", 
    "ConversationContext", "ModelResponse", "ProcessingResult",
    
    # 枚举类型
    "UserRole", "MessageRole", "SessionStatus", "ModelProvider",
    "ErrorCategory", "ErrorLevel", "ErrorCode",
    
    # 异常类
    "ChatBotError", "NetworkError", "APIError", "ValidationError",
    "BusinessError", "SystemError", "ConfigError",
    
    # 管理器和处理器
    "ErrorHandler", "RetryHandler",
    
    # 工厂函数
    "create_default_user", "create_new_session",
    "create_user_message", "create_assistant_message",
    "create_network_error", "create_api_error", "create_validation_error",
    "create_business_error", "create_system_error", "create_config_error",
    
    # 全局实例
    "global_error_handler", "global_retry_handler",
    
    # 配置和常量
    "ErrorContext", "RetryConfig"
]
