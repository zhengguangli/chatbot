"""
会话管理接口定义
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class ChatSession:
    """聊天会话数据模型"""
    session_id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    model_config: Dict[str, Any]
    metadata: Dict[str, Any]
    is_active: bool = True


@dataclass
class Message:
    """消息数据模型"""
    message_id: str
    session_id: str
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: datetime
    metadata: Dict[str, Any]


class ISessionManager(ABC):
    """
    会话管理抽象接口
    负责聊天会话的创建、管理和持久化
    """
    
    @abstractmethod
    async def create_session(
        self,
        user_id: str,
        title: Optional[str] = None,
        model_config: Optional[Dict[str, Any]] = None
    ) -> ChatSession:
        """
        创建新的聊天会话
        
        Args:
            user_id: 用户ID
            title: 会话标题
            model_config: 模型配置
            
        Returns:
            ChatSession: 新创建的会话
        """
        pass
    
    @abstractmethod
    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        """
        获取指定会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            ChatSession或None: 会话对象
        """
        pass
    
    @abstractmethod
    async def update_session(
        self,
        session_id: str,
        title: Optional[str] = None,
        model_config: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        更新会话信息
        
        Args:
            session_id: 会话ID
            title: 新标题
            model_config: 新模型配置
            metadata: 新元数据
            
        Returns:
            bool: 更新是否成功
        """
        pass
    
    @abstractmethod
    async def delete_session(self, session_id: str) -> bool:
        """
        删除会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            bool: 删除是否成功
        """
        pass
    
    @abstractmethod
    async def get_user_sessions(
        self,
        user_id: str,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[ChatSession]:
        """
        获取用户的会话列表
        
        Args:
            user_id: 用户ID
            limit: 返回数量限制
            offset: 偏移量
            
        Returns:
            List[ChatSession]: 会话列表
        """
        pass
    
    @abstractmethod
    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Message:
        """
        添加消息到会话
        
        Args:
            session_id: 会话ID
            role: 消息角色
            content: 消息内容
            metadata: 消息元数据
            
        Returns:
            Message: 新添加的消息
        """
        pass
    
    @abstractmethod
    async def get_session_messages(
        self,
        session_id: str,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Message]:
        """
        获取会话的消息历史
        
        Args:
            session_id: 会话ID
            limit: 返回数量限制
            offset: 偏移量
            
        Returns:
            List[Message]: 消息列表
        """
        pass
    
    @abstractmethod
    async def clear_session_messages(self, session_id: str) -> bool:
        """
        清空会话消息
        
        Args:
            session_id: 会话ID
            
        Returns:
            bool: 清空是否成功
        """
        pass 