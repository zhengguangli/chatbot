"""
模型提供者实现
包含OpenAI适配器和模型提供者注册表
"""

import os
from typing import Dict, List, Optional, Any, AsyncGenerator
import logging
import asyncio
import aiohttp
import json

from contracts.model_provider import (
    IModelProvider, ModelConfig, ModelResponse
)
from core.errors import APIError, ErrorCode


class OpenAIProvider(IModelProvider):
    """OpenAI模型提供者实现"""
    
    def __init__(self, api_key: Optional[str] = None, logger: Optional[logging.Logger] = None):
        # 优先使用传入的api_key，然后是环境变量
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.logger = logger or logging.getLogger(__name__)
        # 支持自定义API端点
        self.base_url = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        
        # 额外的配置项
        self.organization = os.getenv("OPENAI_ORG_ID")
        self.project = os.getenv("OPENAI_PROJECT_ID")
        self.timeout = self._parse_timeout(os.getenv("OPENAI_TIMEOUT", "30"))
        
        # 模型配置
        self.default_model = os.getenv("DEFAULT_MODEL", "qwen3")
        self.default_max_tokens = int(os.getenv("MAX_TOKENS", "2000"))
        self.default_temperature = float(os.getenv("TEMPERATURE", "0.7"))
        
        # Context7配置
        self.context7_enabled = os.getenv("CONTEXT7_ENABLED", "false").lower() == "true"
        
        # 记录配置状态
        if self.api_key:
            self.logger.info(f"OpenAI Provider配置成功，使用模型: {self.default_model}")
            if self.context7_enabled:
                self.logger.info("Context7集成已启用")
        else:
            self.logger.warning("OpenAI API密钥未设置")
            
    def _parse_timeout(self, timeout_str: Optional[str]) -> float:
        """解析超时配置"""
        if not timeout_str:
            return 30.0
        try:
            return float(timeout_str)
        except ValueError:
            return 30.0
    
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
            
            if not self.api_key:
                raise APIError("OpenAI API密钥未设置", ErrorCode.API_KEY_MISSING)
                
            # 构建API请求头
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # 添加组织ID（如果有）
            if self.organization:
                headers["OpenAI-Organization"] = self.organization
                
            # 添加项目ID（如果有）
            if self.project:
                headers["OpenAI-Project"] = self.project
            
            endpoint = f"{self.base_url}/chat/completions"
            
            # 使用环境变量中的默认值，如果config中没有指定
            model_name = config.model_name or self.default_model
            max_tokens = config.max_tokens if config.max_tokens > 0 else self.default_max_tokens
            temperature = config.temperature if config.temperature >= 0 else self.default_temperature
            
            payload = {
                "model": model_name,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            # 记录请求信息（不包含API密钥）
            self.logger.debug(f"发送请求到OpenAI: {model_name}, 消息数: {len(messages)}")
            
            # 发送API请求，使用配置的超时时间
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(endpoint, headers=headers, json=payload) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        self.logger.error(f"OpenAI API错误 {resp.status}: {error_text}")
                        raise APIError(
                            f"OpenAI API调用失败: HTTP {resp.status}, {error_text}", 
                            ErrorCode.API_REQUEST_FAILED
                        )
                    
                    # 解析响应
                    result = await resp.json()
                    
            # 从响应中提取内容
            response_content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            finish_reason = result.get("choices", [{}])[0].get("finish_reason", "unknown")
            
            # 获取token使用情况
            usage = result.get("usage", {})
            total_tokens = usage.get("total_tokens", 0)
            
            # 创建响应对象
            response = ModelResponse(
                content=response_content,
                usage_tokens=total_tokens,
                model=model_name,
                finish_reason=finish_reason,
                metadata={
                    "provider": "openai",
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "context7_enabled": self.context7_enabled
                }
            )
            
            self.logger.debug(f"生成响应成功，tokens: {total_tokens}")
            return response
            
        except aiohttp.ClientError as e:
            self.logger.error(f"网络请求失败: {e}")
            return ModelResponse(
                content=f"抱歉，网络连接出现问题: {str(e)}",
                usage_tokens=0,
                model=config.model_name or self.default_model,
                finish_reason="error",
                metadata={"error": str(e), "error_type": "network"}
            )
        except Exception as e:
            self.logger.error(f"生成响应失败: {e}")
            # 返回友好的错误响应，而不是直接抛出异常
            return ModelResponse(
                content=f"抱歉，AI服务遇到了问题: {str(e)}",
                usage_tokens=0,
                model=config.model_name or self.default_model,
                finish_reason="error",
                metadata={"error": str(e)}
            )
    
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
            supported_models = ["qwen3", "gpt-4", "gpt-4-turbo"]
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
            "qwen3",
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
            "qwen3": {
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
