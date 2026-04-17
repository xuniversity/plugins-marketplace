# Agent Team Prompt Templates

Use these as ready-to-send prompts when you want the Orchestrator to apply the `agent-team` skill with consistent role selection.

Default subagent execution profile:

- `Architect Agent`, `Developer Agent`, and `Code Reviewer Agent` should default to `gpt-5.3-codex` with `high` reasoning.

## Short Default Template

```text
用 $agent-team 处理这个任务，并允许你启用 subAgent。
按默认角色选择策略拆分，先规划，再并行，再汇总。
任务是：<在这里写任务>
```

## Full Default Template

```text
用 $agent-team 处理这个任务，并允许你启用 subAgent。
你作为 Orchestrator 自主决定是否启用 Product/PM、Architect、Developer、QA、Code Reviewer、Docs、Release/Ops。
请使用最小但足够的团队配置，先做计划，再分派有边界的子任务，最后整合结果并验证。
任务是：<在这里写任务>
```

## Fixed Roles Template

```text
用 $agent-team 处理这个任务，并允许你启用 subAgent。
请固定使用这些角色：
- Architect Agent
- Developer Agent
- QA Agent
任务是：<在这里写任务>
```

## Architecture-First Template

```text
用 $agent-team 处理这个任务，并允许你启用 subAgent。
请先让 Product/PM 和 Architect 明确范围、风险和方案，再决定是否安排 Developer、QA、Docs、Release/Ops。
任务是：<在这里写任务>
```

## Implementation Template

```text
用 $agent-team 处理这个任务，并允许你启用 subAgent。
默认用 Architect + Developer + QA。
如果实现路径已经很清楚，可以跳过 Product/PM。
任务是：<在这里写任务>
```

## Review Template

```text
用 $agent-team 处理这个任务，并允许你启用 subAgent。
这是一次 review 请求，请优先使用 Architect + Code Reviewer，必要时加 QA。
任务是：<在这里写任务>
```

## UI E2E Template

```text
用 $agent-team 处理这个任务，并允许你启用 subAgent。
这是一个前端或用户流程任务，请优先使用 Architect + Developer + QA。
如果需要真实浏览器验证，请让 QA Agent 使用 $playwright 做端到端检查并提供验证证据。
任务是：<在这里写任务>
```

## Regression Proof Template

```text
用 $agent-team 处理这个任务，并允许你启用 subAgent。
这次除了实现之外，我还希望拿到真实浏览器回归验证。
请在有必要时让 QA Agent 使用 $playwright 运行关键流程并附上截图或验证结果。
任务是：<在这里写任务>
```

## Docs Template

```text
用 $agent-team 处理这个任务，并允许你启用 subAgent。
这是一次文档任务，请优先使用 Docs Agent，必要时加 Architect。
任务是：<在这里写任务>
```

## Release Template

```text
用 $agent-team 处理这个任务，并允许你启用 subAgent。
这是一次发布或运维相关任务，请优先使用 Developer + QA + Release/Ops，必要时加 Docs 和 Code Reviewer。
任务是：<在这里写任务>
```

## Strict Control Template

```text
用 $agent-team 处理这个任务，并允许你启用 subAgent。
请在每次派出子 Agent 前先说明会派哪些角色、各自负责什么、为什么值得并行，然后再执行。
任务是：<在这里写任务>
```

## Fastest Practical Template

```text
用 $agent-team 处理这个任务，并允许你启用 subAgent。
目标是最快拿到可靠结果，请使用最小但足够的团队配置，不要为了完整性把所有角色都派上。
任务是：<在这里写任务>
```
