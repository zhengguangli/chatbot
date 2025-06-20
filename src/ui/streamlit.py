"""
Streamlit Web界面模块 - 新架构版本
使用新的服务架构，但保持原有的用户体验
"""

import streamlit as st
import logging
import sys
from .compatibility import (
    initialize_openai_client,
    get_chatbot_response,
    manage_conversation_history,
    APP_TITLE,
    APP_DESCRIPTION,
    MAX_CONVERSATION_HISTORY
)

# 配置日志以便在Streamlit中查看OpenAI日志
def configure_streamlit_logging():
    """配置Streamlit的日志系统，确保OpenAI日志可见"""
    # 设置根日志级别
    logging.getLogger().setLevel(logging.DEBUG)
    
    # 特别配置OpenAI相关的日志
    openai_logger = logging.getLogger('services.model_providers')
    openai_logger.setLevel(logging.DEBUG)
    
    # 确保日志能在Streamlit中显示
    if not openai_logger.handlers:
        # 创建控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        
        # 设置格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        
        # 添加到logger
        openai_logger.addHandler(console_handler)
        openai_logger.propagate = False  # 避免重复输出

# 在模块加载时配置日志
configure_streamlit_logging()


def run_streamlit_interface():
    """运行Streamlit Web界面 - 新架构版本"""
    # 确保在Streamlit环境中正确处理异步
    import threading
    import asyncio
    
    # 只在首次初始化时配置事件循环，避免重复
    if "streamlit_initialized" not in st.session_state:
        st.session_state.streamlit_initialized = True
        
        # 显示日志状态
        with st.expander("🔍 OpenAI日志状态", expanded=False):
            st.write("✅ OpenAI请求日志已启用")
            st.write("📊 日志级别: DEBUG")
            st.write("💡 发送消息后可在终端中查看详细API日志")
        
        # 为Streamlit线程配置事件循环（静默配置）
        try:
            # 强制创建新的事件循环，避免线程冲突
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            # 确保事件循环策略正确设置
            asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
        except Exception as e:
            st.error(f"设置事件循环时出错: {str(e)}")
    
    # 页面配置
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 标题和描述
    st.title(APP_TITLE)
    st.write(APP_DESCRIPTION)
    
    # 侧边栏 - 新功能
    with st.sidebar:
        st.header("⚙️ 设置")
        
        # OpenAI日志状态显示
        st.subheader("📊 OpenAI日志")
        st.info("✅ 请求日志已启用\n🔍 查看终端输出以获取详细日志")
        
        # 显示系统状态
        if st.button("🔄 刷新状态"):
            st.rerun()
        
        # 新会话按钮
        if st.button("➕ 新建会话"):
            # 清空当前会话历史
            st.session_state.conversation_history = []
            st.success("已创建新会话！")
        
        # 清空历史按钮
        if st.button("🗑️ 清空历史"):
            st.session_state.conversation_history = []
            st.success("历史记录已清空！")
        
        # 显示统计信息
        if "conversation_history" in st.session_state:
            msg_count = len(st.session_state.conversation_history)
            st.metric("消息数量", msg_count)
    
    # 初始化OpenAI客户端（使用兼容性包装器）
    if "client" not in st.session_state:
        try:
            with st.spinner("正在初始化AI服务..."):
                # 强制为Streamlit线程创建专用事件循环
                import asyncio
                import threading
                
                # 尝试使用异步方式，如果失败则使用同步wrapper
                try:
                    # 尝试直接在当前线程中处理
                    import asyncio
                    try:
                        # 检查是否有活跃的事件循环
                        asyncio.get_running_loop()
                        # 如果有，使用run_in_executor避免阻塞
                        def sync_init():
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            try:
                                return loop.run_until_complete(initialize_openai_client())
                            finally:
                                loop.close()
                        
                        # 使用Streamlit的内置方式处理异步
                        import concurrent.futures
                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            future = executor.submit(sync_init)
                            client = future.result(timeout=30)
                    except RuntimeError:
                        # 没有运行的事件循环，直接创建新的
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            client = loop.run_until_complete(initialize_openai_client())
                        finally:
                            # 保持事件循环以供后续使用
                            pass
                except Exception as fallback_e:
                    st.error(f"初始化客户端失败: {fallback_e}")
                    client = None
                
                if not client:
                    st.error("❌ AI服务初始化失败，请检查配置")
                    st.info("请确保设置了OPENAI_API_KEY环境变量")
                    st.stop()
                st.session_state.client = client
                # 静默初始化成功，不显示成功消息避免每次刷新都显示
        except Exception as e:
            st.error(f"初始化失败: {str(e)}")
            st.stop()
    
    # 初始化会话状态
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    
    # 主聊天区域
    st.subheader("💬 对话")
    
    # 创建聊天容器
    chat_container = st.container()
    
    # 显示对话历史
    with chat_container:
        if not st.session_state.conversation_history:
            st.info("👋 您好！我是智能AI助手，有什么可以帮助您的吗？")
        
        for i, msg in enumerate(st.session_state.conversation_history):
            if msg["role"] == "user":
                with st.chat_message("user", avatar="👤"):
                    st.write(msg["content"])
            else:
                with st.chat_message("assistant", avatar="🤖"):
                    st.write(msg["content"])
    
    # 用户输入区域
    user_input = st.chat_input("请输入您的问题...")
    
    if user_input and user_input.strip():
        # 显示用户消息
        with st.chat_message("user", avatar="👤"):
            st.write(user_input)
        
        # 获取机器人响应
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("🤔 AI正在思考..."):
                try:
                    # 在独立线程中运行异步函数，避免事件循环冲突
                    import asyncio
                    import concurrent.futures
                    
                    # 使用更简单的异步处理方式
                    try:
                        # 检查当前事件循环状态
                        try:
                            current_loop = asyncio.get_running_loop()
                            # 如果在事件循环中，使用run_in_executor
                            def sync_get_response():
                                new_loop = asyncio.new_event_loop()
                                asyncio.set_event_loop(new_loop)
                                try:
                                    return new_loop.run_until_complete(get_chatbot_response(
                                        st.session_state.client,
                                        user_input,
                                        st.session_state.conversation_history
                                    ))
                                finally:
                                    new_loop.close()
                            
                            # 在线程中运行，但更简化
                            import concurrent.futures
                            with concurrent.futures.ThreadPoolExecutor() as executor:
                                future = executor.submit(sync_get_response)
                                response = future.result(timeout=60)
                        except RuntimeError:
                            # 没有运行的事件循环，直接处理
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            try:
                                response = loop.run_until_complete(get_chatbot_response(
                                    st.session_state.client,
                                    user_input,
                                    st.session_state.conversation_history
                                ))
                            finally:
                                pass  # 保持循环用于后续请求
                    except Exception as async_error:
                        st.error(f"获取响应失败: {async_error}")
                        response = "抱歉，处理请求时出现了问题。"
                    
                    if response.startswith("抱歉，发生了错误："):
                        st.error(response)
                    else:
                        st.write(response)
                        
                        # 更新对话历史
                        st.session_state.conversation_history = manage_conversation_history(
                            st.session_state.conversation_history,
                            user_input,
                            response,
                            MAX_CONVERSATION_HISTORY
                        )
                
                except Exception as e:
                    error_msg = f"获取响应时发生错误: {str(e)}"
                    st.error(error_msg)
    
    # 页面底部信息
    with st.expander("ℹ️ 系统信息", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**架构版本**: 重构架构 v2.0")
            st.write("**服务状态**: 使用新服务容器")
            
        with col2:
            st.write("**消息历史**: 自动管理")
            st.write("**数据持久化**: 文件存储")
    
    # 调试信息（可选）
    if st.checkbox("🔧 显示调试信息"):
        st.subheader("调试信息")
        st.write("会话状态:")
        st.json({
            "message_count": len(st.session_state.conversation_history),
            "client_initialized": "client" in st.session_state,
            "last_message": st.session_state.conversation_history[-1] if st.session_state.conversation_history else None
        })


def run_enhanced_streamlit_interface():
    """
    运行增强版Streamlit界面
    提供更多功能，如会话管理、文件上传等
    """
    st.set_page_config(
        page_title="🤖 智能助手 Pro",
        page_icon="🚀",
        layout="wide"
    )
    
    st.title("🚀 智能聊天助手 Pro")
    st.caption("基于重构架构的增强版聊天系统")
    
    # 主要功能标签页
    tab1, tab2, tab3 = st.tabs(["💬 聊天", "📊 会话管理", "⚙️ 设置"])
    
    with tab1:
        # 基础聊天功能
        run_streamlit_interface()
    
    with tab2:
        st.header("📊 会话管理")
        st.info("会话管理功能正在开发中...")
        
        # 这里可以添加会话列表、切换等功能
        if st.button("获取会话列表"):
            st.write("功能开发中，敬请期待")
    
    with tab3:
        st.header("⚙️ 高级设置")
        
        # 模型设置
        st.subheader("🤖 模型配置")
        model_choice = st.selectbox(
            "选择AI模型",
            ["qwen3", "gpt-4", "gpt-4-turbo"],
            index=0
        )
        
        temperature = st.slider(
            "创造性程度 (Temperature)",
            min_value=0.0,
            max_value=2.0,
            value=0.7,
            step=0.1
        )
        
        max_tokens = st.number_input(
            "最大回复长度",
            min_value=100,
            max_value=4000,
            value=2000,
            step=100
        )
        
        if st.button("保存设置"):
            st.success("设置已保存（功能开发中）")


# 主界面选择器
def main():
    """主界面选择器"""
    interface_type = st.sidebar.selectbox(
        "选择界面类型",
        ["标准版", "增强版"],
        index=0
    )
    
    if interface_type == "标准版":
        run_streamlit_interface()
    else:
        run_enhanced_streamlit_interface()


if __name__ == "__main__":
    main() 