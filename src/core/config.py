"""
配置管理系统
分层配置管理，支持多源加载、验证和热重载
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Type
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime

from .errors import ConfigError, ErrorCode, create_config_error


# ============ 配置枚举和类型 ============

class ConfigFormat(Enum):
    """配置文件格式"""
    JSON = "json"
    YAML = "yaml"
    YML = "yml"
    TOML = "toml"
    ENV = "env"


class ConfigSource(Enum):
    """配置来源"""
    FILE = "file"
    ENVIRONMENT = "environment"
    DEFAULT = "default"
    RUNTIME = "runtime"


@dataclass
class ConfigItem:
    """配置项"""
    key: str
    value: Any
    source: ConfigSource
    priority: int
    description: str = ""
    is_sensitive: bool = False
    last_modified: datetime = field(default_factory=datetime.now)


# ============ 默认配置定义 ============

DEFAULT_CONFIG: Dict[str, Any] = {
    "model": {
        "provider": "openai",
        "model_name": "qwen3",
        "temperature": 0.7,
        "max_tokens": 2000,
        "timeout": 30,
        "stream": False
    },
    "database": {
        "backend": "file",
        "connection_string": "./data/chatbot.db",
        "max_connections": 10,
        "auto_backup": True,
        "backup_interval": 3600
    },
    "ui": {
        "theme": "light",
        "language": "zh-CN",
        "max_history_display": 50,
        "auto_save": True,
        "save_interval": 300
    },
    "security": {
        "max_session_duration": 86400,  # 24小时
        "auto_logout": True,
        "log_sensitive_data": False,
        "require_api_key": True
    },
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file_path": "./logs/chatbot.log",
        "max_file_size": 10485760,  # 10MB
        "backup_count": 5
    },
    "features": {
        "enable_conversation_history": True,
        "enable_file_upload": False,
        "enable_voice_input": False,
        "enable_web_search": False,
        "enable_code_execution": False
    }
}


# ============ 敏感配置键 ============

SENSITIVE_KEYS: List[str] = [
    "openai_api_key",
    "anthropic_api_key",
    "google_api_key",
    "database.password",
    "security.encryption_key",
    "security.jwt_secret",
    "api.secret_key"
]


# ============ 简化配置管理器 ============

class ConfigManager:
    """
    简化配置管理器
    支持基本的配置加载和管理功能
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.config: Dict[str, Any] = {}
        self.config_items: Dict[str, ConfigItem] = {}
        self.config_paths: List[Path] = []
        self._initialized = False
    
    async def initialize(
        self,
        config_paths: List[Path],
        config_format: ConfigFormat = ConfigFormat.JSON
    ) -> bool:
        """
        初始化配置管理器
        
        Args:
            config_paths: 配置文件路径列表
            config_format: 配置文件格式
            
        Returns:
            bool: 初始化是否成功
        """
        try:
            self.config_paths = config_paths
            
            # 加载默认配置
            await self._load_default_config()
            
            # 加载环境变量配置
            await self._load_env_config()
            
            # 加载文件配置
            for path in config_paths:
                if path.exists():
                    await self._load_file_config(path, config_format)
                else:
                    self.logger.warning(f"配置文件不存在: {path}")
            
            self._initialized = True
            self.logger.info("配置管理器初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"配置管理器初始化失败: {e}")
            raise create_config_error(f"配置管理器初始化失败: {str(e)}")
    
    async def _load_default_config(self):
        """加载默认配置"""
        for key_path, value in self._flatten_dict(DEFAULT_CONFIG).items():
            self.config_items[key_path] = ConfigItem(
                key=key_path,
                value=value,
                source=ConfigSource.DEFAULT,
                priority=1,
                description=f"默认配置项: {key_path}"
            )
        
        self.config = DEFAULT_CONFIG.copy()
        self.logger.debug("默认配置加载完成")
    
    async def _load_env_config(self):
        """加载环境变量配置"""
        env_mappings = {
            "OPENAI_API_KEY": "openai_api_key",
            "OPENAI_BASE_URL": "openai_base_url",
            "OPENAI_TIMEOUT": "model.timeout",
            "MODEL_TEMPERATURE": "model.temperature",
            "MODEL_MAX_TOKENS": "model.max_tokens",
            "DATABASE_URL": "database.connection_string",
            "LOG_LEVEL": "logging.level",
            "UI_THEME": "ui.theme",
            "UI_LANGUAGE": "ui.language"
        }
        
        for env_key, config_key in env_mappings.items():
            env_value = os.getenv(env_key)
            if env_value:
                # 类型转换
                typed_value = self._convert_env_value(env_value, config_key)
                
                self.config_items[config_key] = ConfigItem(
                    key=config_key,
                    value=typed_value,
                    source=ConfigSource.ENVIRONMENT,
                    priority=3,  # 环境变量优先级高于文件配置
                    description=f"环境变量: {env_key}",
                    is_sensitive=config_key in SENSITIVE_KEYS
                )
                
                # 更新配置字典
                self._set_nested_value(self.config, config_key, typed_value)
        
        self.logger.debug("环境变量配置加载完成")
    
    async def _load_file_config(self, file_path: Path, format: ConfigFormat):
        """
        加载文件配置
        
        Args:
            file_path: 配置文件路径
            format: 配置文件格式
        """
        try:
            content = file_path.read_text(encoding='utf-8')
            
            if format == ConfigFormat.JSON:
                file_config = json.loads(content)
            else:
                # 简化版本，仅支持JSON
                raise create_config_error(f"当前版本暂不支持配置文件格式: {format}")
            
            # 扁平化配置并添加到配置项
            for key_path, value in self._flatten_dict(file_config).items():
                self.config_items[key_path] = ConfigItem(
                    key=key_path,
                    value=value,
                    source=ConfigSource.FILE,
                    priority=2,  # 文件配置优先级中等
                    description=f"文件配置: {file_path.name}",
                    is_sensitive=key_path in SENSITIVE_KEYS
                )
            
            # 合并到主配置
            self._merge_config(self.config, file_config)
            
            self.logger.debug(f"文件配置加载完成: {file_path}")
            
        except Exception as e:
            self.logger.error(f"加载配置文件失败 {file_path}: {e}")
            raise create_config_error(f"加载配置文件失败: {str(e)}")
    
    def get_config_value(
        self,
        key_path: str,
        default_value: Optional[Any] = None
    ) -> Any:
        """
        获取配置值
        
        Args:
            key_path: 配置键路径 (例: "database.host")
            default_value: 默认值
            
        Returns:
            Any: 配置值
        """
        if not self._initialized:
            raise create_config_error("配置管理器未初始化")
        
        try:
            # 先从配置项中查找（支持优先级）
            if key_path in self.config_items:
                return self.config_items[key_path].value
            
            # 从嵌套配置中查找
            keys = key_path.split('.')
            value = self.config
            
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return default_value
            
            return value
            
        except Exception as e:
            self.logger.warning(f"获取配置值失败 {key_path}: {e}")
            return default_value
    
    async def set_config_value(
        self,
        key_path: str,
        value: Any,
        source: ConfigSource = ConfigSource.RUNTIME,
        persist: bool = False
    ) -> bool:
        """
        设置配置值
        
        Args:
            key_path: 配置键路径
            value: 配置值
            source: 配置来源
            persist: 是否持久化到文件
            
        Returns:
            bool: 设置是否成功
        """
        try:
            # 更新配置项
            self.config_items[key_path] = ConfigItem(
                key=key_path,
                value=value,
                source=source,
                priority=4 if source == ConfigSource.RUNTIME else 2,
                description=f"运行时设置: {key_path}",
                is_sensitive=key_path in SENSITIVE_KEYS
            )
            
            # 更新主配置
            self._set_nested_value(self.config, key_path, value)
            
            self.logger.debug(f"配置值设置成功: {key_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"设置配置值失败 {key_path}: {e}")
            return False
    
    def get_sensitive_keys(self) -> List[str]:
        """获取敏感配置键列表"""
        return SENSITIVE_KEYS.copy()
    
    # ============ 工具方法 ============
    
    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
        """扁平化嵌套字典"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
    
    def _set_nested_value(self, d: Dict[str, Any], key_path: str, value: Any):
        """设置嵌套字典值"""
        keys = key_path.split('.')
        current = d
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value
    
    def _merge_config(self, target: Dict[str, Any], source: Dict[str, Any]):
        """合并配置字典"""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._merge_config(target[key], value)
            else:
                target[key] = value
    
    def _convert_env_value(self, env_value: str, key_path: str) -> Any:
        """转换环境变量值类型"""
        # 根据配置键路径推断类型
        if key_path.endswith(('.timeout', '.max_tokens', '.max_connections', '.port')):
            return int(env_value)
        elif key_path.endswith(('.temperature', '.top_p')):
            return float(env_value)
        elif env_value.lower() in ('true', 'false'):
            return env_value.lower() == 'true'
        else:
            return env_value


# ============ 全局配置管理器实例 ============

# 创建全局配置管理器实例
global_config_manager = ConfigManager() 