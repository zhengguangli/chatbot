"""
重构架构的核心接口定义
"""

from .model_provider import IModelProvider
from .session_manager import ISessionManager  
from .message_handler import IMessageHandler
from .storage_service import IStorageService

__all__ = [
    "IModelProvider",
    "ISessionManager", 
    "IMessageHandler",
    "IStorageService",
] 