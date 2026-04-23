# SentrySkills 优化计划

本文档记录已发现的 bug、需要优化的点以及技术债务。按优先级排序。

# P-1 网页加入一个更新列表

## 🔴 P0 - Critical Bugs

### Bug #1: project_path 硬编码导致日志写入错误位置

**影响**: 所有项目的日志都写入到 SentrySkills 安装目录，而非各自的项目目录

**位置**: `shared/scripts/claude_code_hook.py:90`

**问题**:

```python
"project_path": str(PROJECT_ROOT),  # PROJECT_ROOT 总是指向 SentrySkills 项目
```

**表现**:

- 多个项目使用时，日志混在 `SentrySkills/.sentryskills/base/` 目录
- 不同项目的日志无法区分
- 用户无法在自己的项目中找到日志

**修复方向**:

- 从 hook 输入中提取实际工作目录（`cwd`/`workspace_path`）
- 备选方案：使用 `Path.cwd()` 获取当前工作目录
- 确保每个项目的日志写入到 `项目根目录/.sentryskills/base/`

**测试验证**:

- 在不同目录运行 SentrySkills，检查日志位置
- 确认日志中的 `project_root` 字段正确

---

### Bug #2: Block 原因显示不清晰

**影响**: 用户无法快速理解为什么操作被阻止，降低了可用性

**位置**: `shared/scripts/claude_code_hook.py:134-144`

**问题**:

```python
# 当前输出只显示技术代码
f"   Matched : {matched_rules}\n"      # 例如: ['action:execute_command']
f"   Reason  : {reason_codes}\n"       # 例如: []
```

**实际日志文件中有更好的信息，但未被使用**:

```json
{
  "final": {
    "action": "downgrade",
    "explanation": "Preflight risks: action 'execute_command' planned"
  }
}
```

**用户看到的**:

```
[SentrySkills] BLOCKED this tool call.
   Tool    : Bash
   Trace   : cfd294a5-4c1c-440c-bf24-3747b29598d6
   Matched : ['action:execute_command']
   Reason  : []
   Action  : Refusing - do not proceed with this operation.
```

**改进方向**:

1. 使用 `result["explanation"]` 字段（人类可读的解释）
2. 将规则代码映射到描述（从 `detection_rules.json` 获取）
3. 添加风险等级说明（high/medium/low）
4. 提供缓解建议（如何安全地完成操作）

**改进后的输出示例**:

```
[SentrySkills] BLOCKED this tool call.
   Tool    : Bash
   Command : cd "d:/work/..." && python install.py
   Why     : This command execution was flagged as high-risk
   Details : - Action 'execute_command' planned
             - Requires confirmation for high-risk actions
   Risk     : MEDIUM
   Suggestion : Review the command carefully, then retry with explicit approval
   Trace   : cfd294a5-4c1c-440c-bf24-3747b29598d6
   Log file : /path/to/project/.sentryskills/base/logs/20260403_...
```

**修复步骤**:

1. 在 hook 脚本中读取 `result["explanation"]` 和 `result["final"]`
2. 加载 `detection_rules.json` 映射规则名称到描述
3. 格式化输出，添加人类可读的细节
4. 添加日志文件路径（方便用户查看完整详情）

---

## 🟡 P1 - Important Improvements

### Issue #2: 日志目录结构不清晰

**当前状态**:

- `.sentryskills/base/` 下有多种日志文件（`hook_input_*.json`, `hook_result_*.json`）
- 缺少按项目/会话的组织结构
- 历史日志难以查找和清理

**建议优化**:

- 按日期归档历史日志
- 添加日志清理工具（自动删除 N 天前的日志）
- 提供日志查询/统计脚本

---

### Issue #3: 缺少单元测试

**当前状态**: 核心脚本 `self_guard_runtime_hook_template.py` (3268 行) 无测试覆盖

**风险**:

- 重构容易引入 bug
- 难以验证检测规则的有效性
- 回归风险高

**建议添加**:

- `tests/test_detection_rules.py` - 检测规则测试
- `tests/test_preflight.py` - 预检查逻辑测试
- `tests/test_runtime.py` - 运行时监控测试
- `tests/test_output_guard.py` - 输出防护测试

---

### Issue #4: 性能优化空间

**当前性能**: 30-100ms per check

**优化方向**:

- 检测规则模式编译缓存
- 并行执行独立的检测规则
- 减少重复的文件 I/O

**目标**: <50ms per check

---

## 🟢 P2 - Nice to Have

### Issue #5: 错误处理不完善

**问题场景**:

- 日志目录无写权限时的处理
- 检测规则文件损坏时的降级策略
- 子进程超时的错误信息

**建议**:

- 添加更友好的错误提示
- fail-open 机制说明（何时降级，何时阻塞）
- 错误日志集中管理

---

### Issue #6: 配置管理不够灵活

**当前限制**:

- 策略配置只能通过 `--policy-profile` 选择预定义配置
- 无法自定义规则开关
- 无法调整阈值参数

**建议**:

- 支持项目级配置文件 `.sentryskills/config.json`
- 允许覆盖默认策略
- 提供配置验证工具

---

### Issue #7: 双路径架构未完整实现

**现状**: 文档描述了异步子 agent 路径，但实际实现总是同步执行

**缺失部分**:

- 子 agent 生成机制
- 异步结果检查逻辑
- LOW 路径的真正非阻塞实现

**参考**: `ROADMAP.md` 中的详细说明

---

## 🔧 Technical Debt

### Debt #8: 代码重复

- `claude_code_hook.py` 与主脚本有重复的常量定义
- 日志格式化逻辑在多处重复
- 缺少共享的工具函数模块

**建议**: 提取共享模块，减少重复代码

---

### Debt #9: 魔法数字和硬编码

- 硬编码的超时时间 (15s)
- 硬编码的路径分隔符
- 硬编码的日志文件名模式

**建议**: 提取为配置常量

---

### Debt #10: 文档与实现不一致

- 某些功能已实现但文档未更新
- 某些文档描述的功能实际未实现
- API 变更未同步到文档

**建议**: 建立文档更新检查清单

---

## 📋 优先级说明

- **🔴 P0 - Critical**: 阻碍基本使用或导致数据丢失，必须立即修复
- **🟡 P1 - Important**: 影响用户体验或代码质量，应尽快处理
- **🟢 P2 - Nice to Have**: 改进性优化，可安排在空闲时间处理
- **🔧 Technical Debt**: 代码清理和重构，不紧急但应逐步偿还

---

## 🔄 更新日志

- **2026-04-08**: 初始版本，记录 project_path bug 和其他优化点
