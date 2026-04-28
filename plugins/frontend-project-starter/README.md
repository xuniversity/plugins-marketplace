# Frontend Project Starter

Frontend Project Starter bundles reusable frontend skills plus initialization templates for design-system docs, workflow standards, Iconify governance, and shared component implementations.

## Included Skills

- `frontend-design-system`
- `frontend-project-starter`
- `frontend-workflow-standards`
- `iconify-governance`
- `vben-component-rules`

## Component Implementations

The plugin is implementation-aware. Today it ships:

- `vben`: Vue 3 + Vben + Ant Design Vue shared components copied from proven project practice and generalized through placeholder adapters.

Future implementations can be added under:

```text
assets/templates/implementations/<implementation-name>/
```

Each implementation should include an `implementation.yaml` and a `src/` tree that can be copied into a target project.

## Initialize A Project

For the intended relationship between this plugin, a runnable project template, and installed AI skills, see [`docs/template-skill-plugin-usage.md`](docs/template-skill-plugin-usage.md).

Dry run:

```bash
python scripts/init_frontend_project.py --target /path/to/project --implementation vben --dry-run
```

Install docs, canonical `.agents` rules and skills, Codex/Claude compatibility entries, and Vben components:

```bash
python scripts/init_frontend_project.py --target /path/to/project --implementation vben
```

Start from an existing frontend template repository or local template directory:

```bash
python scripts/init_frontend_project.py \
  --target /path/to/new-project \
  --base-template https://github.com/example/frontend-template.git \
  --implementation vben
```

Local templates under `~/Code/template` can also be referenced by directory name:

```bash
python scripts/init_frontend_project.py \
  --target /path/to/new-project \
  --base-template vben-supabase-admin \
  --implementation vben \
  --update-package-json
```

Useful options:

- `--base-template <git-url-or-local-template-path-or-local-name>`
- `--base-template-ref <branch-or-tag>`
- `--skills-dir .agents/skills`
- `--codex-skills-dir .codex/skills`
- `--skip-codex-skills`
- `--src-root /path/to/project/apps/web-antd/src`
- `--update-package-json`
- `--skip-docs`
- `--skip-skills`
- `--skip-project-rules`
- `--skip-components`
- `--force`
- `--list-implementations`

The initializer copies runtime project skills into `.agents/skills` by default: `frontend-design-system`, `frontend-workflow-standards`, `iconify-governance`, and `vben-component-rules`. It also exposes those skills to Codex through `.codex/skills` by creating a symlink when possible, or a mirror copy when the target already has a real `.codex/skills` directory. The plugin-level `frontend-project-starter` skill stays in the plugin because it owns the initializer workflow.

`frontend-design-system` includes `scripts/validate_design_tokens.py` for YAML/schema validation and a CI-friendly `scripts/audit_design_tokens.py` check for hardcoded UI colors and fixed px radii in runtime files. The design-token YAML is a contract and audit input; this plugin does not compile it into `theme.css`, so runtime variables stay owned by the selected base template or target project.

Generated project instruction entry points:

- `.agents/AGENTS.md`: canonical tool-neutral project instructions.
- `AGENTS.md`: thin Codex-compatible entry pointing agents to `.agents/AGENTS.md`.
- `CLAUDE.md`: Claude entry using `@.agents/AGENTS.md`.
- `.codex/skills`: Codex compatibility bridge or mirror of `.agents/skills`.

After initialization, wire the placeholder API adapters under `src/api/`, review dependency and alias checks printed by the script, run token schema validation and the runtime drift audit when relevant, then run the target project's formatter and typecheck.
