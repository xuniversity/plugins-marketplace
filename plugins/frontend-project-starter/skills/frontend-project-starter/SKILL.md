---
name: frontend-project-starter
description: Use when initializing or bootstrapping a frontend project from the Frontend Project Starter plugin, applying design-system docs, workflow standards, Iconify governance, or selectable component implementation templates such as Vben + Ant Design Vue. Trigger when users ask to initialize a frontend project, install starter templates, choose a component implementation, or start from a base template repository.
---

# Frontend Project Starter

Use this skill when the user wants to initialize a frontend project or apply this plugin's templates to an existing project.

## Workflow

1. Identify the target project root.
2. Choose a component implementation. Default to `vben` unless the user names another implementation.
3. If the user provides a base template repository or local template directory, pass it through `--base-template`.
4. Run a dry run first when the target directory already contains source files.
5. Run the initializer script from the plugin root:

```bash
python ../../scripts/init_frontend_project.py --target <project-root> --implementation vben --dry-run
python ../../scripts/init_frontend_project.py --target <project-root> --implementation vben
```

From this skill directory, the script path is `../../scripts/init_frontend_project.py`.

The initializer copies project-level skills into `.agents/skills` by default, then exposes them to Codex through `.codex/skills` as a symlink when possible or a mirror copy when a real `.codex/skills` directory already exists. It intentionally does not copy this initialization skill into the target project; this skill belongs to the plugin and is only needed to apply or reapply the starter.

## Base Template Mode

When initializing a brand-new project from a template repo:

```bash
python ../../scripts/init_frontend_project.py \
  --target <new-project-dir> \
  --base-template <git-url-or-local-template-path> \
  --implementation vben
```

The initializer copies or clones the base template first, then overlays common docs and the chosen component implementation.
Use `--base-template-ref <branch-or-tag>` when the template repo needs a specific branch or tag. By default, the initializer removes the template `.git` directory so the target starts as a fresh project.

## Implementation Model

Component implementations live under:

```text
../../assets/templates/implementations/<implementation-name>/
```

Each implementation should include:

- `implementation.yaml`
- a `src/` tree to copy into the target project
- dependency and alias expectations in `implementation.yaml`

Use `--list-implementations` to see available implementations.

## After Initialization

- Wire placeholder API adapters under `src/api/` to the target backend.
- Confirm dependencies and aliases reported by the initializer.
- Confirm `.agents/AGENTS.md`, root `AGENTS.md`, `CLAUDE.md`, `.agents/skills`, and `.codex/skills` exist when the target project should carry its own project rules.
- Use `--update-package-json` when the initializer should add missing runtime dependencies. It preserves pnpm `catalog:` style when the target project uses it; otherwise it falls back to implementation-declared versions.
- Run the target project's formatter, typecheck, and focused frontend checks.
- For Vben projects, use `$vben-component-rules`, `$frontend-design-system`, `$frontend-workflow-standards`, and `$iconify-governance` after initialization.
