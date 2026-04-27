#!/usr/bin/env python3
"""
Audit a project's Iconify setup and estimate whether it is build-time bundled,
self-hosted, mixed, or still dependent on public runtime API requests.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

TEXT_SUFFIXES = {
    ".astro",
    ".cjs",
    ".css",
    ".cts",
    ".html",
    ".js",
    ".json",
    ".jsx",
    ".mjs",
    ".mts",
    ".svelte",
    ".ts",
    ".tsx",
    ".vue",
    ".yaml",
    ".yml",
}

ICON_LITERAL_SCAN_SUFFIXES = {
    ".astro",
    ".cjs",
    ".cts",
    ".html",
    ".js",
    ".jsx",
    ".mjs",
    ".mts",
    ".svelte",
    ".ts",
    ".tsx",
    ".vue",
}

SKIP_DIRS = {
    ".git",
    ".idea",
    ".next",
    ".nuxt",
    ".output",
    ".turbo",
    ".vscode",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "target",
}

ICON_LITERAL_RE = re.compile(r"""['"](@?[a-z0-9-]+:[a-z0-9-]+(?::[a-z0-9-]+)?)['"]""")
ADD_ICON_PREFIX_RE = re.compile(r"""addIcon\(\s*[`'"]([a-z0-9-]+):""")
ADD_COLLECTION_PREFIX_RE = re.compile(
    r"""addCollection\((?:.|\n){0,400}?prefix\s*:\s*['"]([a-z0-9-]+)['"]""",
)
ADD_PROVIDER_RE = re.compile(
    r"""addAPIProvider\(\s*['"]([^'"]+)['"]\s*,\s*\{(?P<body>(?:.|\n){0,500}?)\}\s*\)""",
)
RESOURCE_RE = re.compile(r"""resources\s*:\s*\[(.*?)\]""", re.S)
QUOTED_STRING_RE = re.compile(r"""['"]([^'"]+)['"]""")
IGNORE_LITERAL_PREFIXES = {
    "about",
    "active",
    "after",
    "aria",
    "before",
    "data",
    "dark",
    "disabled",
    "even",
    "first",
    "focus",
    "group",
    "hover",
    "http",
    "https",
    "importmap",
    "last",
    "lg",
    "mailto",
    "md",
    "node",
    "odd",
    "peer",
    "sm",
    "tel",
    "update",
    "vite",
    "xl",
    "2xl",
}
IGNORE_NAME_PREFIXES = {
    "bg-",
    "border-",
    "col-span-",
    "grid-cols-",
    "max-w-",
    "shadow-",
    "text-",
    "underline",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit a project's Iconify setup for build/runtime/offline risk.",
    )
    parser.add_argument(
        "project_path",
        nargs="?",
        default=".",
        help="Project root to audit.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print JSON output.",
    )
    return parser.parse_args()


def is_text_file(path: Path) -> bool:
    return path.suffix in TEXT_SUFFIXES or path.name == "package.json"


def iter_text_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if not is_text_file(path):
            continue
        yield path


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None


def add_example(bucket: dict[str, list[str]], key: str, value: str, *, limit: int = 5) -> None:
    items = bucket[key]
    if value not in items and len(items) < limit:
        items.append(value)


def relative_line(path: Path, root: Path, text: str, position: int) -> str:
    line = text.count("\n", 0, position) + 1
    return f"{path.relative_to(root)}:{line}"


def parse_package_jsons(root: Path) -> tuple[set[str], list[str]]:
    dependencies: set[str] = set()
    files: list[str] = []
    for package_json in root.rglob("package.json"):
        if any(part in SKIP_DIRS for part in package_json.parts):
            continue
        content = read_text(package_json)
        if not content:
            continue
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            continue
        files.append(str(package_json.relative_to(root)))
        for key in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
            values = data.get(key) or {}
            if isinstance(values, dict):
                dependencies.update(values.keys())
    return dependencies, files


def looks_like_icon_literal(value: str) -> bool:
    if value.startswith("@"):
        _, _, rest = value.partition(":")
        if ":" not in rest:
            return False
        prefix, _, name = rest.partition(":")
    else:
        prefix, _, name = value.partition(":")

    if not prefix or not name:
        return False
    if prefix in IGNORE_LITERAL_PREFIXES:
        return False
    if any(name.startswith(item) for item in IGNORE_NAME_PREFIXES):
        return False
    if value.count(":") > 2:
        return False
    if not any(char.isalpha() for char in prefix):
        return False
    if not any(char.isalpha() for char in name):
        return False
    return True


def classify_provider_resources(resources: list[str]) -> str:
    if not resources:
        return "unknown"
    for resource in resources:
        value = resource.strip()
        if value.startswith("/") or value.startswith("./") or value.startswith("../"):
            return "same_origin"
        if value.startswith("http://localhost") or value.startswith("http://127.0.0.1"):
            return "local_dev"
        if value.startswith("https://api.iconify.design") or value.startswith("https://code.iconify.design"):
            return "public"
    return "external"


def audit_project(root: Path) -> dict[str, Any]:
    dependencies, package_json_files = parse_package_jsons(root)
    findings: dict[str, list[str]] = defaultdict(list)
    local_prefixes: set[str] = set()
    icon_literals: dict[str, list[str]] = defaultdict(list)
    provider_configs: dict[str, dict[str, Any]] = {}
    used_provider_names: set[str] = set()

    for path in iter_text_files(root):
        text = read_text(path)
        if not text:
            continue
        relative = path.relative_to(root)

        if "unplugin-icons" in text:
            add_example(findings, "unplugin_icons", str(relative))
        if "~icons/" in text:
            add_example(findings, "tilde_icons", str(relative))
        if "@iconify/vue" in text or "@iconify/react" in text or "@iconify/svelte" in text:
            add_example(findings, "runtime_icon_libraries", str(relative))
        if "@iconify/json" in text or "@iconify-json/" in text:
            add_example(findings, "local_icon_data_mentions", str(relative))
        if "api.iconify.design" in text or "code.iconify.design" in text:
            add_example(findings, "public_iconify_urls", str(relative))
        if "enableCache(" in text or "disableCache(" in text:
            add_example(findings, "browser_cache_api", str(relative))

        for match in ADD_ICON_PREFIX_RE.finditer(text):
            local_prefixes.add(match.group(1))
            add_example(findings, "local_registration", relative_line(path, root, text, match.start()))

        for match in ADD_COLLECTION_PREFIX_RE.finditer(text):
            local_prefixes.add(match.group(1))
            add_example(findings, "local_registration", relative_line(path, root, text, match.start()))

        for match in ADD_PROVIDER_RE.finditer(text):
            provider_name = match.group(1)
            body = match.group("body") or ""
            resources_match = RESOURCE_RE.search(body)
            resources: list[str] = []
            if resources_match:
                resources = QUOTED_STRING_RE.findall(resources_match.group(1))
            provider_configs[provider_name] = {
                "resources": resources,
                "resource_mode": classify_provider_resources(resources),
                "example": relative_line(path, root, text, match.start()),
            }
            add_example(findings, "custom_providers", relative_line(path, root, text, match.start()))

        if path.suffix in ICON_LITERAL_SCAN_SUFFIXES:
            for match in ICON_LITERAL_RE.finditer(text):
                raw_value = match.group(1)
                if not looks_like_icon_literal(raw_value):
                    continue
                icon_literals[raw_value].append(relative_line(path, root, text, match.start()))
                if raw_value.startswith("@"):
                    provider_name = raw_value.split(":", 1)[0][1:]
                    used_provider_names.add(provider_name)

    dependency_flags = {
        "unplugin_icons_dep": "unplugin-icons" in dependencies,
        "runtime_icon_dep": any(
            dep in dependencies
            for dep in ("@iconify/vue", "@iconify/react", "@iconify/svelte")
        ),
        "local_icon_data_dep": any(
            dep == "@iconify/json" or dep.startswith("@iconify-json/")
            for dep in dependencies
        ),
    }

    default_provider_icon_ids: dict[str, list[str]] = {}
    provider_prefixed_icon_ids: dict[str, list[str]] = {}
    for icon_name, locations in icon_literals.items():
        if icon_name.startswith("@"):
            provider_prefixed_icon_ids[icon_name] = locations
            continue
        prefix = icon_name.split(":", 1)[0]
        if prefix not in local_prefixes:
            default_provider_icon_ids[icon_name] = locations

    build_time_bundle = bool(
        dependency_flags["unplugin_icons_dep"]
        or findings["unplugin_icons"]
        or findings["tilde_icons"]
    )
    runtime_icon_usage = bool(
        dependency_flags["runtime_icon_dep"] or findings["runtime_icon_libraries"]
    )
    has_local_registration = bool(local_prefixes)
    has_same_origin_provider_in_use = any(
        provider_name in used_provider_names
        and provider_configs.get(provider_name, {}).get("resource_mode") in {"same_origin", "local_dev"}
        for provider_name in provider_configs
    )
    has_public_runtime_dependency = runtime_icon_usage and bool(default_provider_icon_ids)

    if build_time_bundle and has_public_runtime_dependency:
        verdict = "mixed_mode"
    elif build_time_bundle and not has_public_runtime_dependency:
        verdict = "build_time_bundle"
    elif has_same_origin_provider_in_use and not has_public_runtime_dependency:
        verdict = "safe_self_hosted_runtime"
    elif has_public_runtime_dependency:
        verdict = "public_runtime_dependency"
    else:
        verdict = "unknown"

    unused_providers = sorted(set(provider_configs) - used_provider_names)

    return {
        "project_path": str(root.resolve()),
        "package_json_files": package_json_files,
        "dependencies": {
            "has_unplugin_icons": dependency_flags["unplugin_icons_dep"],
            "has_runtime_icon_library": dependency_flags["runtime_icon_dep"],
            "has_local_icon_data_package": dependency_flags["local_icon_data_dep"],
        },
        "signals": {
            "build_time_bundle": build_time_bundle,
            "runtime_icon_usage": runtime_icon_usage,
            "local_registration": has_local_registration,
            "public_runtime_dependency": has_public_runtime_dependency,
            "same_origin_provider_in_use": has_same_origin_provider_in_use,
        },
        "verdict": verdict,
        "provider_configs": provider_configs,
        "used_provider_names": sorted(used_provider_names),
        "unused_provider_names": unused_providers,
        "local_prefixes": sorted(local_prefixes),
        "example_findings": findings,
        "default_provider_icon_ids": {
            key: value[:3] for key, value in sorted(default_provider_icon_ids.items())
        },
        "provider_prefixed_icon_ids": {
            key: value[:3] for key, value in sorted(provider_prefixed_icon_ids.items())
        },
    }


def print_report(report: dict[str, Any]) -> None:
    print(f"Project: {report['project_path']}")
    print(f"Verdict: {report['verdict']}")
    print()

    deps = report["dependencies"]
    signals = report["signals"]
    print("Summary:")
    print(f"- build-time bundling signals: {'yes' if signals['build_time_bundle'] else 'no'}")
    print(f"- runtime Iconify library usage: {'yes' if signals['runtime_icon_usage'] else 'no'}")
    print(f"- local icon data package: {'yes' if deps['has_local_icon_data_package'] else 'no'}")
    print(f"- local registration via addIcon/addCollection: {'yes' if signals['local_registration'] else 'no'}")
    print(f"- likely public runtime dependency: {'yes' if signals['public_runtime_dependency'] else 'no'}")
    print(f"- same-origin provider actively used: {'yes' if signals['same_origin_provider_in_use'] else 'no'}")
    print()

    if report["provider_configs"]:
        print("Providers:")
        for provider_name, config in sorted(report["provider_configs"].items()):
            resources = ", ".join(config.get("resources") or []) or "(none detected)"
            print(
                f"- {provider_name}: mode={config.get('resource_mode')} resources={resources} "
                f"example={config.get('example')}"
            )
        if report["unused_provider_names"]:
            print(f"- unused providers: {', '.join(report['unused_provider_names'])}")
        print()

    if report["local_prefixes"]:
        print(f"Local prefixes: {', '.join(report['local_prefixes'])}")
        print()

    if report["default_provider_icon_ids"]:
        print("Runtime icon IDs that likely still use the default provider:")
        for icon_name, locations in list(report["default_provider_icon_ids"].items())[:8]:
            print(f"- {icon_name}: {', '.join(locations)}")
        print()

    if report["provider_prefixed_icon_ids"]:
        print("Provider-prefixed icon IDs:")
        for icon_name, locations in list(report["provider_prefixed_icon_ids"].items())[:8]:
            print(f"- {icon_name}: {', '.join(locations)}")
        print()

    example_findings = report["example_findings"]
    for label, title in (
        ("unplugin_icons", "Build-time Iconify plugin evidence"),
        ("tilde_icons", "Bundled icon import evidence"),
        ("runtime_icon_libraries", "Runtime Iconify library evidence"),
        ("local_registration", "Local registration evidence"),
        ("browser_cache_api", "Browser cache API evidence"),
    ):
        examples = example_findings.get(label) or []
        if not examples:
            continue
        print(f"{title}:")
        for example in examples:
            print(f"- {example}")
        print()

    print("Interpretation:")
    if report["verdict"] == "build_time_bundle":
        print("- The project looks build-time bundled for the detected Iconify usage.")
    elif report["verdict"] == "safe_self_hosted_runtime":
        print("- The project appears to use a same-origin or local provider for runtime Iconify loading.")
    elif report["verdict"] == "mixed_mode":
        print(
            "- The project mixes bundled icons with runtime string-based Iconify usage. "
            "Static icons may be offline-safe, but some dynamic icons likely still need runtime API access."
        )
    elif report["verdict"] == "public_runtime_dependency":
        print(
            "- The project likely depends on runtime Iconify API access for at least some icons. "
            "This is risky for intranet or restricted deployments."
        )
    else:
        print("- The script could not classify the setup confidently. Inspect the evidence and code paths manually.")

    if example_findings.get("browser_cache_api"):
        print("- Do not rely on browser cache APIs as the deployment strategy.")


def main() -> int:
    args = parse_args()
    root = Path(args.project_path).resolve()
    if not root.exists():
        raise SystemExit(f"Path does not exist: {root}")
    report = audit_project(root)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_report(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
