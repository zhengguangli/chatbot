"""
Context7增强的模型提供者
集成Context7文档检索功能，为AI响应提供更准确的上下文
"""

import os
import logging
from typing import Dict, List, Optional, Any
import asyncio

from contracts.model_provider import (
    IModelProvider, ModelConfig, ModelResponse
)
from .model_providers import OpenAIProvider
from core.errors import APIError, ErrorCode


class Context7EnhancedProvider(OpenAIProvider):
    """
    增强版OpenAI提供者，集成Context7文档检索
    """
    
    def __init__(self, api_key: Optional[str] = None, logger: Optional[logging.Logger] = None):
        super().__init__(api_key, logger)
        self.context7_api_key = os.getenv("CONTEXT7_API_KEY")
        self.context7_enabled = os.getenv("CONTEXT7_ENABLED", "false").lower() == "true"
        self.context7_max_tokens = int(os.getenv("CONTEXT7_MAX_TOKENS", "5000"))
        self.context7_libraries = os.getenv("CONTEXT7_LIBRARIES", "").split(",")
        
        if self.context7_enabled:
            self.logger.info("Context7增强功能已启用")
            if self.context7_libraries:
                self.logger.info(f"监控的库: {', '.join(self.context7_libraries)}")
    
    async def _get_context7_docs(self, query: str) -> Optional[str]:
        """
        从Context7获取相关文档
        
        Args:
            query: 用户查询
            
        Returns:
            相关文档内容或None
        """
        if not self.context7_enabled:
            return None
            
        try:
            # 检测查询中提到的库
            mentioned_libs = []
            for lib in self.context7_libraries:
                if lib.lower() in query.lower():
                    mentioned_libs.append(lib)
            
            if not mentioned_libs:
                return None
            
            # 这里应该调用实际的Context7 API
            # 目前返回模拟数据作为示例
            self.logger.info(f"正在从Context7获取文档: {mentioned_libs}")
            
            # 模拟Context7响应
            context_docs = f"""
## Context7文档检索结果

查询到以下相关文档：

### {mentioned_libs[0]}相关文档
- 最新版本信息
- API参考文档
- 最佳实践指南

注意：这是模拟的Context7响应。实际使用时需要集成真实的Context7 API。
"""
            
            return context_docs
            
        except Exception as e:
            self.logger.error(f"Context7文档检索失败: {e}")
            return None
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        config: ModelConfig
    ) -> ModelResponse:
        """
        生成增强的AI响应，包含Context7文档上下文
        """
        try:
            # 获取用户最新的查询
            user_query = ""
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    user_query = msg.get("content", "")
                    break
            
            # 尝试获取Context7文档
            context_docs = await self._get_context7_docs(user_query)
            
            # 如果获取到文档，将其添加到消息上下文中
            enhanced_messages = messages.copy()
            if context_docs:
                # 创建系统消息，包含Context7文档
                context_message = {
                    "role": "system",
                    "content": f"以下是相关的技术文档，请在回答时参考：\n\n{context_docs}"
                }
                
                # 将文档插入到消息列表的开头（在系统提示之后）
                if enhanced_messages and enhanced_messages[0].get("role") == "system":
                    enhanced_messages.insert(1, context_message)
                else:
                    enhanced_messages.insert(0, context_message)
                
                self.logger.info("已添加Context7文档到上下文")
            
            # 调用父类方法生成响应
            response = await super().generate_response(enhanced_messages, config)
            
            # 在元数据中标记是否使用了Context7
            if context_docs:
                response.metadata["context7_used"] = True
                response.metadata["context7_docs_length"] = len(context_docs)
            
            return response
            
        except Exception as e:
            self.logger.error(f"生成增强响应失败: {e}")
            # 如果增强失败，回退到普通响应
            return await super().generate_response(messages, config)
    
    def get_provider_name(self) -> str:
        """获取提供者名称"""
        return "context7-enhanced-openai"
    
    async def test_context7_connection(self) -> bool:
        """
        测试Context7连接
        """
        if not self.context7_enabled:
            return False
            
        try:
            # 这里应该实现实际的Context7连接测试
            # 目前返回模拟结果
            self.logger.info("测试Context7连接...")
            await asyncio.sleep(0.1)  # 模拟网络延迟
            return True
            
        except Exception as e:
            self.logger.error(f"Context7连接测试失败: {e}")
            return False 