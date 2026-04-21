---
name: yunxiao-bug-export
description: Use when you need to export Yunxiao project bug lists, unresolved bug details, rich-text screenshots, and dated Markdown or JSON artifacts through the official alibabacloud-devops-mcp-server. Trigger when the user asks to read Yunxiao bugs, inspect bug details with images, or migrate browser-based Projex harvesting to an MCP-first workflow.
---

# Yunxiao Bug Export

## Overview

This skill exports Yunxiao bugs through the official `alibabacloud-devops-mcp-server` instead of relying on a logged-in browser session. It preserves the repo-local artifact workflow from the old bug harvest flow, but writes outputs under dated directories so later fixing work can consume stable JSON, Markdown, and downloaded screenshots.

## When To Use

Use this skill when one or more of the following are true:

- The bug data lives in Yunxiao project management, not an open webpage
- The user wants bug lists, unresolved bug details, attachments, or inline screenshots
- The output should become reusable repo-local artifacts for follow-up fixing work
- The user wants the official Yunxiao MCP path to be the primary implementation
- A browser-session scraping flow would be brittle or session-dependent

Do not use this skill as the first choice when the user explicitly wants browser scraping or when the target system is outside Yunxiao.

## Workflow

### 1. Prefer MCP-first export

Use the bundled exporter to talk to the official MCP server over stdio. The exporter:

- resolves the current `organizationId`
- resolves the target project by `--project-id`, `--project-name`, or `--project-alias`
- optionally reads a repo-local project config file for alias reuse and default project selection
- pages through Yunxiao bugs with `search_workitems`
- loads per-bug details with `get_work_item`
- loads attachment metadata with `list_workitem_attachments`
- resolves inline image file identifiers with `get_workitem_file`
- downloads signed screenshot URLs immediately before they expire
- materializes a dated artifact directory under `docs/output/yunxiao-bugs/YYYY-MM-DD/`

Recommended command:

```bash
bash scripts/export_yunxiao_bugs.sh \
  --project-name "就业项目" \
  --output-dir "/absolute/path/to/docs/output"
```

By default, the exporter exports unresolved bugs by excluding these statuses:

- `已修复`
- `已关闭`
- `暂不解决`

The exporter also tolerates nearby variants such as `暂不修复` and `已解决`. This default is more reusable across different Yunxiao projects than hardcoding only a few in-progress states. Use `--all-bugs` only when you explicitly want every bug status.

### Project reuse options

Preferred reuse mode:

- direct call-time selection with `--project-id` or `--project-name`
- optional alias-based reuse with `--project-alias`
- optional repo config at `.codex/yunxiao-bug-export.projects.json`

Config file example:

```json
{
  "defaultProjectAlias": "job3",
  "projects": {
    "job3": {
      "organizationId": "f3fdeb6e-03b5-406d-b1dd-c79104fc0f5e",
      "projectId": "a27b5e78f058a07cf351e424c2",
      "projectName": "就业项目",
      "customCode": "NJUJOB",
      "excludedStatuses": ["已修复", "已关闭", "暂不解决"]
    }
  }
}
```

An example file is bundled at [assets/projects.example.json](assets/projects.example.json).

Resolution priority is:

- explicit CLI arguments
- `--project-alias`
- `defaultProjectAlias` from config
- the only project in config, if exactly one exists

The exporter first reads the current shell environment. If `YUNXIAO_ACCESS_TOKEN` or `YUNXIAO_API_BASE_URL` are missing there, it falls back to `~/.codex/config.toml` under `[mcp_servers.yunxiao.env]`.

### Installation and dependency requirements

This skill is installable from a marketplace in one step, but successful execution still depends on the Yunxiao MCP runtime being available on the machine.

Required dependency:

- `alibabacloud-devops-mcp-server` must be installed and callable. The simplest setup is a global npm install:

```bash
npm install -g alibabacloud-devops-mcp-server
```

Required Codex config:

```toml
[mcp_servers.yunxiao]
command = "alibabacloud-devops-mcp-server"

[mcp_servers.yunxiao.env]
YUNXIAO_ACCESS_TOKEN = "pt-..."
YUNXIAO_API_BASE_URL = "https://your-org.devops.aliyuncs.com"
```

Notes:

- `YUNXIAO_ACCESS_TOKEN` and `YUNXIAO_API_BASE_URL` may be placed either in the shell environment or in `~/.codex/config.toml`
- the exporter will fall back to `~/.codex/config.toml` automatically when the shell environment is missing these variables
- the script still expects the MCP server package to exist locally because it talks to the official server over stdio and loads the MCP SDK from that installation

If neither source is available, set:

```bash
export YUNXIAO_ACCESS_TOKEN="..."
export YUNXIAO_API_BASE_URL="https://your-org.devops.aliyuncs.com"
```

The exporter trims a trailing slash from `YUNXIAO_API_BASE_URL` automatically because the official MCP server can misroute requests when the base URL ends with `/`.

### 2. Materialize stable dated artifacts

The output contract is:

- `docs/output/yunxiao-bugs/YYYY-MM-DD/README.md`
- `docs/output/yunxiao-bugs/YYYY-MM-DD/yunxiao-bug-list-cache.json`
- `docs/output/yunxiao-bugs/YYYY-MM-DD/yunxiao-bugs-full.json`
- `docs/output/yunxiao-bugs/YYYY-MM-DD/yunxiao-bugs-summary.json`
- `docs/output/yunxiao-bugs/YYYY-MM-DD/yunxiao-bugs-grouped.md`
- `docs/output/yunxiao-bugs/YYYY-MM-DD/bugs/*.md`
- `docs/output/yunxiao-bugs/YYYY-MM-DD/yunxiao-bug-images/*`
- `docs/output/yunxiao-bugs/LATEST`

This keeps every run grouped by date instead of flattening artifacts into a single directory.

### 3. Re-materialize when raw data already exists

If the raw list cache, full JSON, and optional image map have already been captured, regenerate the dated Markdown and summary artifacts with:

```bash
bash scripts/materialize_yunxiao_bugs.sh \
  --list-url "yunxiao-mcp://project/<PROJECT_ID>/bugs" \
  --list-cache-file "/absolute/path/to/list-cache.json" \
  --full-json-file "/absolute/path/to/full-items.json" \
  --output-dir "/absolute/path/to/docs/output" \
  --image-map-file "/absolute/path/to/image-map.json" \
  --source yunxiao-mcp
```

### 4. Use browser fallback only when MCP cannot cover it

If the official MCP server cannot reproduce a UI-only filtered view, or if authentication and field parity are blocked, fall back to a temporary browser or Playwright workflow in the current task instead of reintroducing a permanent browser-first skill.

## Output Interpretation

The most useful fields for downstream fixing work are usually:

- `workitemCode`
- `subject`
- `status`
- `descriptionText`
- `descriptionImagePaths`
- `attachmentCount`
- `localBugMarkdownPath`

If the description is screenshot-only, `descriptionText` may be short or empty while `descriptionImagePaths` still contains useful evidence.

## Guardrails

- Prefer the official Yunxiao MCP path before any browser automation
- Prefer explicit project selection at call time; use config aliases only to reduce repeated typing
- Always keep outputs under a dated directory, not a flat folder
- Download signed screenshot URLs immediately after `get_workitem_file` returns them
- Preserve repo-local artifacts so later fixing work can reuse them directly
- When multiple projects match by name, inspect the returned project IDs and choose deliberately
- Do not reintroduce a permanent browser-first Projex harvesting skill unless MCP becomes impossible to use
