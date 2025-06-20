# Context7集成指南

## 概述

Context7集成允许聊天机器人在回答技术问题时自动检索和引用最新的技术文档，提供更准确和更新的回答。

## 配置

### 1. 环境变量设置

在`.env`文件中添加以下配置：

```bash
# 启用Context7功能
CONTEXT7_ENABLED=true

# Context7 API密钥（如果需要）
CONTEXT7_API_KEY=your_context7_api_key_here

# 最大文档token数
CONTEXT7_MAX_TOKENS=5000

# 监控的库列表（逗号分隔）
CONTEXT7_LIBRARIES=openai,langchain,streamlit,react,vue,python
```

### 2. 功能说明

当`CONTEXT7_ENABLED=true`时：
- 系统会使用`Context7EnhancedProvider`代替标准的`OpenAIProvider`
- 在处理用户查询时，系统会检测是否提到了配置的库
- 如果检测到相关库，系统会获取相关文档并添加到AI的上下文中
- AI会基于最新的文档信息提供更准确的回答

## 使用示例

### 示例1：询问OpenAI API

用户：如何使用OpenAI的function calling功能？

系统会：
1. 检测到查询中包含"openai"
2. 获取OpenAI的最新文档
3. 将文档添加到上下文
4. 基于最新文档生成回答

### 示例2：询问框架特性

用户：Streamlit最新版本有什么新功能？

系统会：
1. 检测到查询中包含"streamlit"
2. 获取Streamlit的最新版本信息和特性文档
3. 提供基于最新文档的准确回答

## 高级配置

### 自定义文档源

可以通过修改`Context7EnhancedProvider`类来添加自定义的文档源：

```python
async def _get_context7_docs(self, query: str) -> Optional[str]:
    # 添加您的自定义文档检索逻辑
    pass
```

### 性能优化

- 使用`CONTEXT7_MAX_TOKENS`控制文档大小
- 合理配置`CONTEXT7_LIBRARIES`，只监控需要的库
- 考虑添加缓存机制减少重复请求

## 故障排除

1. **Context7功能未生效**
   - 检查`CONTEXT7_ENABLED`是否设置为`true`
   - 查看日志确认是否加载了`Context7EnhancedProvider`

2. **文档检索失败**
   - 检查网络连接
   - 验证API密钥（如果需要）
   - 查看错误日志

3. **响应速度变慢**
   - 调整`CONTEXT7_MAX_TOKENS`
   - 减少监控的库数量

## 未来计划

- [ ] 集成真实的Context7 API
- [ ] 添加文档缓存机制
- [ ] 支持更多文档源
- [ ] 添加文档相关性评分
- [ ] 支持多语言文档 