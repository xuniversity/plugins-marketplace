# kuse

`kuse` switches the active kubeconfig by symlinking `~/.kube/config` to a named kubeconfig profile under `~/.kube/envs`.

It stores and uses local kubeconfig files only. Real kubeconfig files contain cluster endpoints and credentials, so keep them out of this repository.

## Requirements

- Bash
- `kubectl`

## Install

```bash
install -m 0755 cli/kuse/kuse ~/.local/bin/kuse
```

Make sure `~/.local/bin` is on `PATH`.

## Profile layout

By default, profiles live here:

```text
~/.kube/envs/<env>.yaml
```

The active kubeconfig path defaults to:

```text
~/.kube/config
```

Both paths can be overridden:

```bash
export KUSE_DIR="$HOME/.kube/envs"
export KUBE_CONFIG_PATH="$HOME/.kube/config"
```

## Usage

```bash
kuse list
kuse current
kuse use dev
kuse prod
kuse add staging ~/Downloads/staging-kubeconfig.yaml
kuse remove staging
kuse path prod
```

`kuse add` copies a kubeconfig into `KUSE_DIR` and sets file permissions to `0600`.

## Template

Use [`templates/kubeconfig.example.yaml`](./templates/kubeconfig.example.yaml) only as a shape reference. Replace every placeholder with values from a real kubeconfig and store the result outside this repository.
