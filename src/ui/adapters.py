"""
UI适配器
连接新服务架构和现有UI接口的桥梁
"""

import asyncio
from typing import List, Dict, Any, Optional, Tuple
import logging
import uuid

from services import ServiceContainer, ServiceConfig
from interfaces.model_provider import ModelConfig
from interfaces.message_handler import MessageContext
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
        try:
            if self._initialized:
                return True
            
            # 创建服务配置
            config = ServiceConfig(
                storage_path="./data",
                openai_api_key=self.openai_api_key,
                log_level="INFO"
            )
            
            # 创建和初始化服务容器
            self.container = ServiceContainer(config)
            success = await self.container.initialize()
            
            if success:
                # 创建默认用户
                self.current_user = create_default_user()
                
                # 创建默认会话
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
            self.logger.error(f"UI适配器初始化失败: {e}")
            return False
    
    async def get_chatbot_response(
        self,
        user_input: str,
        conversation_history: List[Dict[str, str]]
    ) -> str:
        """
        获取聊天机器人响应
        兼容原有接口，内部使用新服务架构
        
        Args:
            user_input: 用户输入
            conversation_history: 对话历史
            
        Returns:
            str: AI响应内容
        """
        try:
            if not self._initialized:
                await self.initialize()
            
            if not self.container:
                return "服务容器未初始化"
            
            # 获取服务
            message_handler = self.container.get_message_handler()
            provider_registry = self.container.get_model_provider_registry()
            session_manager = self.container.get_session_manager()
            
            if not all([message_handler, provider_registry, session_manager]):
                return "关键服务未就绪"
            
            # 处理用户消息
            context = MessageContext(
                session_id=self.current_session_id or "",
                user_id=self.current_user.user_id if self.current_user else "default",
                conversation_history=conversation_history,
                system_settings={},
                user_preferences={}
            )
            
            if not message_handler:
                return "消息处理器不可用"
            
            processed_message = await message_handler.process_user_message(
                user_input, context
            )
            
            if not processed_message.is_valid:
                return f"消息处理失败: {processed_message.error_message}"
            
            # 添加消息到会话
            if self.current_session_id and session_manager:
                await session_manager.add_message(
                    self.current_session_id,
                    "user",
                    processed_message.content
                )
            
            # 准备AI上下文
            ai_messages = await message_handler.prepare_context_for_ai(
                processed_message.content,
                context
            )
            
            # 获取AI提供者
            if not provider_registry:
                return "AI提供者注册表不可用"
            
            provider = provider_registry.get_provider()
            if not provider:
                return "AI服务暂时不可用，请稍后重试。"
            
            # 创建模型配置
            model_config = ModelConfig(
                model_name="gpt-3.5-turbo",
                provider="openai",
                temperature=0.7,
                max_tokens=2000
            )
            
            # 生成AI响应
            response = await provider.generate_response(ai_messages, model_config)
            
            # 格式化响应
            formatted_response = await message_handler.format_response(
                response.content,
                context
            )
            
            # 添加AI响应到会话
            if self.current_session_id and session_manager:
                await session_manager.add_message(
                    self.current_session_id,
                    "assistant",
                    formatted_response
                )
            
            return formatted_response
            
        except Exception as e:
            self.logger.error(f"获取AI响应失败: {e}")
            return f"抱歉，发生了错误：{str(e)}"
    
    def manage_conversation_history(
        self,
        conversation_history: List[Dict[str, str]],
        user_input: str,
        response: str,
        max_history: int = 20
    ) -> List[Dict[str, str]]:
        """
        管理对话历史
        兼容原有接口
        
        Args:
            conversation_history: 当前对话历史
            user_input: 用户输入
            response: AI响应
            max_history: 最大历史条数
            
        Returns:
            List[Dict[str, str]]: 更新后的对话历史
        """
        try:
            # 添加新的对话
            new_history = conversation_history.copy()
            new_history.append({"role": "user", "content": user_input})
            new_history.append({"role": "assistant", "content": response})
            
            # 保持历史记录在限制范围内
            if len(new_history) > max_history:
                # 保留最近的对话
                new_history = new_history[-max_history:]
            
            return new_history
            
        except Exception as e:
            self.logger.error(f"管理对话历史失败: {e}")
            return conversation_history
    
    async def check_environment(self) -> Tuple[List[str], List[str]]:
        """
        检查环境状态
        兼容原有接口
        
        Returns:
            Tuple[List[str], List[str]]: (问题列表, 警告列表)
        """
        issues = []
        warnings = []
        
        try:
            if not self._initialized:
                await self.initialize()
            
            if not self.container:
                issues.append("服务容器初始化失败")
                return issues, warnings
            
            # 检查服务状态
            status = self.container.get_service_status()
            
            for service_name, is_ok in status.items():
                if not is_ok:
                    issues.append(f"{service_name} 服务不可用")
            
            # 检查OpenAI配置
            if not self.openai_api_key:
                warnings.append("OpenAI API密钥未设置")
            
            # 检查数据目录
            storage_service = self.container.get_storage_service()
            if storage_service:
                try:
                    stats = await storage_service.get_collection_stats("sessions")
                    if not stats.get("exists"):
                        warnings.append("会话数据集合不存在，将自动创建")
                except Exception as e:
                    warnings.append(f"存储服务检查失败: {e}")
            
        except Exception as e:
            issues.append(f"环境检查失败: {e}")
        
        return issues, warnings
    
    async def create_new_session(self, title: Optional[str] = None) -> bool:
        """
        创建新会话
        
        Args:
            title: 会话标题
            
        Returns:
            bool: 创建是否成功
        """
        try:
            if not self._initialized:
                await self.initialize()
            
            session_manager = self.container.get_session_manager()
            if not session_manager or not self.current_user:
                return False
            
            session = await session_manager.create_session(
                self.current_user.user_id,
                title or f"新会话 - {uuid.uuid4().hex[:8]}"
            )
            
            self.current_session_id = session.session_id
            self.logger.info(f"创建新会话: {session.session_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"创建新会话失败: {e}")
            return False
    
    async def get_session_list(self) -> List[Dict[str, Any]]:
        """
        获取用户会话列表
        
        Returns:
            List[Dict[str, Any]]: 会话信息列表
        """
        try:
            if not self._initialized:
                await self.initialize()
            
            session_manager = self.container.get_session_manager()
            if not session_manager or not self.current_user:
                return []
            
            sessions = await session_manager.get_user_sessions(
                self.current_user.user_id
            )
            
            return [
                {
                    "session_id": session.session_id,
                    "title": session.title,
                    "created_at": session.created_at.isoformat(),
                    "updated_at": session.updated_at.isoformat(),
                    "message_count": getattr(session, 'message_count', 0)
                }
                for session in sessions
            ]
            
        except Exception as e:
            self.logger.error(f"获取会话列表失败: {e}")
            return []
    
    async def switch_session(self, session_id: str) -> bool:
        """
        切换到指定会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            bool: 切换是否成功
        """
        try:
            if not self._initialized:
                await self.initialize()
            
            session_manager = self.container.get_session_manager()
            if not session_manager:
                return False
            
            session = await session_manager.get_session(session_id)
            if session:
                self.current_session_id = session_id
                self.logger.info(f"切换到会话: {session_id}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"切换会话失败: {e}")
            return False
    
    async def close(self):
        """关闭适配器和服务"""
        try:
            if self.container:
                await self.container.shutdown()
            self._initialized = False
            self.logger.info("UI适配器已关闭")
            
        except Exception as e:
            self.logger.error(f"关闭UI适配器失败: {e}")


# 全局适配器实例
_global_adapter: Optional[UIAdapter] = None


def get_global_adapter(openai_api_key: Optional[str] = None) -> UIAdapter:
    """获取全局UI适配器实例"""
    global _global_adapter
    
    if _global_adapter is None:
        _global_adapter = UIAdapter(openai_api_key)
    
    return _global_adapter


def run_async_safely(coro):
    """安全运行异步函数"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # 如果已有事件循环在运行（如在Jupyter中），创建任务
            return asyncio.create_task(coro)
        else:
            # 否则直接运行
            return loop.run_until_complete(coro)
    except RuntimeError:
        # 如果没有事件循环，创建新的
        return asyncio.run(coro) 