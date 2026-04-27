# Runtime Token Map

## Purpose

This file records which design tokens are actually wired into the target application's runtime theme. Keep it updated when token variables, theme preferences, or CSS bridges change.

## Runtime-Capable Anchors

Use these CSS variables as the default runtime anchors when they exist:

- Surface: `--background`, `--background-deep`, `--card`, `--popover`
- Text: `--foreground`, `--muted-foreground`, `--card-foreground`, `--popover-foreground`
- Brand and interaction: `--primary`, `--primary-foreground`, `--ring`
- Status: `--success`, `--warning`, `--destructive`
- Information surfaces: `--info`, `--info-foreground`
- Border and input: `--border`, `--input`, `--input-background`, `--input-placeholder`
- Shape: `--radius`, `--radius-sm`, `--radius-md`, `--radius-lg`, `--radius-xl`
- Overlay and shell: `--overlay`, `--overlay-content`, `--header`, `--sidebar`

`--radius-sm`, `--radius-md`, `--radius-lg`, and `--radius-xl` are runtime-derived from `--radius`. If the target framework only defines `--radius`, add the derived variables in the theme CSS and in the preference/theme update hook before using them in shared components.

`--info` may be a low-emphasis surface token in Vben-derived themes. Do not treat it as a readable accent for `CustomTag.color` unless the target runtime proves enough contrast; use `--info-foreground`, `--primary`, `--foreground`, or another readable semantic token instead.

## Documentation-First Families

These are useful design constraints but may not be live runtime preferences yet:

- spacing scale
- full typography scale
- global shadow scale
- motion duration/easing scale
- multi-tenant brand palette switching

## Governance Rules

- If a runtime CSS variable is added, update `design-tokens.yaml` and this map in the same change.
- If a token is only a design target, mark it as `documentation-first`.
- If a token only exists inside one scoped surface, mark it as scoped and do not use it globally.
- Prefer fixing shared token bridges before replacing many page-level literals.
