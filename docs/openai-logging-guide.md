# OpenAI 请求响应日志功能指南

## 概述

为了更好地监控和调试OpenAI API调用，系统现在提供了详细的请求响应日志记录功能。您可以通过配置文件或环境变量来精确控制日志的详细程度。

## 功能特性

### 🚀 请求日志
- 记录API端点、模型名称、温度、最大tokens等请求参数
- 可选记录完整的请求payload（仅在DEBUG级别）
- 记录请求耗时和响应状态

### 📥 响应日志
- 记录响应解析状态和完成原因
- 记录响应内容长度
- 可选记录响应内容预览（仅在DEBUG级别）

### 📊 Token使用统计
- 详细记录输入tokens、输出tokens和总tokens
- 基于模型定价计算估算成本
- 帮助监控API使用情况

### 🔧 灵活配置
- 支持通过配置文件和环境变量控制
- 不同级别的日志详细程度
- 可以选择性启用/禁用特定类型的日志

## 配置选项

### 基本配置

```json
{
  "logging": {
    "openai_request_logging": true,     // 是否启用OpenAI日志
    "openai_log_level": "INFO",         // 日志级别
    "log_request_details": true,        // 记录请求详情
    "log_response_details": true,       // 记录响应详情
    "log_token_usage": true,           // 记录token使用
    "log_estimated_cost": true         // 记录估算成本
  }
}
```

### 环境变量配置

```bash
# 启用/禁用OpenAI日志
export OPENAI_REQUEST_LOGGING=true

# 设置日志级别
export OPENAI_LOG_LEVEL=INFO

# 控制详细程度
export LOG_REQUEST_DETAILS=true
export LOG_RESPONSE_DETAILS=true
export LOG_TOKEN_USAGE=true
export LOG_ESTIMATED_COST=true
```

## 使用场景

### 1. 生产环境（最小化日志）
```json
{
  "openai_request_logging": true,
  "openai_log_level": "WARNING",
  "log_request_details": false,
  "log_response_details": false,
  "log_token_usage": true,
  "log_estimated_cost": true
}
```

**特点：**
- 只记录警告和错误
- 不记录详细的请求/响应信息
- 保留token使用和成本统计

### 2. 开发环境（详细日志）
```json
{
  "openai_request_logging": true,
  "openai_log_level": "DEBUG",
  "log_request_details": true,
  "log_response_details": true,
  "log_token_usage": true,
  "log_estimated_cost": true
}
```

**特点：**
- 详细记录所有信息
- 包含完整的请求和响应payload
- 适合调试和开发

### 3. 静默模式（最小日志）
```json
{
  "openai_request_logging": false,
  "openai_log_level": "ERROR",
  "log_request_details": false,
  "log_response_details": false,
  "log_token_usage": false,
  "log_estimated_cost": false
}
```

**特点：**
- 几乎不产生日志
- 只记录错误信息
- 适合对日志敏感的环境

## 日志示例

### 标准INFO级别日志
```
2024-01-20 10:30:15 - services.model_providers - INFO - 🚀 OpenAI API请求开始
2024-01-20 10:30:15 - services.model_providers - INFO - 📍 端点: https://api.openai.com/v1/chat/completions
2024-01-20 10:30:15 - services.model_providers - INFO - 🤖 模型: qwen3
2024-01-20 10:30:15 - services.model_providers - INFO - 🌡️ 温度: 0.7
2024-01-20 10:30:15 - services.model_providers - INFO - 📝 最大tokens: 2048
2024-01-20 10:30:15 - services.model_providers - INFO - 💬 消息数量: 2
2024-01-20 10:30:16 - services.model_providers - INFO - ⏱️ 请求耗时: 1.23秒
2024-01-20 10:30:16 - services.model_providers - INFO - 📊 响应状态: 200
2024-01-20 10:30:16 - services.model_providers - INFO - ✅ OpenAI API响应成功
2024-01-20 10:30:16 - services.model_providers - INFO - 🎯 响应解析完成
2024-01-20 10:30:16 - services.model_providers - INFO - 🏁 完成原因: stop
2024-01-20 10:30:16 - services.model_providers - INFO - 📏 响应长度: 156字符
2024-01-20 10:30:16 - services.model_providers - INFO - 📊 Token使用情况:
2024-01-20 10:30:16 - services.model_providers - INFO -   • 输入tokens: 45
2024-01-20 10:30:16 - services.model_providers - INFO -   • 输出tokens: 32
2024-01-20 10:30:16 - services.model_providers - INFO -   • 总计tokens: 77
2024-01-20 10:30:16 - services.model_providers - INFO - 💰 估算成本: $0.000154 USD
2024-01-20 10:30:16 - services.model_providers - INFO - 🎉 OpenAI API调用完成，总tokens: 77
```

### DEBUG级别额外信息
```
2024-01-20 10:30:15 - services.model_providers - DEBUG - 📋 请求消息详情:
2024-01-20 10:30:15 - services.model_providers - DEBUG -   1. [system]: 你是一个友好的中文助手，可以回答各种问题并进行对话。请保持回答简洁明了。
2024-01-20 10:30:15 - services.model_providers - DEBUG -   2. [user]: 你好，请介绍一下自己
2024-01-20 10:30:15 - services.model_providers - DEBUG - 📦 完整请求payload:
{
  "model": "qwen3",
  "messages": [...],
  "temperature": 0.7,
  "max_tokens": 2048
}
2024-01-20 10:30:16 - services.model_providers - DEBUG - 📥 完整响应:
{
  "choices": [...],
  "usage": {...}
}
2024-01-20 10:30:16 - services.model_providers - DEBUG - 💬 响应内容预览: 你好！我是一个基于人工智能的中文助手。我可以帮助你回答各种问题，进行对话交流，提供信息查询、学习辅导、创意写作等服务。我会尽力为你提供准确、有用的回答...
```

## 错误处理

系统会特别记录API错误：

```
2024-01-20 10:30:15 - services.model_providers - ERROR - ❌ OpenAI API错误 429: Rate limit exceeded
2024-01-20 10:30:15 - services.model_providers - ERROR - 🔍 请求头 (无敏感信息): {'Content-Type': 'application/json', 'OpenAI-Organization': 'org-xxx'}
```

网络错误：
```
2024-01-20 10:30:15 - services.model_providers - ERROR - 🌐 网络请求失败: Cannot connect to host api.openai.com:443
2024-01-20 10:30:15 - services.model_providers - ERROR - 🔍 网络错误详情:
2024-01-20 10:30:15 - services.model_providers - ERROR -   • 错误类型: ClientConnectorError
2024-01-20 10:30:15 - services.model_providers - ERROR -   • 错误消息: Cannot connect to host api.openai.com:443
2024-01-20 10:30:15 - services.model_providers - ERROR -   • 端点: https://api.openai.com/v1/chat/completions
2024-01-20 10:30:15 - services.model_providers - ERROR -   • 超时设置: 30秒
```

## 最佳实践

### 1. 生产环境建议
- 设置 `openai_log_level` 为 `WARNING` 或 `ERROR`
- 禁用 `log_request_details` 和 `log_response_details`
- 保留 `log_token_usage` 和 `log_estimated_cost` 以监控使用情况

### 2. 开发调试建议
- 设置 `openai_log_level` 为 `DEBUG`
- 启用所有详细日志选项
- 注意DEBUG日志可能包含敏感信息

### 3. 成本监控
- 始终启用 `log_token_usage` 和 `log_estimated_cost`
- 定期检查日志以监控API使用成本
- 设置合理的token限制

### 4. 安全考虑
- DEBUG级别日志可能包含用户输入内容
- 生产环境避免使用DEBUG级别
- 确保日志文件的访问权限设置正确

## 配置优先级

1. 环境变量（最高优先级）
2. 运行时设置
3. 配置文件
4. 默认值（最低优先级）

通过这个灵活的日志系统，您可以根据不同的环境和需求来精确控制OpenAI API调用的日志记录行为。 