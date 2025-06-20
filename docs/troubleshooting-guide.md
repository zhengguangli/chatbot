# 故障排除指南

本文档记录了项目开发过程中遇到的问题和解决方案，帮助用户快速解决常见问题。

## 🚀 启动相关问题

### 问题1: Streamlit事件循环错误

**错误信息：**
```
RuntimeError: There is no current event loop in thread 'ScriptRunner.scriptThread'.
```

**原因：**
- Streamlit运行在独立的线程中，与主线程的事件循环不兼容
- 异步代码在不同线程间调用时出现事件循环冲突

**解决方案：**
1. **延迟创建asyncio.Lock**：避免在模块导入时创建
2. **使用ThreadPoolExecutor**：在独立线程中运行异步函数
3. **创建专用入口文件**：`src/streamlit_app.py`避免启动器冲突

**相关文件：**
- `src/ui/adapters.py` - 修复了Lock的延迟创建
- `src/ui/streamlit.py` - 改进了异步处理
- `src/streamlit_app.py` - 专用Streamlit入口

### 问题2: 多实例启动

**现象：**
- 每次运行`make run`都在新端口启动新实例
- 出现8501, 8502, 8503等多个端口

**原因：**
- subprocess方式启动导致进程隔离
- 旧进程没有正确关闭

**解决方案：**
1. **使用直接导入**：避免subprocess启动方式
2. **环境变量配置**：通过环境变量传递配置
3. **进程清理**：使用`pkill -f streamlit`清理

### 问题3: ThreadPoolExecutor警告

**警告信息：**
```
Thread 'ThreadPoolExecutor-2_0': missing ScriptRunContext! This warning can be ignored when running in bare mode.
```

**原因：**
- ThreadPoolExecutor中的线程缺少Streamlit的脚本运行上下文

**解决方案：**
- 简化异步处理逻辑
- 使用更直接的事件循环管理
- 在必要时保持事件循环而不是立即关闭

## 📊 OpenAI日志相关问题

### 问题4: 日志配置不生效

**现象：**
- 设置了环境变量但日志级别没有改变
- Token使用统计没有显示

**解决方案：**
1. **检查.env文件**：确保位于项目根目录
2. **重启应用**：环境变量需要重新加载
3. **验证配置**：使用测试脚本验证配置加载

**测试命令：**
```bash
uv run python -c "
import sys, os
sys.path.append('src')
from services.model_providers import OpenAIProvider
provider = OpenAIProvider()
print('日志配置:', provider.log_config)
"
```

### 问题5: API密钥相关错误

**错误信息：**
```
⚠️ 启动检查发现问题:
  • 未设置 OPENAI_API_KEY 环境变量，AI功能将不可用
```

**解决方案：**
1. **设置API密钥**：
```bash
# 方法1: 编辑.env文件
cp .env.example .env
# 然后编辑.env文件，设置OPENAI_API_KEY=your_key

# 方法2: 临时设置
export OPENAI_API_KEY=your_key
```

2. **验证设置**：
```bash
echo $OPENAI_API_KEY
```

## 🔧 配置相关问题

### 问题6: 导入错误

**错误信息：**
```
attempted relative import beyond top-level package
```

**原因：**
- 相对导入路径错误
- Python路径配置问题

**解决方案：**
- 所有导入改为绝对导入
- 确保`src`目录在Python路径中

### 问题7: 模块找不到

**错误信息：**
```
ModuleNotFoundError: No module named 'contracts'
```

**解决方案：**
1. **检查目录结构**：确保在项目根目录运行
2. **检查Python路径**：
```python
import sys
print(sys.path)
```
3. **使用正确的启动方式**：
```bash
# 正确方式
cd /path/to/chatbot
uv run streamlit run src/streamlit_app.py

# 或者
make run
```

## 📝 日志调试技巧

### 启用详细日志

**开发环境配置：**
```bash
# .env文件设置
LOG_LEVEL=DEBUG
OPENAI_LOG_LEVEL=DEBUG
LOG_REQUEST_DETAILS=true
LOG_RESPONSE_DETAILS=true
LOG_TOKEN_USAGE=true
LOG_ESTIMATED_COST=true
```

**生产环境配置：**
```bash
# .env文件设置
LOG_LEVEL=WARNING
OPENAI_LOG_LEVEL=WARNING
LOG_REQUEST_DETAILS=false
LOG_RESPONSE_DETAILS=false
LOG_TOKEN_USAGE=true
LOG_ESTIMATED_COST=true
```

### 查看实时日志

**Streamlit应用日志：**
- 日志会直接显示在终端中
- 使用浏览器开发者工具查看前端错误

**API调用日志：**
- DEBUG级别显示完整的请求/响应
- INFO级别显示基本的调用信息
- WARNING级别只显示警告和错误

## 🆘 常用调试命令

### 检查进程状态
```bash
# 查看Streamlit进程
ps aux | grep streamlit

# 清理所有Streamlit进程
pkill -f streamlit
```

### 检查配置状态
```bash
# 验证环境变量
env | grep OPENAI

# 测试API连接
uv run python -c "
import os
print('API Key:', os.getenv('OPENAI_API_KEY', 'Not Set')[:10] + '...')
"
```

### 测试组件功能
```bash
# 测试OpenAI Provider
uv run python -c "
import sys
sys.path.append('src')
from services.model_providers import OpenAIProvider
provider = OpenAIProvider()
print('Provider初始化成功')
"
```

## 📞 获取帮助

如果遇到未列出的问题：

1. **检查日志**：启用DEBUG级别查看详细信息
2. **查看文档**：阅读README.md和其他文档
3. **验证环境**：确保Python版本和依赖正确
4. **重新安装**：必要时重新创建虚拟环境

### 完全重置环境
```bash
# 清理虚拟环境
rm -rf .venv

# 重新安装依赖
uv sync

# 重新配置环境变量
cp .env.example .env
# 编辑.env文件设置API密钥
```

### 验证安装
```bash
# 检查依赖
uv run python -c "import streamlit, openai; print('Dependencies OK')"

# 测试启动
uv run streamlit run src/streamlit_app.py
``` 