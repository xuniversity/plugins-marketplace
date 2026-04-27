---
name: iconify-governance
description: Use when adding, replacing, searching, or reviewing Iconify icons, project icon barrels, createIconifyIcon usage, dynamic route/config icons, or offline and intranet-safe icon behavior in frontend projects.
---

# Iconify Governance

Use this skill to do three things well in frontend projects that use Iconify, `unplugin-icons`, `@iconify/vue`, `@iconify/react`, or a project icon barrel:

1. Unify the project's Iconify entry and usage rules
2. Search for suitable Iconify icon names quickly
3. Audit whether the project is offline or intranet-safe, or still depends on runtime Iconify API requests

## Default Workflow

1. Audit the existing setup before changing anything when icon behavior or offline safety is in scope:

```bash
python scripts/audit_iconify_setup.py <project-path>
```

2. Pick one project-level entry strategy:

- Static UI icons: expose them from one barrel such as `src/icons/index.ts`, `apps/web-antd/src/icons/index.ts`, or a project alias like `#/icons`.
- Dynamic icons from config, routes, API, or DB: store raw Iconify IDs like `mdi:home` and render them through one shared resolver with cache and fallback.
- Avoid scattering direct `@iconify/vue`, `@iconify/react`, or `~icons/...` imports across feature files when the project already has a shared icon layer.

3. Search icon candidates when needed:

```bash
python scripts/search_iconify_icons.py "student profile" --prefixes heroicons,mdi,fluent,ph --limit 8
```

4. Implement with the project's chosen pattern.

5. Re-run the audit if you changed runtime or build behavior.

6. When the user wants a project-level rollout plan or starter skeleton, generate a tailored refactor template:

```bash
python scripts/generate_refactor_template.py --project-path <project-path>
python scripts/generate_refactor_template.py --framework vue --mode mixed
```

## Project Rules

- Fixed UI icons should live in a project icon barrel, commonly `src/icons/index.ts` or `apps/web-antd/src/icons/index.ts`.
- Feature files import fixed UI icons from the project icon barrel, commonly `#/icons`.
- Add new fixed icons with the local helper, commonly `createIconifyIcon('prefix:name')`.
- Use PascalCase export names in the form `{IconSet}{IconName}`, for example `MdiMagnify`.
- Prefer outline icons when the icon set provides them.
- Do not scatter `~icons/...` or direct `@iconify/vue` imports in feature code when the project icon barrel can cover the use case.
- Dynamic icons from routes, config, API, or DB should remain raw Iconify IDs such as `mdi:home` and be rendered through a shared resolver with a fallback.

## Non-Negotiable Rules

- Prefer one canonical icon entry per app or package.
- Prefer raw Iconify IDs in route meta, config, API payloads, and DB fields.
- Prefer local component aliases only for direct UI imports.
- Do not mix persisted aliases like `MdiBell` with persisted raw IDs like `mdi:bell` unless backwards compatibility requires it.
- For offline or intranet environments, do not treat browser cache as the solution.
- Build-time bundling, local icon registration, or a truly used self-hosted provider are the relevant offline solutions.
- If `addAPIProvider()` is configured, verify that icon names actually use that provider, such as `@icon-local:mdi:home`.
- Call out mixed mode explicitly when a repo uses both bundled `~icons/...` imports and runtime string lookups.

## Choose The Right Pattern

- Need a fixed icon in a component: add/export a local component through the shared icon barrel.
- Need icons in route meta or config: store raw Iconify IDs and resolve them through one shared runtime helper.
- Need custom SVGs: register them through `addIcon()` / `addCollection()` or the repo's local SVG loader.
- Need offline safety for all icons: prefer build-time bundling or local registration over default runtime API fetching.

Read `references/patterns.md` when you need the decision table and implementation patterns.

## Scripts

- `scripts/search_iconify_icons.py`: search suitable icons. Use short English intent phrases when possible.
- `scripts/audit_iconify_setup.py`: audit build-time versus runtime Iconify behavior, local icon data packages, custom providers, and public API dependency risk.
- `scripts/generate_refactor_template.py`: generate a project-specific rollout template with recommended entry points and migration steps.

Read `references/offline-audit.md` for detailed audit rules and `references/project-refactor-template.md` for rollout guidance.

## Cross-Rules

- In Vben projects, table action buttons stay text-only per `$vben-component-rules`.
- Do not use icons as a workaround for unclear labels in dense admin tables.
