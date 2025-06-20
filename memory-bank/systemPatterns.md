# System Patterns

> **Purpose**: Architectural decisions, design patterns, and system-wide conventions.

## Architecture Overview
- **架构风格**: 渐进式重构的分层架构
- **核心原则**: 单一职责、开放封闭、依赖倒置
- **重构策略**: 保持UI层，重构业务层，优化数据层

## Design Patterns
- **分层架构模式**: 表示层 → 业务层 → 数据层
- **策略模式**: IModelProvider支持多AI模型切换
- **依赖注入模式**: 组件间依赖通过接口注入
- **仓储模式**: 数据访问抽象化

## Technology Stack
- **Programming Language**: Python 3.9+
- **Web Framework**: Streamlit (保留现有)
- **CLI Framework**: 自定义CLI处理器
- **AI Integration**: OpenAI API + 扩展接口
- **Build Tools**: UV包管理器
- **Testing**: pytest + coverage
- **Code Quality**: Black formatter + type hints

## Code Conventions
- **命名规范**: 类名PascalCase，函数名snake_case
- **接口设计**: 以I前缀标识接口，ABC定义抽象方法
- **错误处理**: 自定义业务异常，结构化错误信息
- **文档要求**: 公共方法必须包含docstring和类型注解

## Integration Points
- **AI模型集成**: 通过IModelProvider接口统一
- **配置管理**: 环境变量 + 配置文件分层管理
- **存储集成**: 文件存储 + 内存缓存混合模式
- **UI集成**: 适配器模式支持多种界面

## Security Patterns
- **API密钥管理**: 环境变量存储，运行时加载
- **数据加密**: 敏感信息本地加密存储
- **访问控制**: 会话隔离，用户数据独立
- **输入验证**: 用户输入清理和长度限制

## Performance Patterns
- **异步处理**: AI调用使用异步模式减少阻塞
- **缓存策略**: 会话和配置信息内存缓存
- **连接复用**: HTTP连接池复用降低延迟
- **资源管理**: 及时释放文件句柄和网络连接 