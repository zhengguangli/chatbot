"""
核心数据模型定义
统一的数据结构，支持序列化和验证
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum
from uuid import uuid4, UUID
import json


# ============ 枚举定义 ============

class UserRole(Enum):
    """用户角色"""
    GUEST = "guest"
    USER = "user"
    ADMIN = "admin"
    SYSTEM = "system"


class MessageRole(Enum):
    """消息角色"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class SessionStatus(Enum):
    """会话状态"""
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"
    DELETED = "deleted"


class ModelProvider(Enum):
    """模型提供者"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    LOCAL = "local"


# ============ 核心数据模型 ============

@dataclass
class User:
    """用户模型"""
    user_id: str = field(default_factory=lambda: str(uuid4()))
    username: str = ""
    display_name: str = ""
    role: UserRole = UserRole.USER
    email: Optional[str] = None
    preferences: Dict[str, Any] = field(default_factory=dict)
    usage_stats: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "display_name": self.display_name,
            "role": self.role.value,
            "email": self.email,
            "preferences": self.preferences,
            "usage_stats": self.usage_stats,
            "created_at": self.created_at.isoformat(),
            "last_active": self.last_active.isoformat(),
            "is_active": self.is_active,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """从字典创建"""
        return cls(
            user_id=data.get("user_id", str(uuid4())),
            username=data.get("username", ""),
            display_name=data.get("display_name", ""),
            role=UserRole(data.get("role", "user")),
            email=data.get("email"),
            preferences=data.get("preferences", {}),
            usage_stats=data.get("usage_stats", {}),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            last_active=datetime.fromisoformat(data.get("last_active", datetime.now().isoformat())),
            is_active=data.get("is_active", True),
            metadata=data.get("metadata", {})
        )


@dataclass
class ModelConfiguration:
    """模型配置"""
    model_name: str = "qwen3"
    provider: ModelProvider = ModelProvider.OPENAI
    temperature: float = 0.7
    max_tokens: int = 2000
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    timeout: int = 30
    stream: bool = False
    custom_params: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "model_name": self.model_name,
            "provider": self.provider.value,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "timeout": self.timeout,
            "stream": self.stream,
            "custom_params": self.custom_params
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModelConfiguration':
        """从字典创建"""
        return cls(
            model_name=data.get("model_name", "qwen3"),
            provider=ModelProvider(data.get("provider", "openai")),
            temperature=data.get("temperature", 0.7),
            max_tokens=data.get("max_tokens", 2000),
            top_p=data.get("top_p", 1.0),
            frequency_penalty=data.get("frequency_penalty", 0.0),
            presence_penalty=data.get("presence_penalty", 0.0),
            timeout=data.get("timeout", 30),
            stream=data.get("stream", False),
            custom_params=data.get("custom_params", {})
        )


@dataclass
class Message:
    """消息模型"""
    message_id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""
    role: MessageRole = MessageRole.USER
    content: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    token_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    parent_message_id: Optional[str] = None
    is_deleted: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "message_id": self.message_id,
            "session_id": self.session_id,
            "role": self.role.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "token_count": self.token_count,
            "metadata": self.metadata,
            "attachments": self.attachments,
            "parent_message_id": self.parent_message_id,
            "is_deleted": self.is_deleted
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """从字典创建"""
        return cls(
            message_id=data.get("message_id", str(uuid4())),
            session_id=data.get("session_id", ""),
            role=MessageRole(data.get("role", "user")),
            content=data.get("content", ""),
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat())),
            token_count=data.get("token_count", 0),
            metadata=data.get("metadata", {}),
            attachments=data.get("attachments", []),
            parent_message_id=data.get("parent_message_id"),
            is_deleted=data.get("is_deleted", False)
        )


@dataclass
class ChatSession:
    """聊天会话模型"""
    session_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""
    title: str = "新对话"
    description: str = ""
    status: SessionStatus = SessionStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_message_at: Optional[datetime] = None
    message_count: int = 0
    total_tokens: int = 0
    model_config: ModelConfiguration = field(default_factory=ModelConfiguration)
    settings: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_message_at": self.last_message_at.isoformat() if self.last_message_at else None,
            "message_count": self.message_count,
            "total_tokens": self.total_tokens,
            "model_config": self.model_config.to_dict(),
            "settings": self.settings,
            "tags": self.tags,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatSession':
        """从字典创建"""
        last_message_at = None
        if data.get("last_message_at"):
            last_message_at = datetime.fromisoformat(data["last_message_at"])
            
        return cls(
            session_id=data.get("session_id", str(uuid4())),
            user_id=data.get("user_id", ""),
            title=data.get("title", "新对话"),
            description=data.get("description", ""),
            status=SessionStatus(data.get("status", "active")),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat())),
            last_message_at=last_message_at,
            message_count=data.get("message_count", 0),
            total_tokens=data.get("total_tokens", 0),
            model_config=ModelConfiguration.from_dict(data.get("model_config", {})),
            settings=data.get("settings", {}),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {})
        )


@dataclass
class ConversationContext:
    """对话上下文"""
    session_id: str
    user_id: str
    current_message: str
    message_history: List[Message] = field(default_factory=list)
    system_prompts: List[str] = field(default_factory=list)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    session_settings: Dict[str, Any] = field(default_factory=dict)
    model_config: Optional[ModelConfiguration] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_formatted_history(self, max_messages: int = 10) -> List[Dict[str, str]]:
        """获取格式化的消息历史"""
        recent_messages = self.message_history[-max_messages:] if max_messages > 0 else self.message_history
        formatted = []
        
        # 添加系统提示
        for prompt in self.system_prompts:
            formatted.append({"role": "system", "content": prompt})
        
        # 添加历史消息
        for msg in recent_messages:
            if not msg.is_deleted:
                formatted.append({"role": msg.role.value, "content": msg.content})
        
        return formatted
    
    def calculate_total_tokens(self) -> int:
        """计算总token数"""
        return sum(msg.token_count for msg in self.message_history)


# ============ 响应模型 ============

@dataclass
class ModelResponse:
    """模型响应"""
    content: str
    usage_tokens: int
    model: str
    finish_reason: str = "stop"
    response_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "content": self.content,
            "usage_tokens": self.usage_tokens,
            "model": self.model,
            "finish_reason": self.finish_reason,
            "response_time": self.response_time,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class ProcessingResult:
    """处理结果"""
    success: bool
    data: Optional[Any] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "success": self.success,
            "data": self.data,
            "error_message": self.error_message,
            "error_code": self.error_code,
            "metadata": self.metadata,
            "processing_time": self.processing_time
        }


# ============ 工厂函数 ============

def create_default_user(username: str = "默认用户") -> User:
    """创建默认用户"""
    return User(
        username=username,
        display_name=username,
        role=UserRole.USER
    )


def create_new_session(user_id: str, title: str = "新对话") -> ChatSession:
    """创建新会话"""
    return ChatSession(
        user_id=user_id,
        title=title,
        model_config=ModelConfiguration()
    )


def create_user_message(session_id: str, content: str) -> Message:
    """创建用户消息"""
    return Message(
        session_id=session_id,
        role=MessageRole.USER,
        content=content
    )


def create_assistant_message(session_id: str, content: str, tokens: int = 0) -> Message:
    """创建助手消息"""
    return Message(
        session_id=session_id,
        role=MessageRole.ASSISTANT,
        content=content,
        token_count=tokens
    ) 