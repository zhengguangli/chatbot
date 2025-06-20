"""
消息处理服务实现
"""

from typing import Dict, List, Optional, Any
import logging
import asyncio

from ..interfaces.message_handler import (
    IMessageHandler, ProcessedMessage, MessageContext, MessageType
)
from ..core.errors import ValidationError, ErrorCode


class MessageHandler(IMessageHandler):
    """消息处理服务实现"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self._content_filters = ["spam", "malicious", "inappropriate"]
    
    async def process_user_message(
        self,
        raw_message: str,
        context: MessageContext
    ) -> ProcessedMessage:
        """处理用户输入消息"""
        try:
            # 基本验证
            if not raw_message or not raw_message.strip():
                return ProcessedMessage(
                    content="",
                    message_type=MessageType.TEXT,
                    metadata={},
                    attachments=[],
                    is_valid=False,
                    error_message="消息内容不能为空"
                )
            
            # 清理消息
            cleaned_content = raw_message.strip()
            
            # 检测消息类型
            message_type = MessageType.TEXT
            if cleaned_content.startswith('/'):
                message_type = MessageType.COMMAND
            
            # 应用内容过滤
            filtered_content = await self.apply_content_filters(cleaned_content, "input")
            
            return ProcessedMessage(
                content=filtered_content,
                message_type=message_type,
                metadata={
                    "original_length": len(raw_message),
                    "processed_length": len(filtered_content),
                    "session_id": context.session_id,
                    "user_id": context.user_id
                },
                attachments=[],
                is_valid=True
            )
            
        except Exception as e:
            self.logger.error(f"处理用户消息失败: {e}")
            return ProcessedMessage(
                content="",
                message_type=MessageType.TEXT,
                metadata={},
                attachments=[],
                is_valid=False,
                error_message=f"消息处理失败: {str(e)}"
            )
    
    async def validate_message(self, message: str, message_type: MessageType) -> bool:
        """验证消息格式和内容"""
        if not message:
            return False
        
        if message_type == MessageType.TEXT:
            return len(message.strip()) > 0
        elif message_type == MessageType.COMMAND:
            return message.startswith('/')
        
        return True
    
    async def format_response(
        self,
        response_content: str,
        context: MessageContext,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """格式化AI响应内容"""
        if not response_content:
            return ""
        
        # 应用输出过滤器
        filtered_response = await self.apply_content_filters(response_content, "output")
        
        # 添加基本格式化
        formatted_response = filtered_response.strip()
        
        return formatted_response
    
    async def extract_commands(self, message: str) -> List[Dict[str, Any]]:
        """从消息中提取命令"""
        commands = []
        
        if message.startswith('/'):
            parts = message[1:].split(' ', 1)
            command_name = parts[0]
            command_args = parts[1] if len(parts) > 1 else ""
            
            commands.append({
                "name": command_name,
                "args": command_args,
                "raw": message
            })
        
        return commands
    
    async def handle_file_attachment(
        self,
        file_data: bytes,
        file_name: str,
        mime_type: str,
        context: MessageContext
    ) -> Dict[str, Any]:
        """处理文件附件"""
        return {
            "success": False,
            "message": "文件上传功能暂未实现"
        }
    
    async def prepare_context_for_ai(
        self,
        current_message: str,
        context: MessageContext,
        max_history_length: int = 10
    ) -> List[Dict[str, str]]:
        """为AI模型准备上下文信息"""
        messages = []
        
        # 添加系统提示
        if context.system_settings.get("system_prompt"):
            messages.append({
                "role": "system",
                "content": context.system_settings["system_prompt"]
            })
        
        # 添加历史消息（简化版）
        for msg in context.conversation_history[-max_history_length:]:
            messages.append(msg)
        
        # 添加当前消息
        messages.append({
            "role": "user",
            "content": current_message
        })
        
        return messages
    
    async def apply_content_filters(
        self,
        content: str,
        filter_type: str = "both"
    ) -> str:
        """应用内容过滤器"""
        if not content:
            return content
        
        # 简单的内容过滤实现
        filtered_content = content
        
        # 移除一些明显的有害内容标识
        for filter_word in self._content_filters:
            filtered_content = filtered_content.replace(filter_word, "***")
        
        return filtered_content
    
    def get_supported_message_types(self) -> List[MessageType]:
        """获取支持的消息类型"""
        return [MessageType.TEXT, MessageType.COMMAND]
    
    async def calculate_message_cost(
        self,
        message: str,
        response: str,
        model_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """计算消息处理成本"""
        # 简化的成本计算
        input_tokens = len(message.split())
        output_tokens = len(response.split())
        
        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "estimated_cost": (input_tokens + output_tokens) * 0.0001  # 估算成本
        }
