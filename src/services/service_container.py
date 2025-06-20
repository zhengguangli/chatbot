"""
服务容器实现
负责依赖注入和服务生命周期管理
"""

from typing import Dict, Any, Optional, Type, TypeVar
import logging
from dataclasses import dataclass
import os

from src.interfaces.storage_service import IStorageService, StorageConfig, StorageBackend
from src.interfaces.session_manager import ISessionManager
from src.interfaces.message_handler import IMessageHandler
from src.interfaces.model_provider import IModelProvider
from src.interfaces.config_manager import IConfigManager

from .storage_service import FileStorageService
from .session_manager import SessionManager
from .message_handler import MessageHandler
from .model_providers import OpenAIProvider, ModelProviderRegistry

T = TypeVar('T')


@dataclass
class ServiceConfig:
    """服务配置"""
    storage_path: str = "./data"
    openai_api_key: Optional[str] = None
    log_level: str = "INFO"
    enable_cache: bool = True


class ServiceContainer:
    """
    服务容器
    管理所有服务的创建、配置和生命周期
    """
    
    def __init__(self, config: Optional[ServiceConfig] = None):
        self.config = config or ServiceConfig()
        self.logger = self._setup_logging()
        
        # 服务实例
        self._services: Dict[str, Any] = {}
        self._initialized = False
    
    async def initialize(self) -> bool:
        """初始化所有服务"""
        try:
            self.logger.info("开始初始化服务容器...")
            
            # 1. 初始化存储服务
            await self._initialize_storage_service()
            
            # 2. 初始化会话管理器
            await self._initialize_session_manager()
            
            # 3. 初始化消息处理器
            await self._initialize_message_handler()
            
            # 4. 初始化模型提供者
            await self._initialize_model_providers()
            
            self._initialized = True
            self.logger.info("服务容器初始化完成")
            return True
            
        except Exception as e:
            self.logger.error(f"服务容器初始化失败: {e}")
            return False
    
    def get_service(self, service_identifier) -> Optional[Any]:
        """获取服务实例"""
        # 支持类型和字符串两种方式
        if isinstance(service_identifier, str):
            # 字符串映射
            mapping = {
                'storage_service': 'IStorageService',
                'session_manager': 'ISessionManager', 
                'message_handler': 'IMessageHandler',
                'model_registry': 'ModelProviderRegistry'
            }
            service_name = mapping.get(service_identifier, service_identifier)
        else:
            # 类型对象
            service_name = service_identifier.__name__
            
        return self._services.get(service_name)
    
    def get_storage_service(self) -> Optional[IStorageService]:
        """获取存储服务"""
        return self.get_service(IStorageService)
    
    def get_session_manager(self) -> Optional[ISessionManager]:
        """获取会话管理器"""
        return self.get_service(ISessionManager)
    
    def get_message_handler(self) -> Optional[IMessageHandler]:
        """获取消息处理器"""
        return self.get_service(IMessageHandler)
    
    def get_model_provider_registry(self) -> Optional[ModelProviderRegistry]:
        """获取模型提供者注册表"""
        return self._services.get("ModelProviderRegistry")
    
    def get_openai_provider(self) -> Optional[OpenAIProvider]:
        """获取OpenAI提供者"""
        return self._services.get("OpenAIProvider")
    
    async def shutdown(self) -> bool:
        """关闭所有服务"""
        try:
            self.logger.info("开始关闭服务容器...")
            
            # 关闭存储服务
            storage_service = self.get_storage_service()
            if storage_service:
                await storage_service.close()
            
            # 清理服务实例
            self._services.clear()
            self._initialized = False
            
            self.logger.info("服务容器已关闭")
            return True
            
        except Exception as e:
            self.logger.error(f"关闭服务容器失败: {e}")
            return False
    
    async def close(self):
        """关闭服务容器（别名）"""
        return await self.shutdown()
    
    def get_status(self) -> Dict[str, Any]:
        """获取服务容器状态"""
        return {
            'initialized': self._initialized,
            'services': self.get_service_status(),
            'config': {
                'storage_path': self.config.storage_path,
                'log_level': self.config.log_level,
                'enable_cache': self.config.enable_cache
            }
        }
    
    # ============ 私有方法 ============
    
    async def _initialize_storage_service(self):
        """初始化存储服务"""
        self.logger.debug("初始化存储服务...")
        
        # 创建存储配置
        storage_config = StorageConfig(
            backend=StorageBackend.FILE,
            connection_string=self.config.storage_path
        )
        
        # 创建文件存储服务
        storage_service = FileStorageService(logger=self.logger)
        
        # 初始化
        success = await storage_service.initialize(storage_config)
        if not success:
            raise RuntimeError("存储服务初始化失败")
        
        self._services["IStorageService"] = storage_service
        self.logger.info(f"文件存储服务初始化成功: {self.config.storage_path}")
    
    async def _initialize_session_manager(self):
        """初始化会话管理器"""
        self.logger.debug("初始化会话管理器...")
        
        storage_service = self.get_storage_service()
        if not storage_service:
            raise RuntimeError("存储服务未初始化")
        
        session_manager = SessionManager(
            storage_service=storage_service,
            logger=self.logger
        )
        
        self._services["ISessionManager"] = session_manager
        self.logger.debug("会话管理器初始化成功")
    
    async def _initialize_message_handler(self):
        """初始化消息处理器"""
        self.logger.debug("初始化消息处理器...")
        
        message_handler = MessageHandler(logger=self.logger)
        
        self._services["IMessageHandler"] = message_handler
        self.logger.debug("消息处理器初始化成功")
    
    async def _initialize_model_providers(self) -> bool:
        """初始化模型提供者"""
        try:
            self.logger.debug("初始化模型提供者...")
            
            # 创建模型提供者注册表
            provider_registry = ModelProviderRegistry(self.logger)
            
            # 检查是否启用Context7
            context7_enabled = os.getenv("CONTEXT7_ENABLED", "false").lower() == "true"
            
            if context7_enabled:
                # 使用Context7增强的提供者
                try:
                    from .context7_enhanced_provider import Context7EnhancedProvider
                    provider = Context7EnhancedProvider(
                        api_key=self.config.openai_api_key,
                        logger=self.logger
                    )
                    self.logger.info("使用Context7增强的OpenAI提供者")
                except ImportError:
                    self.logger.warning("无法导入Context7增强提供者，回退到标准OpenAI提供者")
                    provider = OpenAIProvider(
                        api_key=self.config.openai_api_key,
                        logger=self.logger
                    )
            else:
                # 使用标准OpenAI提供者
                provider = OpenAIProvider(
                    api_key=self.config.openai_api_key,
                    logger=self.logger
                )
            
            # 注册提供者
            provider_registry.register_provider("openai", provider)
            self.logger.info("提供者 openai 注册成功")
            
            provider_registry.set_default_provider("openai")
            self.logger.info("默认提供者设置为: openai")
            
            # 初始化所有提供者
            init_configs = {
                "openai": {"api_key": self.config.openai_api_key}
            }
            
            results = await provider_registry.initialize_all_providers(init_configs)
            
            if results.get("openai", False):
                self.logger.info("提供者 openai 初始化成功")
            else:
                self.logger.warning("OpenAI提供者初始化失败，但继续运行")
            
            # 将服务添加到容器
            self._services["ModelProviderRegistry"] = provider_registry
            self._services["OpenAIProvider"] = provider
            
            self.logger.debug("模型提供者初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"初始化模型提供者失败: {e}")
            return False
    
    def _setup_logging(self) -> logging.Logger:
        """设置日志"""
        logger = logging.getLogger("ServiceContainer")
        
        # 设置日志级别
        level = getattr(logging, self.config.log_level.upper(), logging.INFO)
        logger.setLevel(level)
        
        # 如果没有处理器，添加一个控制台处理器
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def is_initialized(self) -> bool:
        """检查是否已初始化"""
        return self._initialized
    
    def get_service_status(self) -> Dict[str, bool]:
        """获取所有服务状态"""
        status = {}
        
        for service_name, service in self._services.items():
            # 简单的状态检查
            status[service_name] = service is not None
        
        return status


# 全局服务容器实例
_global_container: Optional[ServiceContainer] = None


async def get_global_container(config: Optional[ServiceConfig] = None) -> ServiceContainer:
    """获取全局服务容器实例"""
    global _global_container
    
    if _global_container is None:
        _global_container = ServiceContainer(config)
        await _global_container.initialize()
    
    return _global_container


async def shutdown_global_container():
    """关闭全局服务容器"""
    global _global_container
    
    if _global_container:
        await _global_container.shutdown()
        _global_container = None
