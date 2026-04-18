# Implementation Standards

## Technical Baseline

- Use Vue 3 with the Composition API.
- Use TypeScript for component props, API inputs, and API outputs.
- Use Ant Design Vue 4.x as the base UI library.
- Use Tailwind CSS 3.x for styling composition.
- Use `unplugin-icons` and `@iconify/vue` through the project's icon wrapper.
- Use Quill for rich text editing.
- Use Vite and `pnpm` workspace conventions already present in the repo.

## Template-First Workflow

Review these local sources before implementing a new feature:

- `.specify/templates/project-vben/components/README.md`
- `.specify/templates/project-vben/pages/tag-management/`
- `.specify/templates/project-vben/api/`
- `.specify/templates/project-vben/docs/`

If the template library already covers the requested pattern, reuse that pattern instead of inventing a new structure.

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
  color: rgba(0, 0, 0, 0.88);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.detail-section-title::before {
  content: '';
  width: 3px;
  height: 16px;
  background: hsl(var(--primary));
  border-radius: 2px;
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
  color: rgba(0, 0, 0, 0.45);
  line-height: 1.5;
}

.detail-field-value {
  font-size: 14px;
  font-weight: 500;
  color: rgba(0, 0, 0, 0.88);
  line-height: 1.5;
  min-height: 22px;
}
```

## Styling Rules

- Use `hsl(var(--primary))` for theme highlights instead of hard-coded theme colors.
- Prefer soft Morandi-style colors; avoid loud bright reds or oranges unless the state semantics require them.
- Keep Material Design 3 style details flat rather than heavy or overly layered.

## Table and Button Rules

- Render table action buttons as text-only actions.
- Use `<Button size="small" type="link">`.
- Add `danger` on delete actions.
- Do not place icons inside table action buttons.

## Icon Rules

- Import icons from `#/icons`.
- Prefer outline variants such as `mdi:account-outline`.
- Add new icons in `src/icons/index.ts` via `createIconifyIcon`.

## Type and API Rules

- Give all component props explicit TypeScript types.
- Give all API requests and responses explicit TypeScript types.
- Read `docs/swagger-admin.json.json` before defining interfaces.
- Use `./scripts/sync-swagger.sh` when Swagger artifacts need refreshing.

## Output and Commit Rules

- Do not create `*_UPDATE.md`, `*_FIX.md`, migration notes, or similar Markdown summaries unless the user explicitly requests them.
- If the user asks for a commit, write a concise Chinese commit message in the form `type: 简短中文描述`.
