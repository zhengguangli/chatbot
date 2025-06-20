"""
兼容性包装器
为现有UI提供旧接口的兼容性，内部使用新的服务架构
"""

import os
from typing import List, Dict, Any, Optional
import asyncio
from .adapters import get_global_adapter, run_async_safely
import sys


def initialize_openai_client():
    """
    初始化OpenAI客户端（兼容性函数）
    为了保持向后兼容性，这个函数仍然存在，但内部使用新架构
    
    Returns:
        object: 模拟的客户端对象，实际返回适配器
    """
    try:
        # 获取OpenAI API密钥
        api_key = os.getenv("OPENAI_API_KEY")
        
        # 获取全局适配器
        adapter = get_global_adapter(api_key)
        
        # 检查当前线程
        import threading
        current_thread_name = threading.current_thread().name
        
        # 针对Streamlit的特殊处理
        if 'ScriptRunner' in current_thread_name:
            print(f"检测到Streamlit脚本运行器线程 '{current_thread_name}'")
            
            # 为Streamlit线程创建新的事件循环
            import asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
            # 在此循环中运行初始化
            success = loop.run_until_complete(adapter.initialize())
        else:
            # 异步初始化适配器
            async def init_async():
                return await adapter.initialize()
            
            success = run_async_safely(init_async())
        
        if success:
            print("✅ AI服务初始化成功")
            return adapter  # 返回适配器作为"客户端"
        else:
            print("❌ AI服务初始化失败")
            return None
            
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return None


def get_chatbot_response(client, user_input: str, conversation_history: List[Dict[str, str]]) -> str:
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
        
        # 检测是否在Streamlit环境中
        in_streamlit = 'streamlit' in sys.modules
        
        # 使用适配器获取响应
        if in_streamlit:
            # Streamlit环境中，使用专门的处理方式
            import asyncio
            import concurrent.futures
            
            # 创建异步运行的函数
            async def async_get_response():
                return await client.get_chatbot_response(user_input, conversation_history)
            
            # 使用线程池执行器来运行异步代码
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(lambda: asyncio.run(async_get_response()))
                try:
                    response = future.result(timeout=60)  # 设置超时，避免永久阻塞
                    return str(response) if response else "响应获取失败"
                except concurrent.futures.TimeoutError:
                    return "请求超时，请稍后再试"
                except Exception as e:
                    return f"获取响应失败: {str(e)}"
        else:
            # 非Streamlit环境，使用默认方法
            async def get_response_async():
                return await client.get_chatbot_response(user_input, conversation_history)
            
            response = run_async_safely(get_response_async())
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
    try:
        # 获取全局适配器
        adapter = get_global_adapter()
        
        # 使用适配器管理历史
        return adapter.manage_conversation_history(
            conversation_history, user_input, response, max_history
        )
        
    except Exception as e:
        print(f"管理对话历史失败: {e}")
        # 回退到简单实现
        new_history = conversation_history.copy()
        new_history.append({"role": "user", "content": user_input})
        new_history.append({"role": "assistant", "content": response})
        
        if len(new_history) > max_history:
            new_history = new_history[-max_history:]
        
        return new_history


def check_environment():
    """
    检查环境配置（兼容性函数）
    
    Returns:
        Tuple[List[str], List[str]]: (错误列表, 警告列表)
    """
    try:
        # 获取全局适配器
        adapter = get_global_adapter()
        
        # 使用适配器检查环境
        async def check_env_async():
            return await adapter.check_environment()
        
        issues, warnings = run_async_safely(check_env_async())
        return issues, warnings
        
    except Exception as e:
        return [f"环境检查失败: {e}"], []


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
• 运行 'uv run streamlit run main.py' 启动Web界面
"""


# 导出兼容性接口
APP_TITLE = MockSettings.APP_TITLE
APP_DESCRIPTION = MockSettings.APP_DESCRIPTION  
MAX_CONVERSATION_HISTORY = MockSettings.MAX_CONVERSATION_HISTORY
CLI_HELP_MESSAGE = MockSettings.CLI_HELP_MESSAGE 