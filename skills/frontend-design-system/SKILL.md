---
name: frontend-design-system
description: Use when working on frontend design systems, themes, design tokens, tenant or brand overlays, visual consistency, runtime token boundaries, or token-backed Vue/CSS styling in enterprise frontend projects.
---

# Frontend Design System

Use this skill before design-sensitive frontend changes, especially dashboards, workflow surfaces, portal pages, theme variables, tenant overlays, and design-token updates.

## Workflow

1. Classify the surface as `System Mode`, `Workflow Mode`, or `Portal Mode`.
2. Read the relevant shared docs when present:
   - `docs/design-system/ai-ui-rules.md`
   - `docs/design-system/component-recipes.md`
   - `docs/design-system/design-tokens.yaml`
   - `docs/design-system/runtime-token-map.md`
3. If the change is tenant or brand-specific, read `docs/design-system/tenant-overrides/`.
4. Check whether each token is runtime-capable, portal-derived, or documentation-first before using it in code.
5. For component selection in Vben projects, switch to `$vben-component-rules`.
6. Before finalizing design-sensitive Vue/CSS changes, scan touched runtime files for token drift (`hex`, `rgb`, `rgba`, `white`, `black`, fixed `px` radii) and either replace them with semantic tokens or record why the value is an allowed exception.

## Non-Negotiable Rules

- Use `hsl(var(--...))`, Tailwind semantic classes, or scoped brand tokens only within the correct surface.
- Do not treat portal or brand-only tokens as global admin-page tokens.
- For System Mode and Workflow Mode, do not add literal `hex`, `rgb`, `rgba`, `white`, or `black` UI colors in runtime Vue/CSS. Use runtime-capable tokens such as `--primary`, `--foreground`, `--muted-foreground`, `--border`, `--card`, `--success`, `--warning`, `--destructive`, and `--info`.
- Color props on shared components are still UI colors. Pass token expressions or approved semantic names, not raw palette values, unless the value comes from persisted business data or an official brand asset.
- Use `--radius`, `--radius-sm`, `--radius-md`, `--radius-lg`, `--radius-xl`, or semantic Tailwind radius utilities for corners. Fixed `px` radii are exceptions, not defaults.
- For System Mode and Workflow Mode page shells, prefer the shared page/list component shell or a compact `p-2`/token-backed padding variable. Do not generate broad `p-5` page containers unless an existing local page pattern explicitly requires it.
- Keep governance rationale in docs or code comments, not visible UI copy. Do not surface explanatory lines such as why a list is sorted unless the user requirement explicitly asks for that on-screen message.
- Do not add subtitles, helper copy, slogans, decorative gradients, or hardcoded brand colors unless the requirement or existing design explicitly calls for them.
- When runtime behavior and design docs disagree, obey the current runtime chain first and update docs deliberately.
- When using derived variables such as `--radius-lg`, verify that the target runtime defines them. If not, add a runtime bridge from `--radius` before relying on them.
- If a runtime CSS variable is added, update `design-tokens.yaml` and `runtime-token-map.md` together when those files exist.

## Token Self-Check

For changed runtime Vue/CSS files, run a focused grep or token-drift scanner before final response. Treat findings in docs, generated assets, charts, official brand media, and third-party embedded UI as possible exceptions; treat findings in system or workflow page styling as issues to fix.
