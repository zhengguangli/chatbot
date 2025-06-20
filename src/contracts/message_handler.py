"""
消息处理接口定义
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum


class MessageType(Enum):
    """消息类型枚举"""
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    COMMAND = "command"
    SYSTEM = "system"


@dataclass
class ProcessedMessage:
    """处理后的消息"""
    content: str
    message_type: MessageType
    metadata: Dict[str, Any]
    attachments: List[Dict[str, Any]]
    is_valid: bool
    error_message: Optional[str] = None


@dataclass
class MessageContext:
    """消息上下文"""
    session_id: str
    user_id: str
    conversation_history: List[Dict[str, str]]
    user_preferences: Dict[str, Any]
    system_settings: Dict[str, Any]


class IMessageHandler(ABC):
    """
    消息处理抽象接口
    负责消息的验证、转换、路由和预处理
    """
    
    @abstractmethod
    async def process_user_message(
        self,
        raw_message: str,
        context: MessageContext
    ) -> ProcessedMessage:
        """
        处理用户输入消息
        
        Args:
            raw_message: 原始消息内容
            context: 消息上下文
            
        Returns:
            ProcessedMessage: 处理后的消息
        """
        pass
    
    @abstractmethod
    async def validate_message(
        self,
        message: str,
        message_type: MessageType
    ) -> bool:
        """
        验证消息格式和内容
        
        Args:
            message: 消息内容
            message_type: 消息类型
            
        Returns:
            bool: 消息是否有效
        """
        pass
    
    @abstractmethod
    async def format_response(
        self,
        response_content: str,
        context: MessageContext,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        格式化AI响应内容
        
        Args:
            response_content: AI原始响应
            context: 消息上下文
            metadata: 响应元数据
            
        Returns:
            str: 格式化后的响应
        """
        pass
    
    @abstractmethod
    async def extract_commands(
        self,
        message: str
    ) -> List[Dict[str, Any]]:
        """
        从消息中提取命令
        
        Args:
            message: 消息内容
            
        Returns:
            List[Dict[str, Any]]: 命令列表
        """
        pass
    
    @abstractmethod
    async def handle_file_attachment(
        self,
        file_data: bytes,
        file_name: str,
        mime_type: str,
        context: MessageContext
    ) -> Dict[str, Any]:
        """
        处理文件附件
        
        Args:
            file_data: 文件数据
            file_name: 文件名
            mime_type: MIME类型
            context: 消息上下文
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        pass
    
    @abstractmethod
    async def prepare_context_for_ai(
        self,
        current_message: str,
        context: MessageContext,
        max_history_length: int = 10
    ) -> List[Dict[str, str]]:
        """
        为AI模型准备上下文信息
        
        Args:
            current_message: 当前消息
            context: 消息上下文
            max_history_length: 最大历史长度
            
        Returns:
            List[Dict[str, str]]: 格式化的消息历史
        """
        pass
    
    @abstractmethod
    async def apply_content_filters(
        self,
        content: str,
        filter_type: str = "both"  # "input", "output", "both"
    ) -> str:
        """
        应用内容过滤器
        
        Args:
            content: 内容
            filter_type: 过滤类型
            
        Returns:
            str: 过滤后的内容
        """
        pass
    
    @abstractmethod
    def get_supported_message_types(self) -> List[MessageType]:
        """
        获取支持的消息类型
        
        Returns:
            List[MessageType]: 支持的消息类型列表
        """
        pass
    
    @abstractmethod
    async def calculate_message_cost(
        self,
        message: str,
        response: str,
        model_config: Dict[str, Any]
    ) -> Dict[str, Union[int, float]]:
        """
        计算消息处理成本
        
        Args:
            message: 输入消息
            response: 响应消息
            model_config: 模型配置
            
        Returns:
            Dict[str, Union[int, float]]: 成本信息
        """
        pass 