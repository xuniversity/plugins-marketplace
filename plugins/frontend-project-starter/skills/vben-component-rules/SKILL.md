---
name: vben-component-rules
description: Enforce Vben frontend implementation rules for Vue 3, TypeScript, Ant Design Vue, Swagger-derived API contracts, and required shared components. Use when Codex creates, edits, or reviews CRUD lists, detail drawers or modals, uploads, media previews, timelines, workflow status, audit workbenches, or AI-assisted UI in Vben projects.
---

# Vben Component Rules

Apply this skill before changing Vue, TypeScript, Ant Design Vue, or API-facing frontend code in Vben repositories. Treat the shared component mapping as mandatory unless the user explicitly asks to override a project convention.

## Workflow

1. Read the local shared component sources before implementation.
2. Pick the required shared component instead of a primitive Ant Design Vue component or a custom substitute.
3. Apply the repository's style, icon, typing, and API constraints.
4. Read nearby business pages before introducing a new page shape.
5. If the request appears to conflict with a mandatory rule, surface the conflict before proceeding.

## Required Inputs

- Read `references/component-selection.md` before choosing components.
- Read `references/implementation-standards.md` before changing details, table actions, icons, or API-facing code.
- Read the target project's shared component source before using a component for the first time in a task, commonly `src/components/` or `apps/web-antd/src/components/`.
- Read nearby pages under the project's `views/`, `pages/`, or route modules when implementing a similar workflow.
- Read local Swagger/OpenAPI artifacts or the live Swagger endpoint before defining request or response shapes.

## Non-Negotiable Rules

- Follow the mandatory component mapping in `references/component-selection.md`.
- Follow the implementation and styling rules in `references/implementation-standards.md`.
- Shared component color props and local scoped styles must use runtime design tokens rather than raw palette literals in system or workflow pages.
- Do not guess API payloads or response fields; derive them from the local Swagger file.
- Do not create Markdown change-summary files unless the user explicitly asks for one.
- If a shared component already covers the requested scenario, do not build a custom replacement.
- Do not rely on retired frontend template scaffolds once reusable components have been promoted into the project source tree.

## References

- `references/component-selection.md`
- `references/implementation-standards.md`
