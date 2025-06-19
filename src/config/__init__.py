"""
配置管理模块
"""

from .environment import check_environment, get_openai_config
from .settings import *

__all__ = ["check_environment", "get_openai_config"]
