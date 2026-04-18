---
name: vben-component-rules
description: Enforce Vben frontend implementation rules for Vue 3, TypeScript, Ant Design Vue, and template-based pages. Use when Codex creates, edits, or reviews frontend files in repositories that follow these Vben shared-component, template, and Swagger conventions.
---

# Vben Component Rules

Apply this skill before changing Vue, TypeScript, or API-facing frontend code in repositories that use this Vben template and shared component layout. Treat the shared component mapping as mandatory unless the user explicitly asks to override a project convention.

## Workflow

1. Read the local template sources before implementation.
2. Pick the required shared component instead of a primitive Ant Design Vue component or a custom substitute.
3. Apply the repository's style, icon, typing, and API constraints.
4. If the request appears to conflict with a mandatory rule, surface the conflict before proceeding.

## Required Inputs

- Read `.specify/templates/project-vben/components/README.md` before using a shared component.
- Read `.specify/templates/project-vben/pages/tag-management/` when building a new list/detail workflow.
- Read `.specify/templates/project-vben/api/` and `docs/swagger-admin.json.json` before defining request or response shapes.
- Read `.specify/templates/project-vben/docs/` when the template examples are not enough.

## Non-Negotiable Rules

- Follow the mandatory component mapping in `references/component-selection.md`.
- Follow the implementation and styling rules in `references/implementation-standards.md`.
- Do not guess API payloads or response fields; derive them from the local Swagger file.
- Do not create Markdown change-summary files unless the user explicitly asks for one.
- If a shared component already covers the requested scenario, do not build a custom replacement.

## References

- `references/component-selection.md`
- `references/implementation-standards.md`
