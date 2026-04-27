# Implementation Standards

## Technical Baseline

- Use Vue 3 with the Composition API.
- Use TypeScript for component props, API inputs, and API outputs.
- Use Ant Design Vue 4.x as the base UI library.
- Use Tailwind CSS 3.x for styling composition.
- Use `unplugin-icons` and `@iconify/vue` through the project's icon wrapper.
- Use Quill for rich text editing.
- Use Vite and `pnpm` workspace conventions already present in the repo.

## Project-First Workflow

Review these local sources before implementing a new feature:

- project shared components, commonly `src/components/` or `apps/web-antd/src/components/`
- nearby pages under `src/views/`, `src/pages/`, `apps/*/src/views/`, or the project's route modules
- `docs/design-system/` when the project has design-system docs
- `docs/standards/` when workflow or form behavior is standardized
- local Swagger/OpenAPI artifacts or the live Swagger endpoint

If an existing project component already covers the requested pattern, reuse it instead of inventing a new structure. Retired template scaffolds should not be used as runtime dependencies.

## Detail Modal and Drawer Rules

- Keep the status tag on the title's right side via `titleExtra`.
- Use the subtitle for secondary context such as campus, time, or other metadata.
- Keep detail content grouped into sections with the shared class names below.
- Define the styles in the component's scoped style block when building a custom detail body.

### Required Detail Classes

| Class | Purpose |
| --- | --- |
| `.detail-section` | Section wrapper with bottom spacing |
| `.detail-section-title` | Section heading with left accent bar |
| `.detail-grid` | Default two-column information grid |
| `.detail-field` | Field wrapper |
| `.detail-field-label` | Secondary label text |
| `.detail-field-value` | Primary value text |
| `.full-width` | Span both grid columns |

### Required Detail Style Contract

```css
.detail-section {
  margin-bottom: 32px;
}

.detail-section:last-child {
  margin-bottom: 0;
}

.detail-section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  font-size: 15px;
  font-weight: 600;
  color: hsl(var(--foreground));
  border-bottom: 1px solid hsl(var(--border));
}

.detail-section-title::before {
  content: '';
  width: 3px;
  height: 16px;
  background: hsl(var(--primary));
  border-radius: var(--radius-sm);
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px 24px;
}

.detail-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.detail-field.full-width {
  grid-column: span 2;
}

.detail-field-label {
  font-size: 13px;
  color: hsl(var(--muted-foreground));
  line-height: 1.5;
}

.detail-field-value {
  font-size: 14px;
  font-weight: 500;
  color: hsl(var(--foreground));
  line-height: 1.5;
  min-height: 22px;
}
```

## Styling Rules

- Use `hsl(var(--primary))` for theme highlights instead of hard-coded theme colors.
- Use `hsl(var(--foreground))`, `hsl(var(--muted-foreground))`, `hsl(var(--border))`, `hsl(var(--card))`, and `hsl(var(--popover))` for text, borders, and surfaces.
- Use `hsl(var(--success))`, `hsl(var(--warning))`, and `hsl(var(--destructive))` for status, risk, and semantic feedback colors.
- Treat `hsl(var(--info))` as a low-emphasis information surface in Vben templates. Do not use it as a `CustomTag.color` accent because it can render low-contrast tags; use `hsl(var(--primary))`, `hsl(var(--foreground))`, or the appropriate success/warning/destructive token instead.
- Do not introduce literal `hex`, `rgb`, `rgba`, `white`, or `black` values in new system or workflow page styles. Exceptions are content media, chart palettes, official brand assets, or third-party embedded UI; document the reason inline if an exception is necessary.
- Component props that accept color strings, such as `CustomTag.color`, must receive readable token expressions like `hsl(var(--primary))`, `hsl(var(--foreground))`, or `hsl(var(--success))`, not raw palette values or low-contrast surface tokens.
- Use `var(--radius-sm)`, `var(--radius-md)`, `var(--radius-lg)`, `var(--radius-xl)`, or Tailwind semantic radius utilities instead of fixed `px` radii. Pill or circle shapes may use `rounded-full` only when the shape itself requires it.
- Use the shared page/list shell before adding local card wrappers. For top-level enterprise pages, prefer compact `p-2` or a local token-backed padding variable over broad `p-5` containers.
- Prefer soft Morandi-style colors through semantic tokens; avoid loud bright reds or oranges unless the state semantics require them.
- Keep Material Design 3 style details flat rather than heavy or overly layered.

## Table and Button Rules

- Render table action buttons as text-only actions.
- `TableLayout` owns the list card shell, header divider, quick-filter chips/cards, table content, and pagination surface. Do not duplicate those card styles locally unless the page is not a table/list page.
- Dense list rows should stay scan-friendly: align body cells to the top, keep table padding compact, give the primary text column enough width, clamp secondary descriptions to two lines, and avoid tag clusters wrapping unless the column is intentionally multi-line.
- When a cell shows multiple `CustomTag` values, cap the visible tags and show a compact `+N` overflow indicator. Keep adjacent tags visually separated with a clear horizontal gap, typically `16px` in table rows. Increase the column width before allowing tags to stack vertically in ordinary list rows.
- Classes created inside Ant Design Vue `customRender` or `h(...)` table cells may not receive Vue scoped CSS attributes. Style those cell classes with `:deep(.your-class)` or move them into a shared component/style module; do not rely on plain scoped selectors for runtime VNode classes.
- Use `<Button size="small" type="link">`.
- Add `danger` on delete actions.
- Do not place icons inside table action buttons.
- For `TableLayout` quick filters, prefer these semantic defaults:
  - `全部`, `草稿`, `已结束`, `已禁用` -> `default`
  - `待审核`, `待处理`, `待支付` -> `warning`
  - `审核中`, `进行中`, `处理中` -> `primary`
  - `已通过`, `启用中`, `已完成` -> `success`
  - `已驳回`, `失败`, `已取消` -> `destructive`
  - use `info` only when the shared component maps it to a readable foreground/background pair; do not pass `hsl(var(--info))` directly as `CustomTag.color`

## Icon Rules

- Import icons from `#/icons`.
- Prefer outline variants such as `mdi:account-outline`.
- Add new icons in `src/icons/index.ts` via `createIconifyIcon`.

## Type and API Rules

- Give all component props explicit TypeScript types.
- Give all API requests and responses explicit TypeScript types.
- Read local Swagger/OpenAPI artifacts or the live Swagger endpoint before defining interfaces.
- Use `./scripts/sync-swagger.sh` when Swagger artifacts need refreshing.

## Output and Commit Rules

- Do not create `*_UPDATE.md`, `*_FIX.md`, migration notes, or similar Markdown summaries unless the user explicitly requests them.
- If the user asks for a commit, write a concise Chinese commit message in the form `type: 简短中文描述`.
