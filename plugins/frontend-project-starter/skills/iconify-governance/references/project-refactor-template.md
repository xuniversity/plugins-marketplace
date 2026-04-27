# Project auto-refactor template

Use this when a project wants a standard Iconify shape instead of ad hoc per-feature usage.

## Target architecture

### 1. One fixed-icon barrel

Recommended file:

- `src/icons/index.ts`

Purpose:

- all fixed UI icons come from here
- feature files import from one place
- icon naming is normalized for the app

Example:

```ts
export { default as MdiBell } from '~icons/mdi/bell';
export { default as MdiAccount } from '~icons/mdi/account';
export { default as HeroiconsAcademicCapSolid } from '~icons/heroicons/academic-cap-solid';
```

### 2. One dynamic resolver

Recommended file:

- Vue: `src/icons/resolve-icon.ts`
- React: `src/icons/resolve-icon.tsx`

Purpose:

- turn raw Iconify IDs such as `mdi:account` into renderable components
- centralize cache and fallback behavior
- make offline migration possible in one place

Example:

```ts
const iconCache = new Map<string, any>();

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

### 3. One fallback wrapper component

Recommended file:

- Vue: `src/components/AppIcon.vue`
- React: `src/components/AppIcon.tsx`

Purpose:

- hide framework-specific render details
- ensure all dynamic icon rendering gets a fallback
- make it easy to switch from public runtime fetching to local registration

### 4. One canonical persisted format

Recommended rule:

- route config / menu config / API / DB all store raw Iconify IDs such as `fluent:settings-16-regular`

Avoid:

- storing app-local aliases such as `MdiBell` in DB or API payloads

## Rollout template by mode

### Mode: build_time_bundle

Use when:

- the project mainly uses `unplugin-icons` and `~icons/...`

Template:

1. Create or normalize `src/icons/index.ts`
2. Move fixed UI imports behind that barrel
3. Keep route/config/API values as raw Iconify IDs
4. Add a shared resolver only for dynamic string-based icons
5. If offline is required for dynamic icons too, add local registration or a controlled icon subset

### Mode: public_runtime_dependency

Use when:

- the project renders `mdi:...` / `heroicons:...` strings at runtime with `@iconify/vue` or `@iconify/react`
- there is no local registration or actively used self-hosted provider

Template:

1. Keep persisted values as raw Iconify IDs
2. Add `src/icons/resolve-icon.*`
3. Add `src/components/AppIcon.*`
4. Replace direct ad hoc runtime icon rendering with the shared wrapper
5. Choose one offline-safe end state:
   - local registration via `addCollection()` / `addIcon()`
   - same-origin self-hosted provider that is actually used in icon names
   - selective migration of dynamic icons into a local controlled map

### Mode: mixed_mode

Use when:

- the project already bundles some icons but still resolves other icons from runtime strings

Template:

1. Preserve the existing static barrel
2. Add or normalize one shared dynamic resolver
3. Inventory all string icon sources:
   - route meta
   - config files
   - API payloads
   - DB-backed icon fields
4. Standardize those sources on raw Iconify IDs
5. Decide whether each dynamic source should remain runtime-based or move to a local alias set
6. If intranet deployment matters, remove silent dependence on the public provider

## File checklist

- `src/icons/index.ts`
- `src/icons/resolve-icon.ts` or `src/icons/resolve-icon.tsx`
- `src/components/AppIcon.vue` or `src/components/AppIcon.tsx`
- optional: `src/icons/local-collection.ts`
- optional: `src/icons/provider.ts`

## Migration checklist

1. Run the audit first
2. Pick one canonical persisted format
3. Create one static icon barrel
4. Create one dynamic resolver
5. Replace feature-local icon helper duplicates
6. Add fallback behavior
7. Re-audit and verify offline posture
