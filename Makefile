# 🤖 智能聊天机器人 - 开发工具快捷命令
# 使用方法: make <命令名>

.PHONY: help install format check test clean run web cli

# 默认目标：显示帮助信息
help:
	@echo "🤖 智能聊天机器人 - 开发工具命令"
	@echo ""
	@echo "📦 环境管理："
	@echo "  install      安装所有依赖（包括开发依赖）"
	@echo "  clean        清理缓存文件"
	@echo ""
	@echo "🎨 代码格式化："
	@echo "  format       格式化所有Python代码"
	@echo "  check        检查代码格式（不修改文件）"
	@echo "  diff         显示格式化差异"
	@echo ""
	@echo "🧪 质量检查："
	@echo "  test         运行测试套件"
	@echo "  lint         运行代码检查和测试"
	@echo ""
	@echo "🚀 应用运行："
	@echo "  run          启动Web界面（推荐）"
	@echo "  web          启动Web界面"
	@echo "  cli          启动命令行界面"
	@echo ""
	@echo "📋 配置管理："
	@echo "  env          创建配置文件模板"

# 环境管理
install:
	@echo "📦 安装依赖..."
	uv sync --group dev

clean:
	@echo "🧹 清理缓存文件..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true

# 代码格式化
format:
	@echo "🎨 格式化Python代码..."
	uv run black .
	@echo "✅ 代码格式化完成"

check:
	@echo "🔍 检查代码格式..."
	uv run black --check .

diff:
	@echo "📋 显示格式化差异..."
	uv run black --diff .

# 质量检查
test:
	@echo "🧪 运行测试..."
	uv run pytest

lint: check test
	@echo "✅ 代码检查完成"

# 应用运行
run: web

web:
	@echo "🌐 启动Web界面..."
	uv run streamlit run main.py

cli:
	@echo "💻 启动命令行界面..."
	uv run python cli.py

# 配置管理
env:
	@if [ ! -f .env ]; then \
		echo "📋 创建配置文件..."; \
		cp .env.example .env; \
		echo "✅ 已创建 .env 文件，请编辑其中的配置项"; \
		echo "💡 提示：请设置您的 OPENAI_API_KEY"; \
	else \
		echo "⚠️  .env 文件已存在，跳过创建"; \
	fi

# 开发工作流
dev: install env
	@echo "🔧 开发环境设置完成"
	@echo "💡 接下来请编辑 .env 文件设置 API 密钥"
	@echo "🚀 然后运行 'make run' 启动应用"

# 快速修复
fix: format test
	@echo "🔧 快速修复完成：代码已格式化并通过测试" 