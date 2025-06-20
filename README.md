# 🤖 智能聊天机器人 v2.0

一个基于OpenAI GPT模型的中文智能聊天机器人，支持Web界面和命令行界面双模式运行。使用 [Memory Bank System](https://github.com/vanzan01/cursor-memory-bank) 开发框架构建，具备生产级质量保证。

## ✨ 功能特性

### 🎯 核心功能
- 🧠 基于OpenAI qwen3模型
- 💬 支持连续对话和上下文记忆
- 🌐 提供美观的Streamlit Web界面
- 💻 支持命令行界面作为备用模式
- 🔧 使用UV进行快速依赖管理
- 🚀 双界面自动切换，优先Web模式
- 📝 智能会话历史管理（限制20条消息）

### 🛡️ 增强特性 (v2.0新增)
- ⚡ **智能环境检查** - 自动检测Python版本和API密钥配置
- 🔒 **强化错误处理** - 分类错误提示（超时、API、频率限制等）
- 🎨 **优化用户体验** - 丰富的emoji提示和友好交互
- 🗑️ **对话管理** - 支持清空对话历史命令（`clear`/`清空`）
- ⏱️ **超时保护** - 30秒API调用超时保护
- 💾 **数据验证** - 输入验证和消息格式检查
- 🔧 **模块化架构** - 分离Streamlit和CLI逻辑

## 🚀 快速开始

### 环境要求

- Python >= 3.9
- UV包管理器
- OpenAI API密钥

### 安装UV（如果尚未安装）

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 项目设置

1. **克隆项目并进入目录**
```bash
git clone <your-repo-url>
cd chatbot
```

2. **同步依赖环境**
```bash
uv sync
```

3. **配置OpenAI API密钥和可选参数**

**最简单的方法**（推荐）：
```bash
# 复制配置模板
cp .env.example .env

# 编辑配置文件，填入您的API密钥
# 编辑器中打开 .env 文件，取消注释并填写实际值
```

**其他配置方法**：
```bash
# 方法1：设置环境变量
export OPENAI_API_KEY="your_actual_api_key_here"

# 方法2：手动创建.env文件
echo "OPENAI_API_KEY=your_actual_api_key_here" > .env
```

### 🔧 高级配置选项 (可选)

除了必需的API密钥外，还支持以下可选配置：

```bash
# 必需配置
OPENAI_API_KEY=your_actual_api_key_here

# OpenAI API配置
OPENAI_API_BASE=https://api.openai.com/v1      # 自定义API端点 (代理/镜像)
OPENAI_ORG_ID=your_organization_id              # OpenAI组织ID
OPENAI_PROJECT_ID=your_project_id               # OpenAI项目ID  
OPENAI_TIMEOUT=30                               # API请求超时时间（秒）

# 🔍 OpenAI请求日志配置（新增）
OPENAI_REQUEST_LOGGING=true                     # 启用OpenAI请求日志
OPENAI_LOG_LEVEL=INFO                          # OpenAI日志级别 (DEBUG/INFO/WARNING/ERROR)
LOG_REQUEST_DETAILS=true                       # 记录请求详情 (端点/模型/参数)
LOG_RESPONSE_DETAILS=true                      # 记录响应详情 (完成原因/响应长度)
LOG_TOKEN_USAGE=true                           # 记录Token使用统计
LOG_ESTIMATED_COST=true                        # 记录估算成本

# 模型配置
DEFAULT_MODEL=qwen3                            # 默认模型
MODEL_TEMPERATURE=0.7                          # 温度参数
MODEL_MAX_TOKENS=2048                          # 最大tokens

# 其他配置
LOG_LEVEL=INFO                                 # 全局日志级别
UI_THEME=light                                 # UI主题 (light/dark)
UI_LANGUAGE=zh-CN                              # 界面语言
```

**配置说明：**
- `OPENAI_API_BASE`: 用于配置代理或镜像API端点
- `OPENAI_ORG_ID`: 多组织用户的组织标识
- `OPENAI_PROJECT_ID`: 项目级别的资源管理
- `OPENAI_TIMEOUT`: API调用超时时间，默认30秒

**📊 日志配置说明：**
- `OPENAI_REQUEST_LOGGING`: 控制是否记录OpenAI API调用日志
- `OPENAI_LOG_LEVEL`: 设置日志详细程度，DEBUG最详细，ERROR最简洁
- `LOG_REQUEST_DETAILS`: 记录请求参数（端点、模型、温度等）
- `LOG_RESPONSE_DETAILS`: 记录响应信息（完成原因、响应长度等）
- `LOG_TOKEN_USAGE`: 记录输入/输出/总计tokens统计
- `LOG_ESTIMATED_COST`: 基于模型定价计算每次调用的估算成本

**🎯 不同环境的推荐配置：**

**生产环境（最小化日志）：**
```bash
OPENAI_LOG_LEVEL=WARNING
LOG_REQUEST_DETAILS=false
LOG_RESPONSE_DETAILS=false
LOG_TOKEN_USAGE=true
LOG_ESTIMATED_COST=true
```

**开发环境（详细日志）：**
```bash
OPENAI_LOG_LEVEL=DEBUG
LOG_REQUEST_DETAILS=true
LOG_RESPONSE_DETAILS=true
LOG_TOKEN_USAGE=true
LOG_ESTIMATED_COST=true
```

## 🎯 使用方法

### Web界面（推荐） 🌐

启动Streamlit Web界面：
```bash
uv run streamlit run main.py
```

然后在浏览器中打开 `http://localhost:8501`

**Web界面功能：**
- 🎨 现代化聊天界面
- 💬 实时消息展示
- ⏳ "AI正在思考..." 状态指示器
- 📱 响应式设计，支持移动设备
- 🔄 自动会话状态管理
- ⚠️ 实时错误提示和配置指导

### 命令行界面 💻

当Web界面不可用时，自动降级到命令行模式：
```bash
uv run python main.py
```

**命令行功能：**
- 📝 简洁的对话界面，丰富的emoji提示
- 🚪 支持退出命令（`quit`、`exit`、`退出`）
- 🗑️ 支持清空对话历史（`clear`、`清空`）
- 🔄 连续对话支持
- ⚠️ 智能环境检查和配置指导
- 🛡️ 异常处理（Ctrl+C、EOF等）

### 📋 命令行快捷指令

| 命令 | 功能 |
|------|------|
| `quit` / `exit` / `退出` | 退出程序 |
| `clear` / `清空` | 清空对话历史 |
| `Ctrl+C` | 安全中断程序 |

## 🔧 高级功能

### 环境检查系统

程序启动时会自动检查：
- ✅ Python版本（需要>=3.9）
- ✅ OpenAI API密钥配置
- ✅ API密钥格式验证
- ✅ 网络连接测试

### 错误处理分类

智能识别并提供针对性解决方案：
- ⏰ **超时错误** - 网络连接问题指导
- 🔑 **API错误** - 密钥配置问题指导
- 🚦 **频率限制** - 请求频率建议
- ❌ **通用错误** - 详细错误信息展示

### 性能优化

- 📈 模块加载时间：~0.66秒
- 🔄 智能对话历史管理
- ⚡ 异步处理和超时保护

## 📦 技术栈

### 核心依赖
- **openai (>=1.88.0)** - OpenAI API客户端
- **langchain (>=0.3.25)** - AI应用开发框架  
- **streamlit (>=1.46.0)** - Web界面框架
- **watchdog (>=6.0.0)** - 文件监控

### 开发工具
- **pytest (>=8.4.1)** - 测试框架
- **black (>=25.1.0)** - 代码格式化工具

### 完整依赖列表
项目使用UV管理依赖，共80个包：
- 生产依赖：`pyproject.toml`
- 锁定版本：`uv.lock`

## 🛠️ 开发指南

### 代码格式化 🎨

项目使用 **Black** 进行代码格式化，确保代码风格一致：

```bash
# 安装开发依赖（包含black）
uv sync --group dev

# 检查代码格式（不修改文件）
uv run black --check .

# 查看需要格式化的差异
uv run black --diff .

# 格式化所有Python文件
uv run black .

# 格式化特定文件
uv run black main.py

# 格式化并显示详细信息
uv run black --verbose .
```

**Black配置**（在 `pyproject.toml` 中）：
- 行长度：88字符
- 目标Python版本：3.9+
- 自动排除常见目录：`.git`, `.venv`, `build` 等

### 质量检查工具 🔍

```bash
# 代码格式化检查
uv run black --check .

# 运行测试
uv run pytest

# 组合命令：格式化 + 测试
uv run black . && uv run pytest
```

### 开发工作流 🔄

**方法1：使用 Makefile（推荐）**

```bash
# 查看所有可用命令
make help

# 开发环境初始化
make dev

# 代码格式化
make format

# 代码检查
make check

# 运行测试
make test

# 完整检查（格式+测试）
make lint

# 启动应用
make run
```

**方法2：直接使用UV命令**

```bash
# 1. 开发前 - 同步依赖
uv sync --group dev

# 2. 开发中 - 实时格式化
uv run black main.py

# 3. 提交前 - 完整检查
uv run black --check . && uv run pytest

# 4. 快速修复格式问题
uv run black .
```

### 项目结构

## 📝 Git提交规范

### 🔧 Git提交模板

为了维护项目的提交历史清晰性，请遵循以下提交消息格式：

```
<type>(<scope>): <subject>

<body>

<footer>
```

### 📋 提交类型 (type)

| 类型 | 描述 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat(ui): 添加对话历史清空功能` |
| `fix` | 修复Bug | `fix(api): 修复API超时处理逻辑` |
| `docs` | 文档更新 | `docs(readme): 更新安装说明` |
| `style` | 代码格式化 | `style(core): 格式化chatbot.py代码` |
| `refactor` | 重构代码 | `refactor(config): 重构环境配置模块` |
| `test` | 添加测试 | `test(ui): 添加CLI界面单元测试` |
| `chore` | 构建工具变动 | `chore(deps): 升级streamlit到1.46.0` |
| `perf` | 性能优化 | `perf(api): 优化API调用缓存机制` |

### 🎯 范围 (scope)

| 范围 | 描述 | 示例文件 |
|------|------|----------|
| `ui` | 用户界面 | `src/ui/streamlit_app.py`, `src/ui/cli_app.py` |
| `core` | 核心功能 | `src/core/chatbot.py`, `src/core/client.py` |
| `config` | 配置管理 | `src/config/settings.py`, `src/config/environment.py` |
| `utils` | 工具函数 | `src/utils/messages.py`, `src/utils/errors.py` |
| `docs` | 文档相关 | `README.md`, `*.md` |
| `build` | 构建配置 | `pyproject.toml`, `Makefile` |
| `env` | 环境配置 | `.env`, `uv.lock` |

### ✅ 提交示例

**🆕 新功能：**
```
feat(ui): 添加对话导出功能

- 支持导出聊天记录为JSON格式
- 添加导出按钮到Web界面
- 实现文件下载功能

Closes #15
```

**🐛 Bug修复：**
```
fix(core): 修复Streamlit环境检测警告

- 实现多层环境检测机制
- 避免直接导入Streamlit模块
- 提升用户体验和稳定性

Fixes #8
```

### 🛠️ 设置Git提交模板

**项目级设置（推荐）：**
```bash
# 创建提交模板文件
cat > .gitmessage << 'TEMPLATE'
# <type>(<scope>): <subject>
# 
# <body>
# 
# <footer>
#
# 类型: feat, fix, docs, style, refactor, test, chore, perf
# 范围: ui, core, config, utils, docs, build, env
TEMPLATE

# 设置Git使用该模板
git config commit.template .gitmessage
```

### 📏 提交消息规则

- **主题行：** 不超过50个字符，使用中文描述，动词开头
- **正文：** 每行不超过72个字符，解释"做了什么"和"为什么"
- **页脚：** 引用Issue(`Closes #123`)，重大变更(`BREAKING CHANGE`)

### 🚀 快速提交命令

```bash
# 添加所有修改并提交
git add . && git commit

# 快速修复提交
git commit -m "fix(core): 修复API调用超时问题"

# 功能提交
git commit -m "feat(ui): 添加对话导出功能"

# 文档更新
git commit -m "docs(readme): 更新Git提交规范"
```
