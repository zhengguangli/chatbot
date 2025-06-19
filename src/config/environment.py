"""
环境检查和配置管理模块
"""

import os
import sys

# 加载.env文件
try:
    from dotenv import load_dotenv

    load_dotenv()  # 自动加载项目根目录的.env文件
except ImportError:
    pass  # 如果没有安装python-dotenv，继续使用系统环境变量


def check_environment():
    """检查运行环境和配置"""
    issues = []
    warnings = []

    # 检查Python版本
    if sys.version_info < (3, 9):
        issues.append("Python版本需要3.9或更高")

    # 检查必需的API密钥
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        issues.append("未设置OPENAI_API_KEY环境变量")
    elif len(api_key.strip()) < 10:
        issues.append("OPENAI_API_KEY格式不正确")

    # 检查可选的OpenAI配置项
    base_uri = os.getenv("OPENAI_BASE_URI")
    if base_uri:
        if not base_uri.startswith(("http://", "https://")):
            warnings.append("OPENAI_BASE_URI应该以http://或https://开头")

    org_id = os.getenv("OPENAI_ORG_ID")
    if org_id and len(org_id.strip()) < 5:
        warnings.append("OPENAI_ORG_ID格式可能不正确（太短）")

    project_id = os.getenv("OPENAI_PROJECT_ID")
    if project_id and len(project_id.strip()) < 5:
        warnings.append("OPENAI_PROJECT_ID格式可能不正确（太短）")

    timeout = os.getenv("OPENAI_TIMEOUT")
    if timeout:
        try:
            timeout_val = float(timeout)
            if timeout_val <= 0:
                warnings.append("OPENAI_TIMEOUT应该是正数")
            elif timeout_val > 300:
                warnings.append(
                    "OPENAI_TIMEOUT设置过大（超过5分钟），可能导致长时间等待"
                )
        except ValueError:
            warnings.append("OPENAI_TIMEOUT应该是数字")

    return issues, warnings


def get_openai_config():
    """获取OpenAI配置参数"""
    return {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "base_url": os.getenv("OPENAI_BASE_URI"),
        "organization": os.getenv("OPENAI_ORG_ID"),
        "project": os.getenv("OPENAI_PROJECT_ID"),
        "timeout": _parse_timeout(os.getenv("OPENAI_TIMEOUT")),
    }


def _parse_timeout(timeout_str):
    """解析超时配置"""
    if not timeout_str:
        return None
    try:
        return float(timeout_str)
    except ValueError:
        return None
