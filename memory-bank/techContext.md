# Tech Context - 技术背景

## 技术栈
### 核心依赖
- **openai (>=1.88.0)** - OpenAI API客户端
- **langchain (>=0.3.25)** - AI应用开发框架  
- **streamlit (>=1.46.0)** - Web界面框架
- **watchdog (>=6.0.0)** - 文件监控

### 开发工具
- **pytest (>=8.4.1)** - 测试框架
- **black (>=25.1.0)** - 代码格式化工具
- **UV** - 现代Python包管理器

## 架构模式
- 模块化设计
- 分离的Web和CLI界面逻辑
- 环境检查和配置管理
- 错误处理分类

## 开发环境
- Python >= 3.9
- UV包管理器
- OpenAI API密钥配置
- 支持多平台（macOS/Linux/Windows）

## 性能指标
- 模块加载时间：~0.66秒
- API调用超时：30秒
- 对话历史限制：20条消息 