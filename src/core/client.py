"""
OpenAI客户端管理模块
"""

from openai import OpenAI
from ..config.environment import check_environment, get_openai_config
from ..utils.messages import display_error, display_warning


def initialize_openai_client():
    """初始化OpenAI客户端"""
    # 检查环境
    env_issues, env_warnings = check_environment()
    if env_issues:
        error_msg = "环境配置问题：\n" + "\n".join(f"• {issue}" for issue in env_issues)
        display_error(error_msg)
        return None

    # 显示警告但继续执行
    if env_warnings:
        warning_msg = "配置警告：\n" + "\n".join(
            f"• {warning}" for warning in env_warnings
        )
        display_warning(warning_msg)

    try:
        # 获取配置
        config = get_openai_config()

        # 创建客户端参数
        client_kwargs = {"api_key": config["api_key"]}

        if config["base_url"]:
            client_kwargs["base_url"] = config["base_url"].strip()
        if config["organization"]:
            client_kwargs["organization"] = config["organization"].strip()
        if config["project"]:
            client_kwargs["project"] = config["project"].strip()
        if config["timeout"]:
            client_kwargs["timeout"] = config["timeout"]

        # 创建客户端
        client = OpenAI(**client_kwargs)

        # 测试连接
        client.models.list()
        return client

    except Exception as e:
        error_msg = f"OpenAI客户端初始化失败：{str(e)}"
        display_error(error_msg)
        return None
