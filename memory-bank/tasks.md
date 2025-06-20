# Tasks - Active Task Tracking

> **Purpose**: Central hub for active, in-progress task tracking with detailed steps, checklists, and component lists.

## Current Task Status
- **Last Task**: 项目结构优化 - 将cli.py和main.py移入src并优化代码 ✅ **已归档**
- **Status**: **ARCHIVED** ✅
- **Complexity Level**: Level 2 - 简单增强

## Completed Task Summary
- [x] Task requirements analyzed
- [x] Complexity level determined (Level 2)
- [x] Project structure optimization planned
- [x] **启动器模块架构设计** ✅
- [x] **创建src/launcher模块** ✅
- [x] **实现src/main.py优化版本** ✅
- [x] **实现src/cli.py专用版本** ✅
- [x] **创建根目录启动代理** ✅
- [x] **测试和验证新架构** ✅
- [x] **向后兼容性确认** ✅
- [x] **QA验证和问题修复** ✅
- [x] **项目结构优化完成** ✅
- [x] **任务归档** ✅

## Archive Information
- **Archive Date**: 2025年06月20日
- **Archive Document**: [archive-project-structure-optimization-20250620.md](archive/archive-project-structure-optimization-20250620.md)
- **Completion Status**: ✅ COMPLETED AND ARCHIVED

## Key Achievements
### 🏗️ 项目结构现代化
- **新增代码**: 1,154行高质量代码
- **启动器模块**: src/launcher/ 完整实现
- **命令行选项**: 11个新功能选项
- **向后兼容性**: 100%保持

### 🛠️ 技术改进
- **智能启动**: 4种启动模式自动检测
- **用户体验**: 显著提升的启动体验
- **代码组织**: 清晰的模块化结构
- **错误处理**: 友好的错误提示

### 🔧 QA问题修复
- **相对导入修复**: 5个文件的导入问题已解决
- **Memory Bank同步**: 文档状态一致性确保
- **技术验证**: 4/4 QA检查点通过

## Next Task
**Ready for new task assignment**

---

**最后更新**: 2025年06月20日  
**状态**: 准备接受新任务  
**系统**: Memory Bank已重置，可开始新的VAN模式 

# Task: 项目整体重构

## Description
对当前 chatbot 项目进行一次全面的代码重构，旨在提高代码库的清晰度、可维护性、模块化程度和可扩展性。重构将遵循单一职责原则，消除冗余代码，并建立清晰、一致的架构模式。

## Complexity
- **Level**: 4
- **Type**: Complex System

## Technology Stack
- **Language**: Python
- **Framework**: (无特定框架，但使用了Streamlit进行UI展示)
- **Build Tool**: (无)
- **Testing**: Pytest

## Technology Validation Checkpoints
- [ ] 确认 Python 环境和依赖 (`uv.lock`) 完整
- [ ] 确认 `pytest` 可正常运行测试
- [ ] 确认 `streamlit` 可正常启动

## Status
- [ ] 待办
- [ ] 进行中
- [ ] 已完成

## Implementation Plan

### Phase 1: 结构清理与入口统一
- [ ] **分析和删除根目录脚本**: 评估根目录下的 `cli.py` 和 `main.py`，确认 `src/launcher` 可以完全替代后，将其删除。
- [ ] **强化启动器**: 确保 `src/launcher/core.py` 是唯一的应用启动入口，能够处理所有启动模式（CLI, Streamlit）。
- [ ] **清理 `__pycache__`**: 在重构前，全局清理 `__pycache__` 目录，避免缓存问题。

### Phase 2: 服务层与数据接口重构
- [ ] **合并 `interfaces` 和 `services`**:
    - 分析 `src/interfaces` 和 `src/services` 中功能重叠的模块（如 `MessageHandler`, `SessionManager`, `StorageService`）。
    - 将 `interfaces` 中的逻辑合并到 `services` 的对应模块中，以 `services` 为主。
    - 删除 `src/interfaces` 目录。
- [ ] **统一数据模型**: 检查 `src/core/models.py`，确保其作为唯一的数据模型定义来源。

### Phase 3: UI 层重构
- [ ] **移除v1 UI**: 删除 `src/ui/cli_app.py` 和 `src/ui/streamlit_app.py`。
- [ ] **重构v2 UI**:
    - 将 `src/ui/cli_app_v2.py` 重命名为 `src/ui/cli.py`。
    - 将 `src/ui/streamlit_app_v2.py` 重命名为 `src/ui/streamlit.py`。
    - 更新 UI 代码以适应服务层的变动。

### Phase 4: 配置与核心逻辑重构
- [ ] **统一配置管理**:
    - 将 `src/core/config.py` 的逻辑迁移到 `src/config/settings.py`。
    - 删除 `src/core/config.py`。
    - 确保所有模块通过 `src/config` 获取配置。
- [ ] **重构 `core` 模块**:
    - 明确 `src/core/chatbot.py` 和 `src/core/client.py` 的职责。
    - `chatbot.py` 应专注于会话和消息处理的核心逻辑。
    - `client.py` 应作为与外部服务（如模型API）交互的客户端。

### Phase 5: 测试与验证 (QA)
- [ ] **更新/创建单元测试**: 为重构后的模块编写或更新单元测试。
- [ ] **端到端测试**: 执行 `tests/test_end_to_end.py`，确保核心功能在重构后依然正常。
- [ ] **手动QA**:
    - 测试CLI模式下的所有功能。
    - 测试Streamlit模式下的所有功能。
    - 验证数据持久化（会话、消息）是否正常。

## Creative Phases Required
- [x] **Architecture Design**: 需要在执行前对目标架构进行更详细的设计和可视化。

## Dependencies
- 项目模块之间存在高度耦合，修改时需小心。

## Challenges & Mitigations
- **Challenge**: 重构范围广，容易引入回归错误。
- **Mitigation**: 严格遵循分阶段实施，每个阶段后都进行测试。利用版本控制系统（git）频繁提交，方便回滚。
- **Challenge**: `interfaces` 和 `services` 的逻辑合并可能复杂。
- **Mitigation**: 在合并前，先绘制出两个模块的依赖关系图，确保没有遗漏。 