"""
配置管理接口定义
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union, Type, Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class ConfigFormat(Enum):
    """配置文件格式"""
    JSON = "json"
    YAML = "yaml"
    TOML = "toml"
    ENV = "env"


class ConfigSource(Enum):
    """配置来源"""
    FILE = "file"
    ENVIRONMENT = "environment"
    DEFAULT = "default"
    RUNTIME = "runtime"


@dataclass
class ConfigValidationRule:
    """配置验证规则"""
    field_path: str
    required: bool = False
    data_type: Optional[Type] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    allowed_values: Optional[List[Any]] = None
    pattern: Optional[str] = None


@dataclass
class ConfigSection:
    """配置段"""
    name: str
    description: str
    values: Dict[str, Any]
    source: ConfigSource
    priority: int


class IConfigManager(ABC):
    """
    配置管理抽象接口
    提供多层级配置加载、验证和管理能力
    """
    
    @abstractmethod
    async def initialize(
        self,
        config_paths: List[Path],
        config_format: ConfigFormat = ConfigFormat.YAML
    ) -> bool:
        """
        初始化配置管理器
        
        Args:
            config_paths: 配置文件路径列表
            config_format: 配置文件格式
            
        Returns:
            bool: 初始化是否成功
        """
        pass
    
    @abstractmethod
    async def load_config(
        self,
        reload: bool = False
    ) -> Dict[str, Any]:
        """
        加载配置
        
        Args:
            reload: 是否重新加载
            
        Returns:
            Dict[str, Any]: 完整配置字典
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    async def validate_config(
        self,
        config: Optional[Dict[str, Any]] = None,
        rules: Optional[List[ConfigValidationRule]] = None
    ) -> Dict[str, Any]:
        """
        验证配置
        
        Args:
            config: 要验证的配置，None表示当前配置
            rules: 验证规则，None表示使用默认规则
            
        Returns:
            Dict[str, Any]: 验证结果 {"valid": bool, "errors": List[str]}
        """
        pass
    
    @abstractmethod
    def get_config_section(
        self,
        section_name: str
    ) -> Optional[ConfigSection]:
        """
        获取配置段
        
        Args:
            section_name: 配置段名称
            
        Returns:
            ConfigSection或None: 配置段对象
        """
        pass
    
    @abstractmethod
    async def export_config(
        self,
        export_path: Path,
        format: ConfigFormat = ConfigFormat.YAML,
        include_defaults: bool = True,
        include_sensitive: bool = False
    ) -> bool:
        """
        导出配置
        
        Args:
            export_path: 导出文件路径
            format: 导出格式
            include_defaults: 是否包含默认值
            include_sensitive: 是否包含敏感信息
            
        Returns:
            bool: 导出是否成功
        """
        pass
    
    @abstractmethod
    async def import_config(
        self,
        import_path: Path,
        merge: bool = True,
        validate: bool = True
    ) -> bool:
        """
        导入配置
        
        Args:
            import_path: 导入文件路径
            merge: 是否与现有配置合并
            validate: 是否验证配置
            
        Returns:
            bool: 导入是否成功
        """
        pass
    
    @abstractmethod
    def register_validation_rule(
        self,
        rule: ConfigValidationRule
    ) -> bool:
        """
        注册验证规则
        
        Args:
            rule: 验证规则
            
        Returns:
            bool: 注册是否成功
        """
        pass
    
    @abstractmethod
    def get_config_schema(self) -> Dict[str, Any]:
        """
        获取配置模式
        
        Returns:
            Dict[str, Any]: 配置模式定义
        """
        pass
    
    @abstractmethod
    async def watch_config_changes(
        self,
        callback: Callable[[str, Any], None],
        watch_files: bool = True,
        watch_env: bool = True
    ) -> bool:
        """
        监听配置变化
        
        Args:
            callback: 变化回调函数
            watch_files: 是否监听文件变化
            watch_env: 是否监听环境变量变化
            
        Returns:
            bool: 启动监听是否成功
        """
        pass
    
    @abstractmethod
    def get_sensitive_keys(self) -> List[str]:
        """
        获取敏感配置键列表
        
        Returns:
            List[str]: 敏感键列表
        """
        pass
    
    @abstractmethod
    async def encrypt_sensitive_values(
        self,
        encryption_key: str
    ) -> bool:
        """
        加密敏感配置值
        
        Args:
            encryption_key: 加密密钥
            
        Returns:
            bool: 加密是否成功
        """
        pass
    
    @abstractmethod
    async def decrypt_sensitive_values(
        self,
        encryption_key: str
    ) -> bool:
        """
        解密敏感配置值
        
        Args:
            encryption_key: 解密密钥
            
        Returns:
            bool: 解密是否成功
        """
        pass
    
    @abstractmethod
    def get_config_sources(self) -> Dict[str, ConfigSource]:
        """
        获取配置来源映射
        
        Returns:
            Dict[str, ConfigSource]: 键路径到配置来源的映射
        """
        pass
    
    @abstractmethod
    async def reload_from_source(
        self,
        source: ConfigSource
    ) -> bool:
        """
        从指定来源重新加载配置
        
        Args:
            source: 配置来源
            
        Returns:
            bool: 重新加载是否成功
        """
        pass 