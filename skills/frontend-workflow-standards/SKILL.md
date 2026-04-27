---
name: frontend-workflow-standards
description: Use for frontend workflow statuses, save and submit semantics, frontend-first validation, interruptible workflow interactions, form or detail section heading styles, and default list sorting behavior in enterprise frontend applications.
---

# Frontend Workflow Standards

Use this skill when a frontend change touches workflow status, save/submit behavior, editable approval flows, form validation, section headings, or default business sorting.

## Required Docs

Read these docs when they exist in the target project:

- `docs/standards/表单校验与可中断流程交互规范.md`
- `docs/standards/表单与详情分节标题样式规范.md`
- `docs/standards/列表默认排序规范.md`

## Core Rules

- If the project has no stronger status contract, default user-visible application states to `草稿 / 待审核 / 审核中 / 已取消 / 已驳回 / 已通过`.
- `保存` and `提交` use the same default field validation level unless a requirement explicitly says otherwise.
- For `待审核` or `审核中` records, frontend interactions that can terminate the workflow must confirm first, terminate the current flow, then continue the requested edit/delete/cancel action automatically.
- Field-level errors should be caught before the request when the frontend has enough context.
- Form section headings use the shared divider style; detail section headings use the left-accent title style.
- Frontend pages must not override standardized backend default sorting with hardcoded `createdAt,desc`, `applyAt,desc`, or similar page-local defaults unless the requirement explicitly calls for it.
- Do not render default sorting policy as visible helper text. If the rationale matters, keep it in the standard document, API contract, or a short code comment.

## Cross-Rules

- Use `$vben-component-rules` for component selection in Vben projects.
- Use the project's linked-flow or API verification workflow when the issue may be caused by backend workflow state, approval completion, or linked business data.
