#!/usr/bin/env python3
"""
Generate a project-specific Iconify refactor template.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from audit_iconify_setup import audit_project, read_text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a tailored Iconify project refactor template.",
    )
    parser.add_argument(
        "--project-path",
        default=".",
        help="Project path used for audit-driven template generation.",
    )
    parser.add_argument(
        "--framework",
        choices=["auto", "vue", "react", "generic"],
        default="auto",
        help="Framework override. Defaults to auto detection.",
    )
    parser.add_argument(
        "--mode",
        choices=["auto", "build_time_bundle", "mixed_mode", "public_runtime_dependency", "safe_self_hosted_runtime", "unknown"],
        default="auto",
        help="Template mode override. Defaults to the audit verdict.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print JSON output.",
    )
    return parser.parse_args()


def detect_framework(root: Path) -> str:
    package_json = root / "package.json"
    if package_json.exists():
        content = read_text(package_json) or ""
        if '"vue"' in content or "'vue'" in content:
            return "vue"
        if '"react"' in content or "'react'" in content:
            return "react"

    if any(root.rglob("*.vue")):
        return "vue"
    if any(root.rglob("*.tsx")):
        return "react"
    return "generic"


def framework_files(framework: str) -> dict[str, str]:
    if framework == "vue":
        return {
            "barrel": "src/icons/index.ts",
            "resolver": "src/icons/resolve-icon.ts",
            "wrapper": "src/components/AppIcon.vue",
        }
    if framework == "react":
        return {
            "barrel": "src/icons/index.ts",
            "resolver": "src/icons/resolve-icon.tsx",
            "wrapper": "src/components/AppIcon.tsx",
        }
    return {
        "barrel": "src/icons/index.ts",
        "resolver": "src/icons/resolve-icon.ts",
        "wrapper": "src/components/AppIcon.ts",
    }


def build_steps(mode: str) -> list[str]:
    if mode == "build_time_bundle":
        return [
            "Create or normalize one fixed-icon barrel and route all static UI imports through it.",
            "Keep persisted icon values in config/API/DB as raw Iconify IDs such as `mdi:account`.",
            "Add one shared dynamic resolver only for runtime string-based icons.",
            "If intranet deployment matters for dynamic icons, add local registration or a controlled local subset.",
        ]
    if mode == "public_runtime_dependency":
        return [
            "Keep persisted values as raw Iconify IDs and stop introducing new local alias strings in API or DB records.",
            "Add one shared resolver and one wrapper component so runtime icon rendering is centralized.",
            "Replace feature-local direct Iconify runtime calls with the shared wrapper.",
            "Choose one offline-safe end state: local registration, a truly used same-origin provider, or a controlled local icon map.",
        ]
    if mode == "safe_self_hosted_runtime":
        return [
            "Keep persisted values as raw provider-prefixed or canonical icon IDs according to the app standard.",
            "Centralize runtime icon rendering behind one wrapper and one resolver.",
            "Verify that the same-origin provider is actually referenced by the icon names used in code and data.",
            "Add a fallback icon path so provider misses do not break rendering.",
        ]
    if mode == "mixed_mode":
        return [
            "Preserve the existing static barrel for fixed UI icons.",
            "Add or normalize one shared dynamic resolver for raw Iconify ID strings.",
            "Inventory every string icon source and standardize new values on raw Iconify IDs.",
            "Separate what should stay bundled from what must remain dynamic, then remove silent public provider dependence where needed.",
        ]
    return [
        "Audit current usage and classify static versus dynamic icon paths.",
        "Create one icon barrel, one dynamic resolver, and one wrapper component.",
        "Standardize persisted values on raw Iconify IDs.",
        "Re-audit after the rollout and verify offline posture.",
    ]


def build_template(root: Path, framework: str, mode: str, report: dict[str, Any]) -> dict[str, Any]:
    files = framework_files(framework)
    likely_string_sources = sorted(report.get("default_provider_icon_ids", {}).keys())[:8]
    providers = report.get("provider_configs", {})

    markdown = f"""# Iconify refactor template

## Project

- path: `{root}`
- framework: `{framework}`
- mode: `{mode}`
- current verdict: `{report.get('verdict')}`

## Canonical rules

- fixed UI icons come from `{files['barrel']}`
- dynamic icons are resolved by `{files['resolver']}`
- UI rendering goes through `{files['wrapper']}`
- persisted icon values use raw Iconify IDs such as `mdi:account`

## Recommended files

- `{files['barrel']}`
- `{files['resolver']}`
- `{files['wrapper']}`
- optional: `src/icons/local-collection.ts`
- optional: `src/icons/provider.ts`

## Rollout steps

""" + "\n".join(f"{index}. {step}" for index, step in enumerate(build_steps(mode), start=1)) + f"""

## Project-specific notes

- local prefixes registered now: `{", ".join(report.get('local_prefixes') or ['(none)'])}`
- provider configs detected: `{", ".join(sorted(providers)) or '(none)'}`
- unused providers: `{", ".join(report.get('unused_provider_names') or ['(none)'])}`

## Sample resolver skeleton

```ts
const iconCache = new Map<string, any>();

export function resolveIconifyIcon(iconName?: string) {{
  const normalized = iconName?.trim();
  if (!normalized) {{
    return null;
  }}
  if (!iconCache.has(normalized)) {{
    try {{
      iconCache.set(normalized, createIconifyIcon(normalized));
    }} catch {{
      iconCache.set(normalized, null);
    }}
  }}
  return iconCache.get(normalized);
}}
```

## Sample wrapper contract

- accepts `icon?: string | Component`
- resolves string values through the shared resolver
- uses a shared fallback icon when resolution fails

## Dynamic icon sources to inspect first

""" + (
        "\n".join(f"- `{item}`" for item in likely_string_sources)
        if likely_string_sources
        else "- none detected by the audit"
    ) + """
"""

    return {
        "project_path": str(root),
        "framework": framework,
        "mode": mode,
        "current_verdict": report.get("verdict"),
        "recommended_files": files,
        "steps": build_steps(mode),
        "markdown": markdown,
    }


def main() -> int:
    args = parse_args()
    root = Path(args.project_path).resolve()
    report = audit_project(root)
    framework = detect_framework(root) if args.framework == "auto" else args.framework
    mode = report["verdict"] if args.mode == "auto" else args.mode
    template = build_template(root, framework, mode, report)

    if args.json:
        print(json.dumps(template, ensure_ascii=False, indent=2))
    else:
        print(template["markdown"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
