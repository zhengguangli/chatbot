"""
兼容性包装器
为现有UI提供旧接口的兼容性，内部使用新的服务架构
"""

import os
from typing import List, Dict, Any, Optional, Tuple
import asyncio
from .adapters import get_global_adapter


async def initialize_openai_client():
    """
    初始化OpenAI客户端（兼容性函数）
    为了保持向后兼容性，这个函数仍然存在，但内部使用新架构
    
    Returns:
        object: 模拟的客户端对象，实际返回适配器
    """
    try:
        # 确保我们在正确的事件循环中运行
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # 如果没有运行的事件循环，创建一个新的
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        api_key = os.getenv("OPENAI_API_KEY", "")
        adapter = await get_global_adapter(api_key)
        
        if adapter._initialized:
            # 静默返回，不打印控制台消息避免重复输出
            return adapter
        else:
            # 只在确实失败时打印错误（这种情况很少见）
            print("❌ AI服务初始化失败")
            return None
            
    except Exception as e:
        # 更详细的错误处理，避免事件循环相关错误
        error_msg = str(e)
        if "different loop" in error_msg or "event loop" in error_msg.lower():
            print("⚠️ 事件循环冲突，尝试重新初始化...")
            try:
                # 强制创建新的事件循环
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                api_key = os.getenv("OPENAI_API_KEY", "")
                adapter = await get_global_adapter(api_key)
                return adapter
            except Exception as retry_e:
                print(f"❌ 重试初始化失败: {retry_e}")
                return None
        else:
            print(f"❌ 初始化失败: {e}")
            return None


async def get_chatbot_response(client, user_input: str, conversation_history: List[Dict[str, str]]) -> str:
    """
    获取聊天机器人响应（兼容性函数）
    
    Args:
        client: 客户端对象（实际上是适配器）
        user_input: 用户输入
        conversation_history: 对话历史
        
    Returns:
        str: AI响应
    """
    try:
        if not client:
            return "AI服务不可用，请检查配置。"
        
        response = await client.get_chatbot_response(user_input, conversation_history)
        return str(response) if response else "响应获取失败"
        
    except Exception as e:
        return f"获取响应失败: {str(e)}"


def manage_conversation_history(
    conversation_history: List[Dict[str, str]],
    user_input: str,
    response: str,
    max_history: int = 20
) -> List[Dict[str, str]]:
    """
    管理对话历史（兼容性函数）
    
    Args:
        conversation_history: 当前对话历史
        user_input: 用户输入
        response: AI响应
        max_history: 最大历史条数
        
    Returns:
        List[Dict[str, str]]: 更新后的对话历史
    """
    # 这个函数是同步的，所以我们不能在这里get_global_adapter
    # 幸运的是，它没有异步依赖，所以我们可以直接在UIAdapter中实现
    # 但为了简单起见，我们暂时在这里复制逻辑
    new_history = conversation_history.copy()
    new_history.append({"role": "user", "content": user_input})
    new_history.append({"role": "assistant", "content": response})
    
    if len(new_history) > max_history:
        new_history = new_history[-max_history:]
    
    return new_history


async def check_environment() -> Tuple[List[str], List[str]]:
    """
    检查环境配置（兼容性函数）
    
    Returns:
        Tuple[List[str], List[str]]: (错误列表, 警告列表)
    """
    # 这个函数在当前UI中没有被积极使用，但我们为了兼容性而保留它
    issues = []
    warnings = []
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        warnings.append("OpenAI API密钥未设置")
    return issues, warnings


# 为了完全兼容，提供一些配置常量的模拟
class MockSettings:
    """模拟配置设置，保持向后兼容性"""
    
    APP_TITLE = "🤖 智能聊天助手"
    APP_DESCRIPTION = "基于AI的智能对话系统，重构架构版本"
    MAX_CONVERSATION_HISTORY = 20
    CLI_HELP_MESSAGE = """
💡 使用帮助：
• 确保设置了 OPENAI_API_KEY 环境变量
• 或在 .env 文件中配置 API 密钥
• 运行 'uv run streamlit run src/main.py' 启动Web界面
"""


# 导出兼容性接口
APP_TITLE = MockSettings.APP_TITLE
APP_DESCRIPTION = MockSettings.APP_DESCRIPTION  
MAX_CONVERSATION_HISTORY = MockSettings.MAX_CONVERSATION_HISTORY
CLI_HELP_MESSAGE = MockSettings.CLI_HELP_MESSAGE 