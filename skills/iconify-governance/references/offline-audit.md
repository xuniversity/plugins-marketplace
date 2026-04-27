# Offline and intranet audit rules

## What "offline-safe" really means

For Iconify, the important question is not "is there browser cache?" but:

- are icons bundled at build time
- are icons registered from local data at runtime
- or does the app still need to fetch icon data from an API when it renders

## Preferred safety levels

### Best: build-time bundled

Typical signals:

- `unplugin-icons`
- `~icons/...` imports
- local icon data packages such as `@iconify/json` or `@iconify-json/*`

This is the simplest path for intranet and restricted environments because icons are compiled into the app bundle.

### Good: local runtime registration

Typical signals:

- `addCollection()`
- `addIcon()`
- imported local icon JSON or generated icon subsets

This is also offline-safe for the registered icons.

### Conditional: self-hosted runtime provider

Typical signals:

- `addAPIProvider('name', { resources: [...] })`
- icon names that actually use `@name:prefix:icon`

This can work in an intranet environment, but only if:

- the provider endpoint is reachable from the deployed app
- the code really uses that provider-prefixed icon namespace

### Risky: default runtime API fetching

Typical signals:

- `@iconify/vue` or `@iconify/react` runtime icon component usage
- string icon names like `mdi:home`, `heroicons:academic-cap-solid`
- no local registration for those icons
- no actively used self-hosted provider

This usually means the browser may request icon data at runtime from the default Iconify API.

## Important caveat

Do not count browser storage cache as the real mitigation. Iconify's old browser cache APIs are not the long-term answer for deployment safety.

## What the audit script checks

The script inspects:

- package managers and package manifests
- vite/webpack/build config hints
- `~icons/...` usage
- runtime Iconify library imports
- `addCollection()`, `addIcon()`, `addAPIProvider()`
- quoted icon IDs and whether they appear to use a custom provider

It classifies the project into one of these buckets:

- `build_time_bundle`
- `safe_self_hosted_runtime`
- `mixed_mode`
- `public_runtime_dependency`
- `unknown`

## Common remediation paths

### If the repo already uses `unplugin-icons`

- keep fixed UI icons as `~icons/...` exports
- for dynamic icons, either:
  - convert them to a controlled alias map, or
  - pre-register the allowed icon set locally, or
  - generate a local icon subset at build time

### If the repo uses `@iconify/vue` / `@iconify/react` with raw strings

- keep raw IDs in config/data
- add one shared resolver
- then choose one of:
  - local registration via `addCollection()` / `addIcon()`
  - self-hosted provider that is actually referenced in icon IDs
  - migration of fixed icons to build-time exports

### If the repo has a custom provider configured but unused

- either start using provider-prefixed icon names consistently
- or remove the false sense of safety and treat the setup as public runtime dependency

## Primary references

- Iconify Search API: <https://iconify.design/docs/api/search.html>
- Iconify Vue local data registration: <https://iconify.design/docs/icon-components/vue/add-collection.html>
- Iconify icon data packages: <https://iconify.design/docs/icons/icon-data.html>
- Iconify cache note: <https://iconify.design/docs/iconify-icon/enable-cache.html>
- unplugin-icons repository: <https://github.com/unplugin/unplugin-icons>
