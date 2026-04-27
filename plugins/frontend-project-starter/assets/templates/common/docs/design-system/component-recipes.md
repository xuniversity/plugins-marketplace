# Component Recipes

## Recipe 1: Workflow System Page Shell

Use for dashboards, CRUD lists, audit pages, and settings pages.

- Use a quiet page background and token-backed surfaces.
- Use shared table, filter, detail, upload, and status components.
- Use `--background`, `--card`, `--foreground`, `--muted-foreground`, `--border`, `--primary`, and status semantic tokens.
- Use `--radius-*` or semantic Tailwind radius utilities instead of fixed `px` radii.
- Use the shared shell or compact page padding. `p-2` is the default top-level spacing for dense enterprise pages; larger padding should come from an established local pattern or a token-backed CSS variable.
- Keep operational rationale, scoring notes, and sorting explanations out of visible helper text unless the user explicitly asks for them.

## Recipe 2: Filter Header And Search Toolbar

Use for search plus quick-filter list pages.

- Keep the toolbar functional, not decorative.
- Treat `TableLayout` as the owner of list card, header, quick-filter, table, and pagination styling.
- Inputs, selects, and buttons should share height and border language.
- Keep dense rows aligned to the top, not visually centered against multi-line descriptions.
- Give descriptive primary columns enough width, clamp secondary descriptions to two lines, and keep ordinary tag clusters on one line with a compact `+N` overflow indicator.
- Use a clear horizontal gap between adjacent tags in table cells, typically `16px`; avoid visually touching borders or shadows between sibling tags.
- Quick filter semantic defaults:
  - `全部`, `草稿`, `已结束`, `已禁用` -> `default`
  - `待审核`, `待处理`, `待支付` -> `warning`
  - `审核中`, `进行中`, `处理中` -> `primary`
  - `已通过`, `启用中`, `已完成` -> `success`
  - `已驳回`, `失败`, `已取消` -> `destructive`
  - use `info` only when the shared component maps it to a readable foreground/background pair; do not pass `hsl(var(--info))` directly as `CustomTag.color`

## Recipe 3: Detail Drawer And Detail Modal

- Put status tags on the title's right side when the component supports it.
- Use subtitle for secondary context such as location, time, or source metadata.
- Keep detail content grouped into sections with shared detail classes.
- Do not create a one-off detail visual language for a single page.

## Recipe 4: Workflow Form Surface

- Use consistent section headings.
- Validate field-level errors on the frontend when enough context is available.
- Clearly separate save, submit, cancel, and destructive actions.
- Keep workflow-interrupting actions confirmable and resumable.

## Recipe 5: Status Tag And Flow Summary

- Status colors come from semantic tokens.
- Status blocks should help users identify business stage, not act as decoration.
- Workflow-backed statuses should use the shared workflow status component when available.
- For business/category tags, avoid low-contrast information-surface tokens. Prefer readable accents such as `primary`, `foreground`, `success`, `warning`, or `destructive`.
