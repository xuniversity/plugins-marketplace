# Claude 委托输出契约

当本技能将任务委托给 Claude Code 时，应要求 Claude 最终仅返回一个 JSON 对象，不要输出 markdown 代码块。

推荐结构如下：

```json
{
  "status": "ok",
  "summary": "已完成的简要说明",
  "files_changed": [
    "path/to/fileA",
    "path/to/fileB"
  ],
  "commands_run": [
    "python3 script.py",
    "./mvnw -q test -pl kepler-polaris-service"
  ],
  "verification": [
    "命令 A 成功",
    "命令 B 失败，原因是 ..."
  ],
  "risks": [
    "未覆盖的边界场景",
    "由于环境限制未执行的验证"
  ]
}
```

字段要求：

1. `status`
   - `ok`：任务完成且 Claude 认为已验证
   - `blocked`：无法继续，必须说明原因
   - `failed`：尝试过但未成功完成
2. `summary`
   - 用一句到几句简述完成情况
3. `files_changed`
   - 必须列出实际修改、创建或删除的文件
4. `commands_run`
   - 必须列出真实执行过的命令
5. `verification`
   - 简述验证结果，不能只写“已验证”
6. `risks`
   - 即使为空，也应返回空数组

如果任务受阻，推荐返回：

```json
{
  "status": "blocked",
  "summary": "无法继续执行",
  "files_changed": [],
  "commands_run": [],
  "verification": [],
  "risks": [
    "缺少明确计划步骤"
  ]
}
```
