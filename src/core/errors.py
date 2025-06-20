"""
错误处理系统
分层异常处理，支持错误分类、中文友好消息和自动重试
"""

from enum import Enum
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from datetime import datetime
import traceback
import logging


# ============ 错误分类和级别 ============

class ErrorCategory(Enum):
    """错误分类"""
    NETWORK = "network"           # 网络相关错误
    API = "api"                  # API调用错误
    VALIDATION = "validation"     # 数据验证错误
    BUSINESS = "business"        # 业务逻辑错误
    SYSTEM = "system"            # 系统错误
    CONFIG = "config"            # 配置错误
    PERMISSION = "permission"     # 权限错误
    RESOURCE = "resource"        # 资源错误


class ErrorLevel(Enum):
    """错误级别"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorCode(Enum):
    """预定义错误代码"""
    # 网络错误 (1000-1099)
    NETWORK_TIMEOUT = "NETWORK_TIMEOUT"
    NETWORK_CONNECTION_FAILED = "NETWORK_CONNECTION_FAILED"
    NETWORK_UNAVAILABLE = "NETWORK_UNAVAILABLE"
    
    # API错误 (1100-1199)
    API_KEY_INVALID = "API_KEY_INVALID"
    API_QUOTA_EXCEEDED = "API_QUOTA_EXCEEDED"
    API_RATE_LIMITED = "API_RATE_LIMITED"
    API_MODEL_NOT_FOUND = "API_MODEL_NOT_FOUND"
    API_REQUEST_INVALID = "API_REQUEST_INVALID"
    
    # 验证错误 (1200-1299)
    VALIDATION_REQUIRED_FIELD = "VALIDATION_REQUIRED_FIELD"
    VALIDATION_INVALID_FORMAT = "VALIDATION_INVALID_FORMAT"
    VALIDATION_OUT_OF_RANGE = "VALIDATION_OUT_OF_RANGE"
    VALIDATION_TYPE_MISMATCH = "VALIDATION_TYPE_MISMATCH"
    
    # 业务错误 (1300-1399)
    BUSINESS_SESSION_NOT_FOUND = "BUSINESS_SESSION_NOT_FOUND"
    BUSINESS_USER_NOT_AUTHORIZED = "BUSINESS_USER_NOT_AUTHORIZED"
    BUSINESS_OPERATION_NOT_ALLOWED = "BUSINESS_OPERATION_NOT_ALLOWED"
    BUSINESS_RESOURCE_CONFLICT = "BUSINESS_RESOURCE_CONFLICT"
    
    # 系统错误 (1400-1499)
    SYSTEM_OUT_OF_MEMORY = "SYSTEM_OUT_OF_MEMORY"
    SYSTEM_DISK_FULL = "SYSTEM_DISK_FULL"
    SYSTEM_PERMISSION_DENIED = "SYSTEM_PERMISSION_DENIED"
    SYSTEM_INTERNAL_ERROR = "SYSTEM_INTERNAL_ERROR"
    
    # 配置错误 (1500-1599)
    CONFIG_FILE_NOT_FOUND = "CONFIG_FILE_NOT_FOUND"
    CONFIG_INVALID_FORMAT = "CONFIG_INVALID_FORMAT"
    CONFIG_MISSING_REQUIRED = "CONFIG_MISSING_REQUIRED"
    CONFIG_VALUE_INVALID = "CONFIG_VALUE_INVALID"


# ============ 核心异常类 ============

@dataclass
class ErrorContext:
    """错误上下文信息"""
    timestamp: datetime = field(default_factory=datetime.now)
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    operation: Optional[str] = None
    request_id: Optional[str] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)


class ChatBotError(Exception):
    """聊天机器人基础异常类"""
    
    def __init__(
        self,
        message: str,
        error_code: Union[ErrorCode, str],
        category: ErrorCategory,
        level: ErrorLevel = ErrorLevel.ERROR,
        context: Optional[ErrorContext] = None,
        original_error: Optional[Exception] = None,
        suggestions: Optional[List[str]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code if isinstance(error_code, ErrorCode) else ErrorCode(error_code)
        self.category = category
        self.level = level
        self.context = context or ErrorContext()
        self.original_error = original_error
        self.suggestions = suggestions or []
        self.traceback_info = traceback.format_exc() if original_error else None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "message": self.message,
            "error_code": self.error_code.value,
            "category": self.category.value,
            "level": self.level.value,
            "timestamp": self.context.timestamp.isoformat(),
            "user_id": self.context.user_id,
            "session_id": self.context.session_id,
            "operation": self.context.operation,
            "request_id": self.context.request_id,
            "suggestions": self.suggestions,
            "original_error": str(self.original_error) if self.original_error else None,
            "additional_data": self.context.additional_data
        }
    
    def get_user_friendly_message(self) -> str:
        """获取用户友好的错误消息"""
        return ERROR_MESSAGES.get(self.error_code, self.message)


# ============ 具体异常类 ============

class NetworkError(ChatBotError):
    """网络相关错误"""
    
    def __init__(self, message: str, error_code: ErrorCode, **kwargs):
        super().__init__(
            message=message,
            error_code=error_code,
            category=ErrorCategory.NETWORK,
            **kwargs
        )


class APIError(ChatBotError):
    """API调用错误"""
    
    def __init__(self, message: str, error_code: ErrorCode, **kwargs):
        super().__init__(
            message=message,
            error_code=error_code,
            category=ErrorCategory.API,
            **kwargs
        )


class ValidationError(ChatBotError):
    """数据验证错误"""
    
    def __init__(self, message: str, error_code: ErrorCode, field_name: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            error_code=error_code,
            category=ErrorCategory.VALIDATION,
            level=ErrorLevel.WARNING,
            **kwargs
        )
        self.field_name = field_name


class BusinessError(ChatBotError):
    """业务逻辑错误"""
    
    def __init__(self, message: str, error_code: ErrorCode, **kwargs):
        super().__init__(
            message=message,
            error_code=error_code,
            category=ErrorCategory.BUSINESS,
            **kwargs
        )


class SystemError(ChatBotError):
    """系统错误"""
    
    def __init__(self, message: str, error_code: ErrorCode, **kwargs):
        super().__init__(
            message=message,
            error_code=error_code,
            category=ErrorCategory.SYSTEM,
            level=ErrorLevel.CRITICAL,
            **kwargs
        )


class ConfigError(ChatBotError):
    """配置错误"""
    
    def __init__(self, message: str, error_code: ErrorCode, **kwargs):
        super().__init__(
            message=message,
            error_code=error_code,
            category=ErrorCategory.CONFIG,
            **kwargs
        )


# ============ 中文友好错误消息 ============

ERROR_MESSAGES: Dict[ErrorCode, str] = {
    # 网络错误
    ErrorCode.NETWORK_TIMEOUT: "网络连接超时，请检查网络连接后重试",
    ErrorCode.NETWORK_CONNECTION_FAILED: "无法连接到服务器，请检查网络设置",
    ErrorCode.NETWORK_UNAVAILABLE: "网络不可用，请检查网络连接",
    
    # API错误
    ErrorCode.API_KEY_INVALID: "API密钥无效，请检查配置文件中的API密钥",
    ErrorCode.API_QUOTA_EXCEEDED: "API调用次数已用完，请等待配额重置或升级账户",
    ErrorCode.API_RATE_LIMITED: "API调用过于频繁，请稍后重试",
    ErrorCode.API_MODEL_NOT_FOUND: "指定的AI模型不存在，请检查模型名称",
    ErrorCode.API_REQUEST_INVALID: "API请求格式无效，请检查请求参数",
    
    # 验证错误
    ErrorCode.VALIDATION_REQUIRED_FIELD: "必填字段不能为空，请完整填写信息",
    ErrorCode.VALIDATION_INVALID_FORMAT: "数据格式不正确，请检查输入格式",
    ErrorCode.VALIDATION_OUT_OF_RANGE: "数值超出允许范围，请输入有效数值",
    ErrorCode.VALIDATION_TYPE_MISMATCH: "数据类型不匹配，请检查输入类型",
    
    # 业务错误
    ErrorCode.BUSINESS_SESSION_NOT_FOUND: "会话不存在或已过期，请创建新的对话",
    ErrorCode.BUSINESS_USER_NOT_AUTHORIZED: "用户未授权进行此操作，请检查权限",
    ErrorCode.BUSINESS_OPERATION_NOT_ALLOWED: "当前状态下不允许此操作，请稍后重试",
    ErrorCode.BUSINESS_RESOURCE_CONFLICT: "资源冲突，请刷新后重试",
    
    # 系统错误
    ErrorCode.SYSTEM_OUT_OF_MEMORY: "系统内存不足，请关闭其他应用程序后重试",
    ErrorCode.SYSTEM_DISK_FULL: "磁盘空间不足，请清理磁盘空间",
    ErrorCode.SYSTEM_PERMISSION_DENIED: "权限不足，请检查文件权限设置",
    ErrorCode.SYSTEM_INTERNAL_ERROR: "系统内部错误，请联系技术支持",
    
    # 配置错误
    ErrorCode.CONFIG_FILE_NOT_FOUND: "配置文件不存在，请检查配置文件路径",
    ErrorCode.CONFIG_INVALID_FORMAT: "配置文件格式错误，请检查配置语法",
    ErrorCode.CONFIG_MISSING_REQUIRED: "缺少必需的配置项，请完善配置",
    ErrorCode.CONFIG_VALUE_INVALID: "配置值无效，请检查配置项的值",
}


# ============ 解决建议 ============

ERROR_SUGGESTIONS: Dict[ErrorCode, List[str]] = {
    ErrorCode.NETWORK_TIMEOUT: [
        "检查网络连接是否正常",
        "尝试使用其他网络环境",
        "增加超时时间设置",
        "联系网络管理员"
    ],
    ErrorCode.API_KEY_INVALID: [
        "检查.env文件中的OPENAI_API_KEY是否正确",
        "确认API密钥没有过期",
        "重新生成API密钥",
        "检查API密钥格式是否正确"
    ],
    ErrorCode.API_QUOTA_EXCEEDED: [
        "等待配额重置（通常在月初）",
        "升级到更高级别的API计划",
        "优化请求以减少token使用",
        "使用其他API提供商"
    ],
    ErrorCode.CONFIG_FILE_NOT_FOUND: [
        "创建缺失的配置文件",
        "检查配置文件路径是否正确",
        "从示例配置文件复制",
        "重新运行初始化命令"
    ]
}


# ============ 错误处理工具 ============

class ErrorHandler:
    """错误处理器"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.error_registry: Dict[str, ChatBotError] = {}
    
    def handle_error(self, error: Exception, context: Optional[ErrorContext] = None) -> ChatBotError:
        """
        统一错误处理
        
        Args:
            error: 原始异常
            context: 错误上下文
            
        Returns:
            ChatBotError: 标准化的错误对象
        """
        if isinstance(error, ChatBotError):
            return error
        
        # 根据异常类型转换为标准错误
        if isinstance(error, ConnectionError):
            return NetworkError(
                message=str(error),
                error_code=ErrorCode.NETWORK_CONNECTION_FAILED,
                context=context,
                original_error=error,
                suggestions=ERROR_SUGGESTIONS.get(ErrorCode.NETWORK_CONNECTION_FAILED, [])
            )
        
        elif isinstance(error, TimeoutError):
            return NetworkError(
                message=str(error),
                error_code=ErrorCode.NETWORK_TIMEOUT,
                context=context,
                original_error=error,
                suggestions=ERROR_SUGGESTIONS.get(ErrorCode.NETWORK_TIMEOUT, [])
            )
        
        elif isinstance(error, ValueError):
            return ValidationError(
                message=str(error),
                error_code=ErrorCode.VALIDATION_INVALID_FORMAT,
                context=context,
                original_error=error
            )
        
        elif isinstance(error, FileNotFoundError):
            return ConfigError(
                message=str(error),
                error_code=ErrorCode.CONFIG_FILE_NOT_FOUND,
                context=context,
                original_error=error,
                suggestions=ERROR_SUGGESTIONS.get(ErrorCode.CONFIG_FILE_NOT_FOUND, [])
            )
        
        else:
            # 未知错误，归类为系统错误
            return SystemError(
                message=f"未知错误: {str(error)}",
                error_code=ErrorCode.SYSTEM_INTERNAL_ERROR,
                context=context,
                original_error=error
            )
    
    def log_error(self, error: ChatBotError):
        """记录错误到日志"""
        log_method = {
            ErrorLevel.INFO: self.logger.info,
            ErrorLevel.WARNING: self.logger.warning,
            ErrorLevel.ERROR: self.logger.error,
            ErrorLevel.CRITICAL: self.logger.critical
        }.get(error.level, self.logger.error)
        
        log_method(
            f"Error [{error.error_code.value}]: {error.message}",
            extra={
                "error_code": error.error_code.value,
                "category": error.category.value,
                "level": error.level.value,
                "context": error.context.__dict__ if error.context else {},
                "traceback": error.traceback_info
            }
        )
    
    def register_error(self, error_id: str, error: ChatBotError):
        """注册错误到错误注册表"""
        self.error_registry[error_id] = error
    
    def get_error(self, error_id: str) -> Optional[ChatBotError]:
        """从错误注册表获取错误"""
        return self.error_registry.get(error_id)


# ============ 重试机制 ============

@dataclass
class RetryConfig:
    """重试配置"""
    max_attempts: int = 3
    delay_seconds: float = 1.0
    backoff_multiplier: float = 2.0
    retry_on_errors: List[ErrorCode] = field(default_factory=lambda: [
        ErrorCode.NETWORK_TIMEOUT,
        ErrorCode.NETWORK_CONNECTION_FAILED,
        ErrorCode.API_RATE_LIMITED
    ])


class RetryHandler:
    """重试处理器"""
    
    def __init__(self, config: Optional[RetryConfig] = None):
        self.config = config or RetryConfig()
    
    def should_retry(self, error: ChatBotError, attempt: int) -> bool:
        """
        判断是否应该重试
        
        Args:
            error: 错误对象
            attempt: 当前尝试次数
            
        Returns:
            bool: 是否应该重试
        """
        return (
            attempt < self.config.max_attempts and
            error.error_code in self.config.retry_on_errors
        )
    
    def get_delay(self, attempt: int) -> float:
        """
        获取重试延迟时间
        
        Args:
            attempt: 当前尝试次数
            
        Returns:
            float: 延迟秒数
        """
        return self.config.delay_seconds * (self.config.backoff_multiplier ** (attempt - 1))


# ============ 快捷工具函数 ============

def create_network_error(message: str, **kwargs) -> NetworkError:
    """创建网络错误"""
    return NetworkError(message, ErrorCode.NETWORK_CONNECTION_FAILED, **kwargs)


def create_api_error(message: str, **kwargs) -> APIError:
    """创建API错误"""
    return APIError(message, ErrorCode.API_REQUEST_INVALID, **kwargs)


def create_validation_error(message: str, field_name: Optional[str] = None, **kwargs) -> ValidationError:
    """创建验证错误"""
    return ValidationError(message, ErrorCode.VALIDATION_INVALID_FORMAT, field_name=field_name, **kwargs)


def create_business_error(message: str, **kwargs) -> BusinessError:
    """创建业务错误"""
    return BusinessError(message, ErrorCode.BUSINESS_OPERATION_NOT_ALLOWED, **kwargs)


def create_system_error(message: str, **kwargs) -> SystemError:
    """创建系统错误"""
    return SystemError(message, ErrorCode.SYSTEM_INTERNAL_ERROR, **kwargs)


def create_config_error(message: str, **kwargs) -> ConfigError:
    """创建配置错误"""
    return ConfigError(message, ErrorCode.CONFIG_INVALID_FORMAT, **kwargs)


# ============ 全局错误处理器实例 ============

# 创建全局错误处理器实例
global_error_handler = ErrorHandler()
global_retry_handler = RetryHandler() 