"""
核心启动逻辑模块
包含环境检测、启动模式选择和应用程序启动器的核心实现
"""

import os
import sys
import inspect
import logging
from enum import Enum
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass


class LaunchMode(Enum):
    """启动模式枚举"""
    AUTO = "auto"        # 自动检测
    WEB = "web"          # Web界面 (Streamlit)
    CLI = "cli"          # 命令行界面
    VALIDATE = "validate" # 架构验证模式


@dataclass
class LaunchConfig:
    """启动配置"""
    mode: LaunchMode = LaunchMode.AUTO
    debug: bool = False
    verbose: bool = False
    config_path: Optional[str] = None
    port: Optional[int] = None
    host: str = "localhost"
    
    # 环境选项
    skip_dependency_check: bool = False
    force_mode: bool = False
    
    # 额外参数
    extra_args: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.extra_args is None:
            self.extra_args = {}


def detect_environment() -> LaunchMode:
    """
    智能检测运行环境，确定最佳启动模式
    
    Returns:
        LaunchMode: 检测到的最佳启动模式
    """
    # 方法1: 检查命令行参数中是否包含streamlit
    if len(sys.argv) > 0 and 'streamlit' in sys.argv[0]:
        return LaunchMode.WEB
    
    # 方法2: 检查环境变量（Streamlit运行时设置）
    if 'STREAMLIT_SERVER_PORT' in os.environ:
        return LaunchMode.WEB
        
    # 方法3: 检查调用堆栈是否包含streamlit
    try:
        for frame_info in inspect.stack():
            if 'streamlit' in frame_info.filename:
                return LaunchMode.WEB
    except Exception:
        # 如果检查调用堆栈失败，忽略错误
        pass
    
    # 方法4: 检查是否在Jupyter环境中
    try:
        if 'ipykernel' in sys.modules:
            return LaunchMode.WEB
    except Exception:
        pass
    
    # 默认返回CLI模式
    return LaunchMode.CLI


class ApplicationLauncher:
    """应用程序启动器"""
    
    def __init__(self, config: LaunchConfig):
        self.config = config
        self.logger = self._setup_logging()
        
    def _setup_logging(self) -> logging.Logger:
        """设置日志"""
        logger = logging.getLogger("ApplicationLauncher")
        
        if self.config.debug:
            level = logging.DEBUG
        elif self.config.verbose:
            level = logging.INFO
        else:
            level = logging.WARNING
            
        logger.setLevel(level)
        
        # 如果没有处理器，添加控制台处理器
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def determine_launch_mode(self) -> LaunchMode:
        """确定最终的启动模式"""
        if self.config.mode != LaunchMode.AUTO:
            if self.config.force_mode:
                return self.config.mode
            else:
                # 非强制模式下，仍然检查环境兼容性
                detected = detect_environment()
                if detected == LaunchMode.WEB and self.config.mode == LaunchMode.CLI:
                    self.logger.warning("检测到Web环境，但指定了CLI模式。使用CLI模式。")
                return self.config.mode
        else:
            return detect_environment()
    
    def launch_web_interface(self):
        """启动Web界面"""
        try:
            self.logger.info("🌐 启动Web界面 (Streamlit)...")
            
            # 导入Web界面
            # 使用完整的模块路径
            from src.ui import run_streamlit_interface
            
            # 应用配置
            if self.config.port:
                os.environ['STREAMLIT_SERVER_PORT'] = str(self.config.port)
            if self.config.host != "localhost":
                os.environ['STREAMLIT_SERVER_ADDRESS'] = self.config.host
                
            # 启动界面
            run_streamlit_interface()
            
        except ImportError as e:
            self.logger.error(f"❌ Web界面模块导入失败: {e}")
            self.logger.info("💡 请确保安装了streamlit: uv add streamlit")
            return False
        except Exception as e:
            self.logger.error(f"❌ Web界面启动失败: {e}")
            return False
            
        return True
    
    def launch_cli_interface(self):
        """启动CLI界面"""
        try:
            self.logger.info("💻 启动命令行界面...")
            
            # 导入CLI界面
            # 使用完整的模块路径
            from src.ui import run_cli_interface
            
            # 启动界面
            run_cli_interface()
            
        except ImportError as e:
            self.logger.error(f"❌ CLI界面模块导入失败: {e}")
            return False
        except Exception as e:
            self.logger.error(f"❌ CLI界面启动失败: {e}")
            return False
            
        return True
    
    def launch_validation_mode(self):
        """启动架构验证模式"""
        try:
            self.logger.info("🔍 启动架构验证模式...")
            
            # 导入验证脚本
            import subprocess
            import sys
            
            # 运行验证脚本
            result = subprocess.run([
                sys.executable, "validate_architecture.py"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info("✅ 架构验证通过")
                print(result.stdout)
                return True
            else:
                self.logger.error("❌ 架构验证失败")
                print(result.stderr)
                return False
                
        except Exception as e:
            self.logger.error(f"❌ 验证模式启动失败: {e}")
            return False
    
    def launch(self) -> bool:
        """
        启动应用程序
        
        Returns:
            bool: 启动是否成功
        """
        try:
            # 确定启动模式
            mode = self.determine_launch_mode()
            self.logger.debug(f"使用启动模式: {mode.value}")
            
            # 根据模式启动相应界面
            if mode == LaunchMode.WEB:
                return self.launch_web_interface()
            elif mode == LaunchMode.CLI:
                return self.launch_cli_interface()
            elif mode == LaunchMode.VALIDATE:
                return self.launch_validation_mode()
            else:
                self.logger.error(f"❌ 不支持的启动模式: {mode}")
                return False
                
        except KeyboardInterrupt:
            self.logger.info("⚠️ 用户中断启动")
            return False
        except Exception as e:
            self.logger.error(f"❌ 启动过程中发生错误: {e}")
            if self.config.debug:
                import traceback
                traceback.print_exc()
            return False


def launch_application(config: LaunchConfig) -> bool:
    """
    便捷函数：启动应用程序
    
    Args:
        config: 启动配置
        
    Returns:
        bool: 启动是否成功
    """
    launcher = ApplicationLauncher(config)
    return launcher.launch() 