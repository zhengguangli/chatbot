"""
Streamlit Web界面模块
"""

import streamlit as st
from ..core.client import initialize_openai_client
from ..core.chatbot import get_chatbot_response, manage_conversation_history
from ..config.settings import APP_TITLE, APP_DESCRIPTION, MAX_CONVERSATION_HISTORY


def run_streamlit_interface():
    """运行Streamlit Web界面"""
    st.title(APP_TITLE)
    st.write(APP_DESCRIPTION)

    # 初始化OpenAI客户端
    client = initialize_openai_client()
    if not client:
        st.stop()

    # 初始化会话状态
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []

    # 显示对话历史
    for msg in st.session_state.conversation_history:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        else:
            st.chat_message("assistant").write(msg["content"])

    # 用户输入
    user_input = st.chat_input("请输入您的问题...")

    if user_input:
        # 显示用户消息
        st.chat_message("user").write(user_input)

        # 获取机器人响应
        with st.chat_message("assistant"):
            with st.spinner("AI正在思考..."):
                response = get_chatbot_response(
                    client, user_input, st.session_state.conversation_history
                )
            st.write(response)

        # 更新对话历史
        st.session_state.conversation_history = manage_conversation_history(
            st.session_state.conversation_history,
            user_input,
            response,
            MAX_CONVERSATION_HISTORY,
        )
