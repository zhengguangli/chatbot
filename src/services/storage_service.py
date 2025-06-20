"""
文件存储服务实现
基于文件系统的数据持久化服务
"""

import json
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
import asyncio
from dataclasses import asdict

from src.interfaces.storage_service import (
    IStorageService, StorageConfig, StorageBackend, 
    QueryOptions, QueryFilter
)
from src.core.errors import (
    SystemError, ConfigError, create_system_error, 
    ErrorCode, ErrorContext
)


class FileStorageService(IStorageService):
    """
    文件存储服务实现
    使用JSON文件进行数据持久化
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.config: Optional[StorageConfig] = None
        self.data_dir: Optional[Path] = None
        self.collections: Dict[str, Dict[str, Any]] = {}
        self._initialized = False
        self._lock = asyncio.Lock()
    
    async def initialize(self, config: StorageConfig) -> bool:
        """
        初始化文件存储服务
        
        Args:
            config: 存储配置
            
        Returns:
            bool: 初始化是否成功
        """
        async with self._lock:
            try:
                if config.backend != StorageBackend.FILE:
                    raise ConfigError(
                        f"不支持的存储后端: {config.backend}",
                        ErrorCode.CONFIG_VALUE_INVALID
                    )
                
                self.config = config
                self.data_dir = Path(config.connection_string)
                
                # 创建数据目录
                self.data_dir.mkdir(parents=True, exist_ok=True)
                
                # 加载现有数据
                await self._load_all_collections()
                
                self._initialized = True
                self.logger.info(f"文件存储服务初始化成功: {self.data_dir}")
                return True
                
            except Exception as e:
                self.logger.error(f"文件存储服务初始化失败: {e}")
                return False
    
    async def store_data(
        self,
        collection: str,
        data: Dict[str, Any],
        key: Optional[str] = None
    ) -> str:
        """
        存储数据到集合
        
        Args:
            collection: 集合名称
            data: 要存储的数据
            key: 可选的唯一键，如果不提供则自动生成
            
        Returns:
            str: 数据的唯一标识符
        """
        if not self._initialized:
            raise SystemError("存储服务未初始化", ErrorCode.SYSTEM_INTERNAL_ERROR)
        
        async with self._lock:
            try:
                # 确保集合存在
                if collection not in self.collections:
                    self.collections[collection] = {}
                
                # 生成或使用提供的键
                if key is None:
                    import uuid
                    key = str(uuid.uuid4())
                
                # 添加元数据
                data_with_meta = {
                    **data,
                    "_id": key,
                    "_created_at": datetime.now().isoformat(),
                    "_updated_at": datetime.now().isoformat()
                }
                
                # 存储到内存
                self.collections[collection][key] = data_with_meta
                
                # 持久化到文件
                await self._save_collection(collection)
                
                self.logger.debug(f"数据存储成功: {collection}/{key}")
                return key
                
            except Exception as e:
                self.logger.error(f"存储数据失败: {e}")
                raise SystemError(f"存储数据失败: {str(e)}", ErrorCode.SYSTEM_INTERNAL_ERROR)
    
    async def retrieve_data(
        self,
        collection: str,
        key: str
    ) -> Optional[Dict[str, Any]]:
        """
        检索单条数据
        
        Args:
            collection: 集合名称
            key: 数据唯一标识符
            
        Returns:
            Dict[str, Any]或None: 检索到的数据
        """
        if not self._initialized:
            raise SystemError("存储服务未初始化", ErrorCode.SYSTEM_INTERNAL_ERROR)
        
        try:
            if collection not in self.collections:
                return None
            
            data = self.collections[collection].get(key)
            if data:
                # 移除内部元数据
                return {k: v for k, v in data.items() if not k.startswith('_')}
            
            return None
            
        except Exception as e:
            self.logger.error(f"检索数据失败: {e}")
            return None
    
    async def query_data(
        self,
        collection: str,
        options: Optional[QueryOptions] = None
    ) -> List[Dict[str, Any]]:
        """
        查询多条数据
        
        Args:
            collection: 集合名称
            options: 查询选项
            
        Returns:
            List[Dict[str, Any]]: 查询结果列表
        """
        if not self._initialized:
            raise SystemError("存储服务未初始化", ErrorCode.SYSTEM_INTERNAL_ERROR)
        
        try:
            if collection not in self.collections:
                return []
            
            results = list(self.collections[collection].values())
            
            # 应用分页
            start = options.offset if options else 0
            end = start + options.limit if options and options.limit else len(results)
            results = results[start:end]
            
            # 清理元数据
            return [{k: v for k, v in item.items() if not k.startswith('_')} for item in results]
            
        except Exception as e:
            self.logger.error(f"查询数据失败: {e}")
            return []
    
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
            collection: 集合名称
            key: 数据唯一标识符
            data: 更新的数据
            merge: 是否合并现有数据
            
        Returns:
            bool: 更新是否成功
        """
        if not self._initialized:
            raise SystemError("存储服务未初始化", ErrorCode.SYSTEM_INTERNAL_ERROR)
        
        async with self._lock:
            try:
                if collection not in self.collections or key not in self.collections[collection]:
                    return False
                
                if merge:
                    # 合并数据
                    existing_data = self.collections[collection][key]
                    updated_data = {**existing_data, **data}
                else:
                    # 替换数据
                    updated_data = {**data, "_id": key}
                
                updated_data["_updated_at"] = datetime.now().isoformat()
                self.collections[collection][key] = updated_data
                
                # 持久化到文件
                await self._save_collection(collection)
                
                self.logger.debug(f"数据更新成功: {collection}/{key}")
                return True
                
            except Exception as e:
                self.logger.error(f"更新数据失败: {e}")
                return False
    
    async def delete_data(
        self,
        collection: str,
        key: str
    ) -> bool:
        """
        删除数据
        
        Args:
            collection: 集合名称
            key: 数据唯一标识符
            
        Returns:
            bool: 删除是否成功
        """
        if not self._initialized:
            raise SystemError("存储服务未初始化", ErrorCode.SYSTEM_INTERNAL_ERROR)
        
        async with self._lock:
            try:
                if collection not in self.collections or key not in self.collections[collection]:
                    return False
                
                del self.collections[collection][key]
                
                # 持久化到文件
                await self._save_collection(collection)
                
                self.logger.debug(f"数据删除成功: {collection}/{key}")
                return True
                
            except Exception as e:
                self.logger.error(f"删除数据失败: {e}")
                return False
    
    async def bulk_insert(
        self,
        collection: str,
        data_list: List[Dict[str, Any]]
    ) -> List[str]:
        """
        批量插入数据
        
        Args:
            collection: 集合名称
            data_list: 数据列表
            
        Returns:
            List[str]: 插入数据的唯一标识符列表
        """
        if not self._initialized:
            raise SystemError("存储服务未初始化", ErrorCode.SYSTEM_INTERNAL_ERROR)
        
        async with self._lock:
            try:
                keys = []
                
                # 确保集合存在
                if collection not in self.collections:
                    self.collections[collection] = {}
                
                for data in data_list:
                    key = await self.store_data(collection, data)
                    keys.append(key)
                
                # 持久化到文件
                await self._save_collection(collection)
                
                self.logger.debug(f"批量插入成功: {collection}, {len(keys)}条记录")
                return keys
                
            except Exception as e:
                self.logger.error(f"批量插入失败: {e}")
                return []
    
    async def create_index(
        self,
        collection: str,
        field: str,
        unique: bool = False
    ) -> bool:
        """
        创建索引 (文件存储暂不支持索引)
        
        Args:
            collection: 集合名称
            field: 字段名
            unique: 是否唯一索引
            
        Returns:
            bool: 创建是否成功
        """
        self.logger.warning("文件存储暂不支持索引功能")
        return True  # 返回True以保持兼容性
    
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
        try:
            backup_dir = Path(backup_path)
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            collections_to_backup = collections or list(self.collections.keys())
            
            for collection in collections_to_backup:
                if collection in self.collections:
                    source_file = self.data_dir / f"{collection}.json"
                    target_file = backup_dir / f"{collection}.json"
                    
                    if source_file.exists():
                        shutil.copy2(source_file, target_file)
            
            self.logger.info(f"数据备份成功: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"数据备份失败: {e}")
            return False
    
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
        try:
            backup_dir = Path(backup_path)
            if not backup_dir.exists():
                return False
            
            collections_to_restore = collections or [
                f.stem for f in backup_dir.glob("*.json")
            ]
            
            for collection in collections_to_restore:
                backup_file = backup_dir / f"{collection}.json"
                target_file = self.data_dir / f"{collection}.json"
                
                if backup_file.exists():
                    shutil.copy2(backup_file, target_file)
            
            # 重新加载数据
            await self._load_all_collections()
            
            self.logger.info(f"数据恢复成功: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"数据恢复失败: {e}")
            return False
    
    async def get_collection_stats(
        self,
        collection: str
    ) -> Dict[str, Any]:
        """
        获取集合统计信息
        
        Args:
            collection: 集合名称
            
        Returns:
            Dict[str, Any]: 统计信息
        """
        if collection not in self.collections:
            return {"exists": False}
        
        return {
            "exists": True,
            "count": len(self.collections[collection])
        }
    
    async def close(self) -> bool:
        """
        关闭存储服务连接
        
        Returns:
            bool: 关闭是否成功
        """
        try:
            self._initialized = False
            self.collections.clear()
            self.logger.info("文件存储服务已关闭")
            return True
            
        except Exception as e:
            self.logger.error(f"关闭存储服务失败: {e}")
            return False
    
    def get_backend_type(self) -> StorageBackend:
        """
        获取存储后端类型
        
        Returns:
            StorageBackend: 后端类型
        """
        return StorageBackend.FILE
    
    # ============ 私有方法 ============
    
    async def _load_all_collections(self):
        """加载所有集合数据"""
        if not self.data_dir or not self.data_dir.exists():
            return
        
        for file_path in self.data_dir.glob("*.json"):
            collection_name = file_path.stem
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.collections[collection_name] = data
                
                self.logger.debug(f"加载集合: {collection_name}")
                
            except Exception as e:
                self.logger.error(f"加载集合失败 {collection_name}: {e}")
    
    async def _save_collection(self, collection: str):
        """保存集合到文件"""
        try:
            if not self.data_dir:
                raise SystemError("数据目录未初始化", ErrorCode.SYSTEM_INTERNAL_ERROR)
            
            file_path = self.data_dir / f"{collection}.json"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(
                    self.collections[collection],
                    f,
                    ensure_ascii=False,
                    indent=2
                )
            
        except Exception as e:
            self.logger.error(f"保存集合失败 {collection}: {e}")
            raise 