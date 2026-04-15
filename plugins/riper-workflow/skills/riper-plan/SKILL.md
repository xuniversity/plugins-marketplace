---
name: riper-plan
description: 当用户发出“进入计划模式”、“进入PLAN模式”、“ENTER PLAN MODE”等类似指令时，使用这个技能。
---

# RIPER 计划模式

在当前模式中，你可以进行任务拆解与规划，指定完整的实施计划。

## 规则

**输出格式**：每个响应必须以 `[MODE: PLAN]` 开头

**初始上下文收集**（在创建计划前必须先运行这些命令）：

审查近期更改以了解当前状态：
```bash
git log -n 10 -p --since="1 week ago" -- .
```

获取近期工作概览：
```bash
git diff HEAD~10..HEAD --stat
```

检查进行中的工作模式：
```bash
git log -n 10 --oneline --grep="WIP\|TODO\|FIXME"
```

**允许的操作**：
- 创建详细的技术规范
- 定义实现步骤
- 记录设计决策
- 仅可写入仓库根目录的 `.agents/memory-bank/*/plans/` （使用 `git rev-parse --show-toplevel` 查找根目录）
- 识别风险与缓解措施

**禁止的操作**：
- 向项目文件写入实际代码
- 执行实现命令
- 修改现有代码
- 写入仓库根目录 `.agents/memory-bank/*/plans/` 目录之外的位置

## 计划文档管理

通过以下方式将计划保存至仓库根目录：
1. 首先运行：`git rev-parse --show-toplevel` 以获取仓库根目录路径
2. 然后在以下位置创建计划：`[根目录]/.agents/memory-bank/[分支名]/plans/[日期]-[功能].md`

示例：如果仓库根目录是 `/path/to/repo`，则保存到：
`/path/to/repo/.agents/memory-bank/分支名称/plans/2025-01-06-功能名称.md`

必需的计划章节：
- 元数据（日期、分支、状态）
- 技术规范
- 实现步骤（编号）
- 测试要求
- 成功标准

## 输出模板

```
[MODE: PLAN]

## 创建技术规范

### 计划位置
1.  运行：`git rev-parse --show-toplevel` 以获取仓库根目录
2.  保存到：`[根目录]/.agents/memory-bank/[分支名]/plans/[文件名].md`

### 规范
[详细的技术设计]

### 实现步骤
1.  [具体操作]
2.  [具体操作]

### 成功标准
- [ ] [可衡量的结果]
```

## 工具使用限制

- ✅ Read：所有文件
- ✅ Write：仅可写入 `[根目录]/.agents/memory-bank/*/plans/`（通过 `git rev-parse --show-toplevel` 获取根目录）
- ✅ Bash：可执行命令
- ❌ Edit：不可用于项目文件

## 模式切换

当被调用时，检查上下文：
- 如果任务涉及"plan"、"specify"、"design"

记住：你处理的是RIPER工作流程的计划阶段。计划时要详细，但永远不要偏离规范。