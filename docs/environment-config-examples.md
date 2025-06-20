# 环境变量配置示例

本文档提供了不同使用场景下的环境变量配置示例，帮助您快速设置适合的配置。

## 🚀 快速开始

### 1. 复制配置模板

```bash
# 复制配置模板
cp .env.example .env

# 编辑配置文件
# 使用您喜欢的编辑器打开 .env 文件
```

### 2. 基本配置（最小化）

仅配置必需的API密钥：

```bash
# .env 文件内容
OPENAI_API_KEY=your_actual_api_key_here
```

### 3. 开发环境配置（推荐）

适合开发和调试的详细配置：

```bash
# 基本配置
OPENAI_API_KEY=your_actual_api_key_here

# 详细日志配置（开发环境）
OPENAI_REQUEST_LOGGING=true
OPENAI_LOG_LEVEL=DEBUG
LOG_REQUEST_DETAILS=true
LOG_RESPONSE_DETAILS=true
LOG_TOKEN_USAGE=true
LOG_ESTIMATED_COST=true

# 模型配置
DEFAULT_MODEL=qwen3
MODEL_TEMPERATURE=0.7
MODEL_MAX_TOKENS=2048
```

## 📊 不同场景配置

### 🛠️ 开发调试环境

用于本地开发，需要详细的调试信息：

```bash
# 开发环境 .env 配置
OPENAI_API_KEY=your_api_key
OPENAI_LOG_LEVEL=DEBUG
LOG_REQUEST_DETAILS=true
LOG_RESPONSE_DETAILS=true
LOG_TOKEN_USAGE=true
LOG_ESTIMATED_COST=true
LOG_LEVEL=DEBUG
```

**特点：**
- 🔍 最详细的日志信息
- 📝 完整的请求/响应记录
- 💰 实时成本监控
- 🐛 便于问题诊断

### 🏭 生产环境

适合生产部署，日志简洁但保留关键信息：

```bash
# 生产环境 .env 配置
OPENAI_API_KEY=your_api_key
OPENAI_LOG_LEVEL=WARNING
LOG_REQUEST_DETAILS=false
LOG_RESPONSE_DETAILS=false
LOG_TOKEN_USAGE=true
LOG_ESTIMATED_COST=true
LOG_LEVEL=INFO
```

**特点：**
- ⚠️ 只记录警告和错误
- 📊 保留Token使用统计
- 💰 保留成本监控
- 🚀 高性能，低存储开销

### 🔇 静默模式

最小化日志输出，适合对日志敏感的环境：

```bash
# 静默模式 .env 配置
OPENAI_API_KEY=your_api_key
OPENAI_REQUEST_LOGGING=false
OPENAI_LOG_LEVEL=ERROR
LOG_REQUEST_DETAILS=false
LOG_RESPONSE_DETAILS=false
LOG_TOKEN_USAGE=false
LOG_ESTIMATED_COST=false
LOG_LEVEL=WARNING
```

**特点：**
- 🤫 几乎无日志输出
- ❌ 只记录严重错误
- 🏃‍♂️ 最佳性能
- 🔒 最高隐私保护

### 💰 成本监控模式

专注于API使用成本监控：

```bash
# 成本监控 .env 配置
OPENAI_API_KEY=your_api_key
OPENAI_LOG_LEVEL=INFO
LOG_REQUEST_DETAILS=false
LOG_RESPONSE_DETAILS=false
LOG_TOKEN_USAGE=true
LOG_ESTIMATED_COST=true
DEFAULT_MODEL=qwen3
MODEL_MAX_TOKENS=1024  # 限制tokens降低成本
```

**特点：**
- 📊 详细的Token使用统计
- 💰 精确的成本估算
- 🎯 专注成本控制
- 📈 便于使用分析

## 🌐 代理/镜像配置

### 使用API代理

如果需要通过代理访问OpenAI API：

```bash
# 代理配置
OPENAI_API_KEY=your_api_key
OPENAI_API_BASE=https://your-proxy.com/v1
OPENAI_TIMEOUT=60  # 代理可能需要更长超时时间
```

### 使用第三方兼容API

如果使用与OpenAI API兼容的其他服务：

```bash
# 兼容API配置
OPENAI_API_KEY=your_compatible_api_key
OPENAI_API_BASE=https://api.compatible-service.com/v1
DEFAULT_MODEL=compatible_model_name
```

## 🏢 企业配置

### 多组织管理

```bash
# 企业配置
OPENAI_API_KEY=your_api_key
OPENAI_ORG_ID=org-your_organization_id
OPENAI_PROJECT_ID=proj_your_project_id

# 生产级日志配置
OPENAI_LOG_LEVEL=WARNING
LOG_TOKEN_USAGE=true
LOG_ESTIMATED_COST=true
```

## 📝 环境变量设置方法

### 方法1：.env 文件（推荐）

```bash
# 1. 复制模板
cp .env.example .env

# 2. 编辑文件
nano .env  # 或使用您喜欢的编辑器

# 3. 重启应用以应用配置
```

### 方法2：命令行设置

```bash
# 临时设置（当前终端会话）
export OPENAI_API_KEY="your_api_key"
export OPENAI_LOG_LEVEL="DEBUG"

# 启动应用
uv run streamlit run src/main.py
```

### 方法3：系统环境变量

```bash
# macOS/Linux 添加到 ~/.bashrc 或 ~/.zshrc
echo 'export OPENAI_API_KEY="your_api_key"' >> ~/.zshrc
source ~/.zshrc

# Windows 使用系统设置或 PowerShell
$env:OPENAI_API_KEY="your_api_key"
```

## 🔍 配置验证

启动应用后，查看日志确认配置是否正确加载：

```bash
# 启动应用并查看配置信息
uv run streamlit run src/main.py

# 应该看到类似的日志：
# INFO - OpenAI Provider配置成功，使用模型: qwen3
# INFO - 🔍 OpenAI请求日志已启用，级别: INFO
```

## ⚠️ 安全提醒

- 🔐 **永远不要将 .env 文件提交到版本控制**
- 🔑 **API密钥应当保密，不要分享给他人**
- 🚫 **生产环境避免使用DEBUG级别日志**
- 📝 **定期轮换API密钥以确保安全**

## 🆘 故障排除

### 配置未生效

1. 确认文件名为 `.env`（注意前面的点）
2. 确认文件位于项目根目录
3. 重启应用程序
4. 检查环境变量优先级

### API密钥问题

1. 确认密钥格式正确（以 `sk-` 开头）
2. 确认密钥有效且未过期
3. 检查API配额和限制
4. 验证网络连接

### 日志问题

1. 确认日志级别设置正确
2. 检查日志文件权限
3. 验证配置语法正确 