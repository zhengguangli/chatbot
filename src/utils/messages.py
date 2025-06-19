"""
消息处理和格式化工具模块
"""

import streamlit as st


def display_error(message, use_streamlit=True):
    """显示错误消息"""
    if use_streamlit:
        try:
            st.error(message)
        except:
            print(f"错误：{message}")
    else:
        print(f"错误：{message}")


def display_warning(message, use_streamlit=True):
    """显示警告消息"""
    if use_streamlit:
        try:
            st.warning(message)
        except:
            print(f"警告：{message}")
    else:
        print(f"警告：{message}")


def display_info(message, use_streamlit=True):
    """显示信息消息"""
    if use_streamlit:
        try:
            st.info(message)
        except:
            print(f"信息：{message}")
    else:
        print(f"信息：{message}")


def format_error_list(issues, title="问题列表"):
    """格式化错误列表"""
    if not issues:
        return ""

    formatted = f"{title}：\n"
    for issue in issues:
        formatted += f"• {issue}\n"
    return formatted.strip()


def format_conversation_message(role, content):
    """格式化对话消息"""
    return {"role": role, "content": content}


def validate_message_format(message):
    """验证消息格式"""
    return (
        isinstance(message, dict)
        and "role" in message
        and "content" in message
        and message["role"] in ["user", "assistant", "system"]
    )
