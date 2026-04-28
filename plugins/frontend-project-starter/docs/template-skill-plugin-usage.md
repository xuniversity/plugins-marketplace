# Frontend Starter Usage

This plugin is the distribution and initialization layer for frontend project rules, skills, docs, and shared component templates.

## Recommended Combination

Use the pieces together like this:

| Layer | Role | Source of Truth |
| --- | --- | --- |
| Frontend plugin | Installs project rules, skills, docs, and implementation assets into a target project | `plugins/frontend-project-starter` |
| Project template | Provides the runnable Vben application baseline, dependencies, aliases, runtime tokens, and shared component code | `vben-admin-simple` or another selected base template |
| Skills | Tell AI agents how to work after initialization | Installed to `.agents/skills`, exposed to Codex through `.codex/skills` |
| Project rules | Tell any agent where the canonical instructions live | `.agents/AGENTS.md`, with `AGENTS.md` and `CLAUDE.md` compatibility entry points |

The plugin should not be a runtime dependency of the generated application. After initialization, the target project owns its copied docs, skills, and component code.

Design tokens are enforced as documentation, schema validation, agent rules, and audit checks. `design-tokens.yaml` is not compiled into `theme.css`; the selected project template owns runtime CSS variables and theme hooks.

## New Project Workflow

For a new Vben project, start from the Vben template and apply the plugin implementation:

```bash
python /path/to/plugins-marketplace/plugins/frontend-project-starter/scripts/init_frontend_project.py \
  --target /path/to/new-project \
  --base-template /path/to/vben-admin-simple \
  --implementation vben \
  --update-package-json
```

If the template lives under `~/Code/template`, `--base-template` may be the directory name:

```bash
python /path/to/plugins-marketplace/plugins/frontend-project-starter/scripts/init_frontend_project.py \
  --target /path/to/new-project \
  --base-template vben-supabase-admin \
  --implementation vben \
  --update-package-json
```

Then open the target project and use normal product language with the agent. The agent should read `AGENTS.md`, follow `.agents/AGENTS.md`, and use the installed skills naturally.

## Existing Project Workflow

For an existing Vben project:

```bash
python /path/to/plugins-marketplace/plugins/frontend-project-starter/scripts/init_frontend_project.py \
  --target /path/to/existing-project \
  --implementation vben \
  --update-package-json
```

Review the dependency and alias checks printed by the script. Use `--force` only when you intentionally want to overwrite existing copied docs, skills, or shared components.

## When To Use Which Skill

- `frontend-project-starter`: use when initializing or updating a project from this plugin.
- `frontend-design-system`: use for design tokens, runtime theme boundaries, colors, radii, and visual consistency.
- `vben-component-rules`: use for Vben/Vue/Ant Design Vue implementation, list pages, shared components, detail drawers, uploads, and table density.
- `iconify-governance`: use for Iconify search, icon naming, and icon barrel changes.
- `frontend-workflow-standards`: use for statuses, save/submit behavior, validation, interruptible flows, and list ordering.

## Validation Loop

After plugin or template changes:

1. Run the initializer into a temporary target based on the current project template.
2. Run the target typecheck, for Vben usually:

   ```bash
   pnpm -F @vben/web-antd run typecheck
   ```

3. Ask an agent to create a small natural-language validation page without manually pasting every rule.
4. Validate design token docs when they change:

   ```bash
   python .agents/skills/frontend-design-system/scripts/validate_design_tokens.py . --all
   ```

5. Run the token drift audit on changed runtime files:

   ```bash
   python .agents/skills/frontend-design-system/scripts/audit_design_tokens.py . --paths <changed-runtime-files>
   ```

6. Inspect the page in a browser and feed any drift back into the plugin docs, skills, shared components, or target runtime token bridge.

## Adding Other Implementations

The current implementation is `vben`. Other frontend stacks can be added under:

```text
assets/templates/implementations/<implementation-name>/
```

Each implementation should include:

- `implementation.yaml`
- shared component or adapter files under `src/`
- dependency and alias expectations
- any implementation-specific notes in skills or docs

The initializer should keep `--implementation <name>` as the selection boundary so one plugin can support multiple frontend stacks without mixing component rules.
