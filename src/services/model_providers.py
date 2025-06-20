"""
模型提供者实现
包含OpenAI适配器和模型提供者注册表
"""

import os
from typing import Dict, List, Optional, Any, AsyncGenerator
import logging
import asyncio

from ..interfaces.model_provider import (
    IModelProvider, ModelConfig, ModelResponse
)
from ..core.errors import APIError, ErrorCode


class OpenAIProvider(IModelProvider):
    """OpenAI模型提供者实现"""
    
    def __init__(self, api_key: Optional[str] = None, logger: Optional[logging.Logger] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.logger = logger or logging.getLogger(__name__)
        self.base_url = "https://api.openai.com/v1"
    
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """初始化提供者"""
        try:
            if not self.api_key:
                self.logger.error("OpenAI API密钥未设置")
                return False
            
            self.logger.info("OpenAI Provider初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"OpenAI Provider初始化失败: {e}")
            return False
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        config: ModelConfig
    ) -> ModelResponse:
        """生成AI响应"""
        try:
            # 验证输入
            if not messages:
                raise APIError("消息列表不能为空", ErrorCode.API_REQUEST_INVALID)
            
            # 构建响应内容（模拟）
            last_message = messages[-1].get("content", "")
            
            if "你好" in last_message:
                response_content = "你好！我是AI助手，很高兴为您服务。有什么我可以帮助您的吗？"
            elif "天气" in last_message:
                response_content = "抱歉，我无法获取实时天气信息。建议您查看当地天气预报应用。"
            else:
                response_content = f"我理解您说的是：{last_message}。请告诉我更多详情，我会尽力帮助您。"
            
            # 计算token数
            total_tokens = sum(len(msg.get("content", "").split()) for msg in messages)
            total_tokens += len(response_content.split())
            
            # 创建响应对象
            response = ModelResponse(
                content=response_content,
                usage_tokens=total_tokens,
                model=config.model_name,
                finish_reason="stop",
                metadata={
                    "provider": "openai",
                    "temperature": config.temperature,
                    "max_tokens": config.max_tokens
                }
            )
            
            self.logger.debug(f"生成响应成功，tokens: {total_tokens}")
            return response
            
        except Exception as e:
            self.logger.error(f"生成响应失败: {e}")
            raise APIError(f"OpenAI API调用失败: {str(e)}", ErrorCode.API_REQUEST_FAILED)
    
    async def generate_stream_response(
        self,
        messages: List[Dict[str, str]],
        config: ModelConfig
    ) -> AsyncGenerator[str, None]:
        """生成流式响应"""
        try:
            # 模拟流式响应
            response_text = "这是一个模拟的流式响应，展示如何分块返回内容。"
            words = response_text.split()
            
            for word in words:
                yield word + " "
                await asyncio.sleep(0.1)  # 模拟网络延迟
            
        except Exception as e:
            self.logger.error(f"流式响应失败: {e}")
            raise APIError(f"OpenAI流式API调用失败: {str(e)}", ErrorCode.API_REQUEST_FAILED)
    
    async def validate_config(self, config: ModelConfig) -> bool:
        """验证模型配置"""
        try:
            # 检查模型名称
            supported_models = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
            if config.model_name not in supported_models:
                return False
            
            # 检查参数范围
            if not (0 <= config.temperature <= 2):
                return False
            
            if config.max_tokens <= 0:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"配置验证失败: {e}")
            return False
    
    def get_supported_models(self) -> List[str]:
        """获取支持的模型列表"""
        return [
            "gpt-3.5-turbo",
            "gpt-4",
            "gpt-4-turbo",
            "gpt-4o"
        ]
    
    def get_provider_name(self) -> str:
        """获取提供者名称"""
        return "openai"
    
    def get_model_limits(self, model: str) -> Dict[str, Any]:
        """获取模型限制信息"""
        limits = {
            "gpt-3.5-turbo": {
                "max_tokens": 4096,
                "context_window": 16384,
                "cost_per_1k_tokens": 0.002
            },
            "gpt-4": {
                "max_tokens": 8192,
                "context_window": 8192,
                "cost_per_1k_tokens": 0.03
            },
            "gpt-4-turbo": {
                "max_tokens": 4096,
                "context_window": 128000,
                "cost_per_1k_tokens": 0.01
            }
        }
        
        return limits.get(model, {})
    
    async def test_connection(self) -> bool:
        """测试API连接"""
        try:
            # 这里应该调用OpenAI API的健康检查端点
            # 目前返回True表示连接正常
            return True
            
        except Exception as e:
            self.logger.error(f"连接测试失败: {e}")
            return False


class ModelProviderRegistry:
    """模型提供者注册表"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self._providers: Dict[str, IModelProvider] = {}
        self._default_provider: Optional[str] = None
    
    def register_provider(self, name: str, provider: IModelProvider) -> bool:
        """注册模型提供者"""
        try:
            if name in self._providers:
                self.logger.warning(f"提供者 {name} 已存在，将被覆盖")
            
            self._providers[name] = provider
            
            # 设置第一个注册的提供者为默认提供者
            if not self._default_provider:
                self._default_provider = name
            
            self.logger.info(f"提供者 {name} 注册成功")
            return True
            
        except Exception as e:
            self.logger.error(f"注册提供者失败 {name}: {e}")
            return False
    
    def get_provider(self, name: Optional[str] = None) -> Optional[IModelProvider]:
        """获取模型提供者"""
        try:
            provider_name = name or self._default_provider
            
            if not provider_name:
                return None
            
            return self._providers.get(provider_name)
            
        except Exception as e:
            self.logger.error(f"获取提供者失败 {name}: {e}")
            return None
    
    def list_providers(self) -> List[str]:
        """列出所有注册的提供者"""
        return list(self._providers.keys())
    
    def set_default_provider(self, name: str) -> bool:
        """设置默认提供者"""
        if name in self._providers:
            self._default_provider = name
            self.logger.info(f"默认提供者设置为: {name}")
            return True
        
        self.logger.error(f"提供者 {name} 不存在")
        return False
    
    def get_default_provider(self) -> Optional[str]:
        """获取默认提供者名称"""
        return self._default_provider
    
    async def initialize_all_providers(self, configs: Dict[str, Dict[str, Any]]) -> Dict[str, bool]:
        """初始化所有提供者"""
        results = {}
        
        for provider_name, provider in self._providers.items():
            config = configs.get(provider_name, {})
            
            try:
                if hasattr(provider, 'initialize'):
                    success = await provider.initialize(config)
                else:
                    success = True  # 如果没有initialize方法，认为成功
                
                results[provider_name] = success
                
                if success:
                    self.logger.info(f"提供者 {provider_name} 初始化成功")
                else:
                    self.logger.error(f"提供者 {provider_name} 初始化失败")
                    
            except Exception as e:
                self.logger.error(f"提供者 {provider_name} 初始化异常: {e}")
                results[provider_name] = False
        
        return results
    
    def unregister_provider(self, name: str) -> bool:
        """注销提供者"""
        if name in self._providers:
            del self._providers[name]
            
            # 如果删除的是默认提供者，重新设置默认提供者
            if self._default_provider == name:
                self._default_provider = next(iter(self._providers.keys())) if self._providers else None
            
            self.logger.info(f"提供者 {name} 已注销")
            return True
        
        return False
