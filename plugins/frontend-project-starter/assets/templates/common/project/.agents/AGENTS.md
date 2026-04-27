## Scope

This file defines the default frontend workflow for this project. It is tool-neutral and should be shared by Codex, Claude, Cursor, and other agent runtimes.

## Skills

Canonical project skills live under `./.agents/skills`. Tool-specific skill directories, such as `./.codex/skills`, should point to or mirror this canonical directory.

- `frontend-design-system`: use for design-system docs, design tokens, theme variables, runtime token boundaries, and token-backed styling.
- `vben-component-rules`: use for Vue 3, TypeScript, Ant Design Vue, Vben shared components, CRUD lists, detail modals or drawers, uploads, timelines, workflow status, and AI-assisted UI.
- `iconify-governance`: use when adding, replacing, searching, or reviewing Iconify icons and project icon barrels.
- `frontend-workflow-standards`: use for workflow statuses, save/submit semantics, validation, interruptible interactions, section headings, and default list sorting.

## Frontend Rules

- Prefer shared components under `web-antd/src/components`, `apps/web-antd/src/components`, or the project's equivalent shared component directory before building custom Ant Design Vue wrappers.
- Read `docs/design-system/ai-ui-rules.md`, `docs/design-system/component-recipes.md`, `docs/design-system/design-tokens.yaml`, and `docs/design-system/runtime-token-map.md` before design-sensitive work.
- Runtime colors and radii should use semantic tokens. Avoid literal `hex`, `rgb`, `rgba`, `white`, `black`, and fixed `px` radii in new system or workflow UI.
- For dense enterprise pages, prefer shared shells or compact `p-2`/token-backed page padding. Avoid broad `p-5` page containers unless the existing local pattern requires them.
- Do not add visible helper text that explains standards, scoring, or sorting policy unless the requirement asks for that message.
- Fixed UI icons should be exported from `web-antd/src/icons/index.ts` or the project's equivalent icon barrel; feature code should import from that barrel.

## Verification

- After frontend code changes, run a focused type or syntax check when feasible.
- For Vben projects, prefer `pnpm -F @vben/web-antd run typecheck` as the default targeted check.
