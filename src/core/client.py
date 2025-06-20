"""
OpenAI客户端管理模块
"""

from openai import OpenAI
from config import global_config_manager
from utils.messages import display_error, display_warning


def initialize_openai_client():
    """
    初始化OpenAI客户端
    使用新的ConfigManager
    """
    try:
        # 从全局配置管理器获取值
        api_key = global_config_manager.get_config_value("api_key")
        base_url = global_config_manager.get_config_value("base_url")
        organization = global_config_manager.get_config_value("organization")
        project = global_config_manager.get_config_value("project")
        timeout = global_config_manager.get_config_value("model.timeout")

        if not api_key:
            display_error("OpenAI API密钥未配置。请检查您的.env文件或环境变量。")
            return None

        # 创建客户端参数
        client_kwargs = {"api_key": api_key}

        if base_url:
            client_kwargs["base_url"] = base_url
        if organization:
            client_kwargs["organization"] = organization
        if project:
            client_kwargs["project"] = project
        if timeout:
            client_kwargs["timeout"] = float(timeout)

        # 创建客户端
        client = OpenAI(**client_kwargs)

        # 测试连接
        client.models.list()
        return client

    except Exception as e:
        error_msg = f"OpenAI客户端初始化失败：{str(e)}"
        display_error(error_msg)
        return None
