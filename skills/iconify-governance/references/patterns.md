# Recommended Iconify patterns

## Goal

Give the project one consistent answer to each of these questions:

- Where do fixed UI icons come from?
- What format do persisted icon values use?
- How are dynamic icon names resolved?
- What is the offline/intranet-safe path?

## Recommended decision table

| Scenario | Preferred pattern |
|---|---|
| Fixed UI icon in a component | Export a component from one barrel like `src/icons/index.ts` |
| Route meta or menu config icon | Store a raw Iconify ID like `fluent:settings-16-regular` |
| API / DB / backend payload icon | Store a raw Iconify ID like `mdi:account` |
| Dynamic user-configured icon | Resolve raw ID through one shared helper with cache + fallback |
| Custom local SVG icon | Register it locally with `addIcon()` / `addCollection()` or the repo's SVG loader |

## Strong defaults

- Static imports:
  prefer one barrel, for example `#/icons`
- Persisted values:
  prefer raw Iconify IDs such as `heroicons:academic-cap-solid`
- Dynamic rendering:
  prefer one shared resolver that caches component creation and falls back to a safe icon

## Why raw Iconify IDs are the safest persisted format

Raw Iconify IDs are portable across frameworks and rendering strategies:

- Vue runtime component: `icon="mdi:account"`
- React runtime component: `icon="mdi:account"`
- Build-time reference: `~icons/mdi/account`
- Migration target: self-hosted provider or local registration can still keep the same semantic ID

By contrast, local aliases like `MdiAccount` are app-specific and tightly coupled to one barrel file.

## Minimal shared runtime resolver pattern

Use a shared helper when icons come from routes, config, APIs, or user-managed records.

```ts
const iconCache = new Map<string, Component | null>();

export function resolveIconifyIcon(iconName?: string) {
  const normalized = iconName?.trim();
  if (!normalized) {
    return null;
  }

  if (!iconCache.has(normalized)) {
    try {
      iconCache.set(normalized, createIconifyIcon(normalized));
    } catch {
      iconCache.set(normalized, null);
    }
  }

  return iconCache.get(normalized);
}
```

Pair it with:

- one fallback icon
- one validation point for allowed icon formats
- one place to switch from public runtime API to local registration later

## Anti-patterns to call out

- Persisting `MdiBell` in backend data while other places store `mdi:bell`
- Directly importing `~icons/...` in many feature files when the project already has an icon barrel
- Creating multiple helper functions that each resolve dynamic icon names differently
- Mixing Ant Design icons with Iconify in an Iconify-first codebase unless there is a project-level exception
- Assuming a configured provider removes risk even when icon names never reference that provider

## Migration guidance

If the project already mixes component aliases and raw Iconify IDs:

1. Keep existing runtime behavior stable
2. Standardize new persisted values on raw Iconify IDs
3. Add compatibility mapping only where needed
4. Move fixed UI imports behind the shared barrel
5. Re-run the audit after the refactor
