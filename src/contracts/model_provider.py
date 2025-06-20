"""
AI模型提供者接口定义
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, AsyncGenerator, Any
from dataclasses import dataclass


@dataclass
class ModelConfig:
    """模型配置"""
    model_name: str
    provider: str
    temperature: float = 0.7
    max_tokens: int = 2000
    timeout: int = 30
    
    
@dataclass 
class ModelResponse:
    """模型响应"""
    content: str
    usage_tokens: int
    model: str
    finish_reason: str
    metadata: Dict[str, Any]


class IModelProvider(ABC):
    """
    AI模型提供者抽象接口
    支持多种AI模型集成和统一调用
    """
    
    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """
        初始化提供者
        
        Args:
            config: 提供者特定的配置
            
        Returns:
            bool: 初始化是否成功
        """
        pass
    
    @abstractmethod
    async def generate_response(
        self, 
        messages: List[Dict[str, str]],
        config: ModelConfig
    ) -> ModelResponse:
        """
        生成AI响应
        
        Args:
            messages: 消息历史列表
            config: 模型配置
            
        Returns:
            ModelResponse: 模型响应结果
        """
        pass
    
    @abstractmethod
    async def generate_stream_response(
        self,
        messages: List[Dict[str, str]], 
        config: ModelConfig
    ) -> AsyncGenerator[str, None]:
        """
        生成流式响应
        
        Args:
            messages: 消息历史列表
            config: 模型配置
            
        Yields:
            str: 流式响应内容
        """
        pass
        
    @abstractmethod
    async def validate_config(self, config: ModelConfig) -> bool:
        """
        验证模型配置有效性
        
        Args:
            config: 模型配置
            
        Returns:
            bool: 配置是否有效
        """
        pass
    
    @abstractmethod
    def get_supported_models(self) -> List[str]:
        """
        获取支持的模型列表
        
        Returns:
            List[str]: 支持的模型名称列表
        """
        pass
        
    @abstractmethod
    def get_provider_name(self) -> str:
        """
        获取提供者名称
        
        Returns:
            str: 提供者名称
        """
        pass 