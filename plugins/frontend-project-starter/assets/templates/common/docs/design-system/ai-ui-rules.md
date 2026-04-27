# AI UI Rules

## Read Order

For design-sensitive frontend work, read these files first:

1. `docs/design-system/component-recipes.md`
2. `docs/design-system/design-tokens.yaml`
3. `docs/design-system/runtime-token-map.md`

For workflow forms, detail views, or approval-like interactions, also read:

- `docs/standards/表单校验与可中断流程交互规范.md`
- `docs/standards/表单与详情分节标题样式规范.md`
- `docs/standards/列表默认排序规范.md`

## Surface Modes

- `System Mode`: admin dashboards, CRUD pages, settings pages, operational tools.
- `Workflow Mode`: application forms, approval flows, record details, status transitions.
- `Portal Mode`: public-facing pages, brand surfaces, landing-style content.

## Non-Negotiable Rules

- Use existing shared components before building local substitutes.
- Use runtime design tokens for colors, surfaces, status, and radii in System and Workflow pages.
- Use compact page shells for enterprise work surfaces. Prefer shared shells or `p-2`/token-backed padding variables over broad `p-5` containers.
- Avoid literal `hex`, `rgb`, `rgba`, `white`, `black`, and fixed `px` radii in runtime Vue/CSS unless the value is content media, official brand material, a chart palette, or a documented third-party exception.
- Do not add subtitles, helper copy, slogans, or decorative gradients unless the requirement or existing design explicitly asks for them.
- Do not add visible governance explanations such as default sorting rationale; keep that in docs, API contracts, or comments.
- For dense enterprise pages, prioritize scanability, stable layout, and predictable workflows over marketing composition.
