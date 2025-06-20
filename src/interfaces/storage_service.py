"""
存储服务接口定义
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class StorageBackend(Enum):
    """存储后端类型"""
    FILE = "file"
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MEMORY = "memory"


@dataclass
class StorageConfig:
    """存储配置"""
    backend: StorageBackend
    connection_string: str
    max_connections: int = 10
    timeout: int = 30
    auto_backup: bool = True
    backup_interval: int = 3600  # seconds


@dataclass
class QueryFilter:
    """查询过滤器"""
    field: str
    operator: str  # "eq", "ne", "gt", "lt", "ge", "le", "in", "like"
    value: Any


@dataclass
class QueryOptions:
    """查询选项"""
    filters: List[QueryFilter]
    sort_by: Optional[str] = None
    sort_order: str = "asc"  # "asc", "desc"
    limit: Optional[int] = None
    offset: int = 0


class IStorageService(ABC):
    """
    存储服务抽象接口
    提供统一的数据持久化和检索能力
    """
    
    @abstractmethod
    async def initialize(self, config: StorageConfig) -> bool:
        """
        初始化存储服务
        
        Args:
            config: 存储配置
            
        Returns:
            bool: 初始化是否成功
        """
        pass
    
    @abstractmethod
    async def store_data(
        self,
        collection: str,
        data: Dict[str, Any],
        key: Optional[str] = None
    ) -> str:
        """
        存储数据
        
        Args:
            collection: 集合/表名
            data: 要存储的数据
            key: 可选的唯一键
            
        Returns:
            str: 数据的唯一标识符
        """
        pass
    
    @abstractmethod
    async def retrieve_data(
        self,
        collection: str,
        key: str
    ) -> Optional[Dict[str, Any]]:
        """
        检索单条数据
        
        Args:
            collection: 集合/表名
            key: 数据唯一标识符
            
        Returns:
            Dict[str, Any]或None: 检索到的数据
        """
        pass
    
    @abstractmethod
    async def query_data(
        self,
        collection: str,
        options: Optional[QueryOptions] = None
    ) -> List[Dict[str, Any]]:
        """
        查询多条数据
        
        Args:
            collection: 集合/表名
            options: 查询选项
            
        Returns:
            List[Dict[str, Any]]: 查询结果列表
        """
        pass
    
    @abstractmethod
    async def update_data(
        self,
        collection: str,
        key: str,
        data: Dict[str, Any],
        merge: bool = True
    ) -> bool:
        """
        更新数据
        
        Args:
            collection: 集合/表名
            key: 数据唯一标识符
            data: 更新的数据
            merge: 是否合并现有数据
            
        Returns:
            bool: 更新是否成功
        """
        pass
    
    @abstractmethod
    async def delete_data(
        self,
        collection: str,
        key: str
    ) -> bool:
        """
        删除数据
        
        Args:
            collection: 集合/表名
            key: 数据唯一标识符
            
        Returns:
            bool: 删除是否成功
        """
        pass
    
    @abstractmethod
    async def bulk_insert(
        self,
        collection: str,
        data_list: List[Dict[str, Any]]
    ) -> List[str]:
        """
        批量插入数据
        
        Args:
            collection: 集合/表名
            data_list: 数据列表
            
        Returns:
            List[str]: 插入数据的唯一标识符列表
        """
        pass
    
    @abstractmethod
    async def create_index(
        self,
        collection: str,
        field: str,
        unique: bool = False
    ) -> bool:
        """
        创建索引
        
        Args:
            collection: 集合/表名
            field: 字段名
            unique: 是否唯一索引
            
        Returns:
            bool: 创建是否成功
        """
        pass
    
    @abstractmethod
    async def backup_data(
        self,
        backup_path: str,
        collections: Optional[List[str]] = None
    ) -> bool:
        """
        备份数据
        
        Args:
            backup_path: 备份文件路径
            collections: 要备份的集合列表，None表示全部
            
        Returns:
            bool: 备份是否成功
        """
        pass
    
    @abstractmethod
    async def restore_data(
        self,
        backup_path: str,
        collections: Optional[List[str]] = None
    ) -> bool:
        """
        恢复数据
        
        Args:
            backup_path: 备份文件路径
            collections: 要恢复的集合列表，None表示全部
            
        Returns:
            bool: 恢复是否成功
        """
        pass
    
    @abstractmethod
    async def get_collection_stats(
        self,
        collection: str
    ) -> Dict[str, Any]:
        """
        获取集合统计信息
        
        Args:
            collection: 集合/表名
            
        Returns:
            Dict[str, Any]: 统计信息
        """
        pass
    
    @abstractmethod
    async def close(self) -> bool:
        """
        关闭存储服务连接
        
        Returns:
            bool: 关闭是否成功
        """
        pass
    
    @abstractmethod
    def get_backend_type(self) -> StorageBackend:
        """
        获取存储后端类型
        
        Returns:
            StorageBackend: 后端类型
        """
        pass 