# Technical Context

> **Purpose**: Technical implementation details, dependencies, and environment setup.

## Development Environment
- **OS**: macOS (Darwin)
- **Shell**: /usr/local/bin/zsh
- **Working Directory**: /Users/lizhengguang/Desktop/chatbot
- **Python Version**: >= 3.9 required

## Dependencies
- **Package Manager**: UV
- **Core Dependencies**:
  - openai >= 1.88.0
  - langchain >= 0.3.25
  - streamlit >= 1.46.0
  - watchdog >= 6.0.0
  - dotenv >= 0.9.9
- **Dev Dependencies**:
  - black >= 25.1.0
  - pytest >= 8.4.1

## Build Configuration
- **格式化工具**: Black (line-length=88, target-version=py39)
- **类型检查**: mypy (计划添加)
- **测试框架**: pytest + coverage
- **包管理**: UV lock文件管理依赖版本

## Environment Variables
- **OPENAI_API_KEY**: OpenAI API密钥 (必需)
- **OPENAI_API_BASE**: 自定义API端点 (可选)
- **OPENAI_ORG_ID**: 组织ID (可选)
- **OPENAI_PROJECT_ID**: 项目ID (可选)
- **OPENAI_TIMEOUT**: API超时时间，默认30秒
- **LOG_LEVEL**: 日志级别，默认INFO

## Component Interfaces
- **IModelProvider**: AI模型抽象接口
- **ISessionManager**: 会话管理接口
- **IMessageHandler**: 消息处理接口
- **IStorageService**: 存储服务接口
- **IConfigManager**: 配置管理接口

## Data Schema
- **ChatSession**: {session_id, user_id, created_at, updated_at, model_config}
- **Message**: {message_id, session_id, role, content, timestamp, token_count}
- **ModelConfig**: {model_name, temperature, max_tokens, timeout}
- **UserConfig**: {user_id, preferences, usage_stats}

## Testing Strategy
- **单元测试**: 每个组件独立测试，覆盖率>80%
- **集成测试**: 组件间交互测试
- **性能测试**: API响应时间和并发测试
- **端到端测试**: 完整用户流程测试

## Deployment Configuration
- **本地开发**: `uv run python main.py` (CLI) 或 `uv run streamlit run main.py` (Web)
- **生产环境**: Docker容器化部署 (未来计划)
- **环境隔离**: 开发/测试/生产环境分离
- **配置管理**: 环境特定的配置文件

## Project Structure
- `src/` - Main source directory
  - `core/` - Core chatbot functionality
  - `ui/` - User interface modules (streamlit & CLI)
  - `config/` - Configuration management
  - `utils/` - Utility functions
- `main.py` - Entry point
- `pyproject.toml` - Project configuration 