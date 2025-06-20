"""
核心业务逻辑模块
重构后的模块化架构，包含接口、模型、错误处理和配置管理
"""

# 保持向后兼容的原有导出
from .client import initialize_openai_client
from .chatbot import get_chatbot_response, manage_conversation_history

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

from .config import (
    # 配置管理
    ConfigManager, ConfigItem, ConfigFormat, ConfigSource,
    DEFAULT_CONFIG, SENSITIVE_KEYS,
    # 全局实例
    global_config_manager
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
    "ErrorCategory", "ErrorLevel", "ErrorCode", "ConfigFormat", "ConfigSource",
    
    # 异常类
    "ChatBotError", "NetworkError", "APIError", "ValidationError",
    "BusinessError", "SystemError", "ConfigError",
    
    # 管理器和处理器
    "ConfigManager", "ErrorHandler", "RetryHandler",
    
    # 工厂函数
    "create_default_user", "create_new_session",
    "create_user_message", "create_assistant_message",
    "create_network_error", "create_api_error", "create_validation_error",
    "create_business_error", "create_system_error", "create_config_error",
    
    # 全局实例
    "global_config_manager", "global_error_handler", "global_retry_handler",
    
    # 配置和常量
    "DEFAULT_CONFIG", "SENSITIVE_KEYS", "ErrorContext", "ConfigItem", "RetryConfig"
]
