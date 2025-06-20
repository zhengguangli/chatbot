"""
UI适配器
连接新服务架构和现有UI接口的桥梁
"""

import asyncio
from typing import List, Dict, Any, Optional, Tuple
import logging
import uuid

from services.service_container import ServiceContainer, ServiceConfig
from contracts.model_provider import ModelConfig
from contracts.message_handler import MessageContext
from core.models import User, create_default_user
from core.errors import ChatBotError


class UIAdapter:
    """
    UI适配器
    为现有UI提供兼容的接口，内部使用新的服务架构
    """
    
    def __init__(self, openai_api_key: Optional[str] = None):
        self.openai_api_key = openai_api_key
        self.logger = logging.getLogger(__name__)
        self.container: Optional[ServiceContainer] = None
        self.current_user: Optional[User] = None
        self.current_session_id: Optional[str] = None
        self._initialized = False
    
    async def initialize(self) -> bool:
        """初始化适配器和服务容器"""
        if self._initialized:
            return True
        
        try:
            config = ServiceConfig(
                storage_path="./data",
                openai_api_key=self.openai_api_key,
                log_level="INFO"
            )
            
            self.container = ServiceContainer(config)
            success = await self.container.initialize()
            
            if success:
                self.current_user = create_default_user()
                session_manager = self.container.get_session_manager()
                if session_manager:
                    session = await session_manager.create_session(
                        self.current_user.user_id,
                        "默认会话"
                    )
                    self.current_session_id = session.session_id
                
                self._initialized = True
                self.logger.info("UI适配器初始化成功")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"UI适配器初始化失败: {e}", exc_info=True)
            return False
    
    async def get_chatbot_response(
        self,
        user_input: str,
        conversation_history: List[Dict[str, str]]
    ) -> str:
        """获取聊天机器人响应"""
        if not self._initialized:
            await self.initialize()

        assert self.container is not None, "服务容器未初始化"
        
        message_handler = self.container.get_message_handler()
        provider_registry = self.container.get_model_provider_registry()
        session_manager = self.container.get_session_manager()

        assert message_handler is not None
        assert provider_registry is not None
        assert session_manager is not None

        context = MessageContext(
            session_id=self.current_session_id or "",
            user_id=self.current_user.user_id if self.current_user else "default",
            conversation_history=conversation_history,
            system_settings={},
            user_preferences={}
        )

        processed_message = await message_handler.process_user_message(
            user_input, context
        )

        if not processed_message.is_valid:
            return f"消息处理失败: {processed_message.error_message}"

        if self.current_session_id:
            await session_manager.add_message(
                self.current_session_id,
                "user",
                processed_message.content
            )

        ai_messages = await message_handler.prepare_context_for_ai(
            processed_message.content,
            context
        )

        provider = provider_registry.get_provider()
        if not provider:
            return "AI服务暂时不可用，请稍后重试。"

        model_config = ModelConfig(
            model_name="qwen3",
            provider="openai"
        )

        response = await provider.generate_response(ai_messages, model_config)

        formatted_response = await message_handler.format_response(
            response.content,
            context
        )

        if self.current_session_id:
            await session_manager.add_message(
                self.current_session_id,
                "assistant",
                formatted_response
            )
        
        return formatted_response

    def manage_conversation_history(
        self,
        conversation_history: List[Dict[str, str]],
        user_input: str,
        response: str,
        max_history: int = 20
    ) -> List[Dict[str, str]]:
        """管理对话历史"""
        new_history = conversation_history.copy()
        new_history.append({"role": "user", "content": user_input})
        new_history.append({"role": "assistant", "content": response})

        if len(new_history) > max_history:
            return new_history[-max_history:]
        
        return new_history

    async def close(self):
        """关闭适配器和服务"""
        if self.container:
            await self.container.shutdown()
        self._initialized = False
        self.logger.info("UI适配器已关闭")


# 全局适配器实例
_global_adapter: Optional[UIAdapter] = None

async def get_global_adapter(openai_api_key: Optional[str] = None) -> UIAdapter:
    """获取并初始化全局UI适配器实例"""
    global _global_adapter
    
    if _global_adapter is None:
        _global_adapter = UIAdapter(openai_api_key)
    
    if not _global_adapter._initialized:
        await _global_adapter.initialize()

    return _global_adapter 