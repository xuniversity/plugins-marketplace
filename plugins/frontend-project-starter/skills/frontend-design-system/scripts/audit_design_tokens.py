#!/usr/bin/env python3
"""Audit frontend files for design-token drift."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


RUNTIME_SUFFIXES = {
    ".astro",
    ".css",
    ".js",
    ".jsx",
    ".less",
    ".mjs",
    ".mts",
    ".pcss",
    ".postcss",
    ".sass",
    ".scss",
    ".svelte",
    ".ts",
    ".tsx",
    ".vue",
}

SKIP_DIRS = {
    ".agents",
    ".cache",
    ".claude",
    ".codex",
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
    "docs",
    "node_modules",
    "output",
    "public",
    "target",
}

IGNORE_MARKERS = (
    "design-token-audit: ignore",
    "design-token-ignore",
    "token-audit: ignore",
)

HEX_COLOR_RE = re.compile(
    r"(?<![\w#])#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})(?![\w-])",
)
COLOR_FUNCTION_RE = re.compile(r"(?<![\w-])(?:rgb|rgba|hsl|hsla)\(\s*(?!var\()", re.I)
TAILWIND_NAMED_COLOR_RE = re.compile(
    r"\b(?:bg|text|border|ring|divide|outline|decoration|placeholder|from|via|to|shadow)"
    r"-(?:white|black)(?:/[0-9]+)?\b",
    re.I,
)
CSS_NAMED_COLOR_RE = re.compile(
    r"(?:^|[;{,]\s*)"
    r"(?:color|background(?:-color)?|border(?:-color)?|fill|stroke|outline-color|"
    r"box-shadow|caret-color|accent-color)"
    r"\s*:\s*['\"]?(?:white|black)\b",
    re.I,
)
CUSTOM_PROP_NAMED_COLOR_RE = re.compile(r"\B--[\w-]+\s*:\s*(?:white|black)\b", re.I)
COLOR_ATTR_RE = re.compile(
    r"\b(?:color|background|background-color|fill|stroke|border-color)=['\"](?:white|black)['\"]",
    re.I,
)
CSS_RADIUS_RE = re.compile(
    r"\bborder(?:-(?:top|right|bottom|left|start|end))?"
    r"(?:-(?:left|right|start|end))?-radius\s*:\s*[^;{}]*\b\d+(?:\.\d+)?px\b",
    re.I,
)
JS_RADIUS_RE = re.compile(
    r"\bborder(?:TopLeft|TopRight|BottomLeft|BottomRight)?Radius\b"
    r"\s*[:=]\s*['\"]?\d+(?:\.\d+)?px\b",
    re.I,
)
TAILWIND_RADIUS_RE = re.compile(
    r"\brounded(?:-[trblsexy]|-(?:tl|tr|bl|br|ss|se|ee|es))?-\[\d+(?:\.\d+)?px\]",
)
PX_VALUE_RE = re.compile(r"\b(\d+(?:\.\d+)?)px\b")


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    rule: str
    value: str
    message: str


@dataclass(frozen=True)
class Rule:
    name: str
    pattern: re.Pattern[str]
    message: str


RULES = (
    Rule(
        "hardcoded-color",
        HEX_COLOR_RE,
        "Replace raw hex colors with runtime tokens or a documented scoped brand token.",
    ),
    Rule(
        "hardcoded-color-function",
        COLOR_FUNCTION_RE,
        "Use hsl(var(--token)) or another runtime token expression instead of literal color functions.",
    ),
    Rule(
        "named-color",
        TAILWIND_NAMED_COLOR_RE,
        "Replace Tailwind white/black utilities with semantic surface, text, or border tokens.",
    ),
    Rule(
        "named-color",
        CSS_NAMED_COLOR_RE,
        "Replace named white/black UI colors with semantic runtime tokens.",
    ),
    Rule(
        "named-color",
        CUSTOM_PROP_NAMED_COLOR_RE,
        "Map local CSS variables to runtime tokens instead of named white/black values.",
    ),
    Rule(
        "named-color",
        COLOR_ATTR_RE,
        "Pass token expressions or approved semantic colors instead of named white/black props.",
    ),
    Rule(
        "fixed-px-radius",
        CSS_RADIUS_RE,
        "Use --radius, derived radius variables, or semantic radius utilities instead of fixed px radii.",
    ),
    Rule(
        "fixed-px-radius",
        JS_RADIUS_RE,
        "Use --radius, derived radius variables, or semantic radius utilities instead of fixed px radii.",
    ),
    Rule(
        "fixed-px-radius",
        TAILWIND_RADIUS_RE,
        "Use semantic rounded utilities or token-backed arbitrary values instead of fixed px radii.",
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit Vue/CSS/TSX runtime files for design-token drift.",
    )
    parser.add_argument(
        "project_path",
        nargs="?",
        default=".",
        help="Project root to audit. Defaults to the current directory.",
    )
    parser.add_argument(
        "--paths",
        nargs="*",
        default=[],
        help="Optional files or directories to scan, relative to the project root when not absolute.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON output.",
    )
    parser.add_argument(
        "--max-findings",
        type=int,
        default=80,
        help="Maximum findings to print in text mode. Defaults to 80.",
    )
    return parser.parse_args()


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None


def relative_parts(path: Path, root: Path) -> tuple[str, ...]:
    try:
        return path.resolve().relative_to(root.resolve()).parts
    except ValueError:
        return path.parts


def should_skip(path: Path, root: Path) -> bool:
    parts = relative_parts(path, root)
    if any(part in SKIP_DIRS for part in parts):
        return True
    if path.name.endswith(".d.ts"):
        return True
    if path.name.endswith((".generated.ts", ".generated.tsx", ".generated.js")):
        return True
    return False


def is_runtime_file(path: Path) -> bool:
    return path.suffix in RUNTIME_SUFFIXES


def iter_files_in_dir(path: Path, root: Path) -> Iterable[Path]:
    for item in path.rglob("*"):
        if not item.is_file():
            continue
        if should_skip(item, root):
            continue
        if is_runtime_file(item):
            yield item


def default_scan_roots(root: Path) -> list[Path]:
    candidates: list[Path] = []
    for relative in ("src", "app", "pages", "components"):
        candidate = root / relative
        if candidate.exists():
            candidates.append(candidate)
    for pattern in ("apps/*/src", "packages/*/src"):
        candidates.extend(path for path in root.glob(pattern) if path.exists())
    if candidates:
        return sorted(set(candidates))
    return [root]


def resolve_scan_paths(root: Path, paths: list[str]) -> list[Path]:
    if paths:
        resolved = []
        for value in paths:
            path = Path(value).expanduser()
            resolved.append(path if path.is_absolute() else root / path)
        return resolved
    return default_scan_roots(root)


def iter_scan_files(root: Path, paths: list[str]) -> list[Path]:
    files: set[Path] = set()
    for path in resolve_scan_paths(root, paths):
        if not path.exists() or should_skip(path, root):
            continue
        if path.is_file():
            if is_runtime_file(path):
                files.add(path.resolve())
            continue
        files.update(item.resolve() for item in iter_files_in_dir(path, root))
    return sorted(files)


def has_ignore_marker(lines: list[str], index: int) -> bool:
    current = lines[index]
    previous = lines[index - 1] if index > 0 else ""
    return any(marker in current or marker in previous for marker in IGNORE_MARKERS)


def is_comment_only(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith(("//", "/*", "*", "<!--"))


def should_ignore_match(rule_name: str, value: str) -> bool:
    if rule_name != "fixed-px-radius":
        return False
    normalized = value.lower().replace(" ", "")
    if "var(--radius" in normalized:
        return True
    px_values = [float(match.group(1)) for match in PX_VALUE_RE.finditer(value)]
    return bool(px_values) and all(item >= 999 for item in px_values)


def relative_path(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)


def scan_file(path: Path, root: Path) -> list[Finding]:
    text = read_text(path)
    if text is None:
        return []

    findings: list[Finding] = []
    lines = text.splitlines()
    display_path = relative_path(path, root)

    for index, line in enumerate(lines):
        if has_ignore_marker(lines, index) or is_comment_only(line):
            continue
        for rule in RULES:
            for match in rule.pattern.finditer(line):
                value = match.group(0).strip()
                if should_ignore_match(rule.name, value):
                    continue
                findings.append(
                    Finding(
                        path=display_path,
                        line=index + 1,
                        rule=rule.name,
                        value=value,
                        message=rule.message,
                    ),
                )

    return findings


def audit_project(root: Path, paths: list[str]) -> dict[str, object]:
    files = iter_scan_files(root, paths)
    findings: list[Finding] = []
    for path in files:
        findings.extend(scan_file(path, root))

    return {
        "root": str(root),
        "filesScanned": len(files),
        "findingCount": len(findings),
        "findings": [asdict(finding) for finding in findings],
    }


def print_text_report(report: dict[str, object], *, max_findings: int) -> None:
    count = int(report["findingCount"])
    files_scanned = int(report["filesScanned"])

    if count == 0:
        print(f"design-token audit: ok ({files_scanned} files scanned)")
        return

    print(f"design-token audit: failed ({count} findings across {files_scanned} files scanned)")
    findings = report["findings"]
    if not isinstance(findings, list):
        return

    for item in findings[:max_findings]:
        if not isinstance(item, dict):
            continue
        print(
            f"- {item['path']}:{item['line']} [{item['rule']}] {item['value']} - {item['message']}",
        )

    remaining = count - max_findings
    if remaining > 0:
        print(f"... {remaining} more findings hidden; rerun with --json or a higher --max-findings.")

    print("")
    print("Allowed exceptions must carry a nearby comment such as:")
    print("  /* design-token-audit: ignore -- official brand asset color */")


def main() -> int:
    args = parse_args()
    root = Path(args.project_path).expanduser().resolve()
    report = audit_project(root, args.paths)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_text_report(report, max_findings=args.max_findings)

    return 1 if int(report["findingCount"]) else 0


if __name__ == "__main__":
    sys.exit(main())
