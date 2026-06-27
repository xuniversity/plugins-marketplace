# CLI Tools

This directory keeps small internal command-line tools that are useful across projects.

The CLI tools here are source scripts and templates only. Do not commit personal runtime configuration, tokens, kubeconfig files, Codex `config.toml` profiles, or `auth.json` profiles. Use the `.example` files as templates and keep real files under the user's home directory.

## Tools

- [`kuse`](./kuse/README.md): switch between local kubeconfig environment profiles.
- [`codex-config`](./codex-config/README.md): switch and sync local Codex config/auth profiles.

## Install

Install a tool by copying the script into a directory on `PATH`, for example:

```bash
install -m 0755 cli/kuse/kuse ~/.local/bin/kuse
install -m 0755 cli/codex-config/codex-config ~/.local/bin/codex-config
```

These tools are not marketplace plugins. They are intentionally kept under `cli/` so they can be reviewed and installed explicitly.
