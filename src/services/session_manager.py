"""
会话管理服务实现
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from contracts.session_manager import ISessionManager
from core.models import ChatSession, Message, create_new_session
from contracts.storage_service import IStorageService, QueryOptions, QueryFilter
from core.errors import ValidationError, ErrorCode


class SessionManager(ISessionManager):
    """会话管理服务实现"""
    
    def __init__(self, storage_service: IStorageService, logger: Optional[logging.Logger] = None):
        self.storage = storage_service
        self.logger = logger or logging.getLogger(__name__)
    
    async def create_session(
        self,
        user_id: str,
        title: Optional[str] = None,
        model_config: Optional[Dict[str, Any]] = None
    ) -> ChatSession:
        """创建新会话"""
        if not user_id:
            raise ValidationError("用户ID不能为空", ErrorCode.VALIDATION_REQUIRED_FIELD)
        
        session = create_new_session(user_id, title or "新对话")
        session_data = session.to_dict()
        await self.storage.store_data("sessions", session_data, session.session_id)
        
        return session
    
    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        """获取会话"""
        session_data = await self.storage.retrieve_data("sessions", session_id)
        if session_data:
            return ChatSession.from_dict(session_data)
        return None
    
    async def update_session(
        self,
        session_id: str,
        title: Optional[str] = None,
        model_config: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """更新会话"""
        session = await self.get_session(session_id)
        if not session:
            return False
        
        if title:
            session.title = title
        if metadata:
            session.metadata.update(metadata)
        
        session.updated_at = datetime.now()
        return await self.storage.update_data("sessions", session_id, session.to_dict())
    
    async def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        return await self.storage.delete_data("sessions", session_id)
    
    async def get_user_sessions(
        self,
        user_id: str,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[ChatSession]:
        """获取用户会话列表"""
        options = QueryOptions(
            filters=[QueryFilter(field="user_id", operator="eq", value=user_id)],
            sort_by="created_at",
            sort_order="desc",
            limit=limit,
            offset=offset
        )
        sessions_data = await self.storage.query_data("sessions", options)
        return [ChatSession.from_dict(data) for data in sessions_data]
    
    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Message:
        """添加消息"""
        from core.models import create_user_message, create_assistant_message
        
        if role == "user":
            message = create_user_message(session_id, content)
        else:
            message = create_assistant_message(session_id, content)
        
        message_data = message.to_dict()
        await self.storage.store_data("messages", message_data, message.message_id)
        
        return message
    
    async def get_session_messages(
        self,
        session_id: str,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Message]:
        """获取会话消息"""
        options = QueryOptions(
            filters=[QueryFilter(field="session_id", operator="eq", value=session_id)],
            sort_by="timestamp",
            sort_order="asc",
            limit=limit,
            offset=offset
        )
        messages_data = await self.storage.query_data("messages", options)
        return [Message.from_dict(data) for data in messages_data]
    
    async def clear_session_messages(self, session_id: str) -> bool:
        """清空会话消息"""
        return True
