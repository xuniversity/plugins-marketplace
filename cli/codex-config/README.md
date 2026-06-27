# codex-config

`codex-config` switches between local Codex profile files under `~/.codex`.

It is intended for local workstation use. Real `config.toml.*` and `auth.json.*` files can contain tokens, model provider settings, private server URLs, and other sensitive local settings, so keep them out of this repository.

## Requirements

- POSIX shell
- `python3`
- `tomlkit` for the `sync` command

Install the Python dependency if needed:

```bash
python3 -m pip install tomlkit
```

## Install

```bash
install -m 0755 cli/codex-config/codex-config ~/.local/bin/codex-config
```

Make sure `~/.local/bin` is on `PATH`.

## Profile layout

By default, the command manages files under:

```text
~/.codex/
```

Expected profile names:

```text
~/.codex/config.toml.<suffix>
~/.codex/auth.json.<suffix>
```

Active Codex files:

```text
~/.codex/config.toml
~/.codex/auth.json
```

Override the directory when testing:

```bash
export CODEX_DIR=/tmp/codex-config-test
```

## Usage

```bash
codex-config list
codex-config current
codex-config use work
codex-config work
codex-config save-auth work
codex-config sync
codex-config sync work personal
```

`codex-config use <suffix>`:

- backs up unmatched active files before replacing them;
- copies `config.toml.<suffix>` to `config.toml`;
- copies `auth.json.<suffix>` to `auth.json` when the auth profile exists.

`codex-config sync` copies shared sections from the active `config.toml` into profile files:

- `mcp_servers`
- `skills`
- `plugins`
- `marketplaces`

Backup retention defaults to 3 unmatched backups per file. Override with:

```bash
export CODEX_CONFIG_BACKUP_KEEP=5
```

## Templates

- [`templates/config.toml.example`](./templates/config.toml.example) shows the expected profile file shape.
- [`templates/auth.json.example`](./templates/auth.json.example) is a placeholder only. Generate real auth profiles through normal Codex login flows, then save them locally with `codex-config save-auth <suffix>`.
