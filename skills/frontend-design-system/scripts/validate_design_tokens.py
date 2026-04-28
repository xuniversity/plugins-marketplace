#!/usr/bin/env python3
"""Validate design-tokens.yaml against design-tokens.schema.json."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate docs/design-system/design-tokens.yaml against its JSON schema.",
    )
    parser.add_argument(
        "project_path",
        nargs="?",
        default=".",
        help="Project root to validate. Defaults to the current directory.",
    )
    parser.add_argument(
        "--tokens",
        default="docs/design-system/design-tokens.yaml",
        help="Path to design-tokens.yaml, relative to project root unless absolute.",
    )
    parser.add_argument(
        "--schema",
        default="docs/design-system/design-tokens.schema.json",
        help="Path to design-tokens.schema.json, relative to project root unless absolute.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Validate the main token file plus tenant override YAML files when present.",
    )
    return parser.parse_args()


def resolve_path(root: Path, value: str) -> Path:
    path = Path(value).expanduser()
    return path if path.is_absolute() else root / path


def display_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def collect_token_files(root: Path, tokens_path: Path, validate_all: bool) -> list[Path]:
    files = [tokens_path]
    if not validate_all:
        return files

    overrides_root = root / "docs" / "design-system" / "tenant-overrides"
    if overrides_root.exists():
        files.extend(sorted(overrides_root.rglob("*.yaml")))
        files.extend(sorted(overrides_root.rglob("*.yml")))

    seen: set[Path] = set()
    unique_files: list[Path] = []
    for path in files:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        unique_files.append(path)
    return unique_files


def load_dependencies():
    try:
        import yaml  # type: ignore[import-not-found]
        from jsonschema import Draft202012Validator  # type: ignore[import-not-found]
    except ImportError as error:
        print(
            "design-token schema validation requires Python packages: pyyaml jsonschema",
            file=sys.stderr,
        )
        print("Install them in your validation environment, then rerun this script.", file=sys.stderr)
        raise SystemExit(2) from error
    return yaml, Draft202012Validator


def main() -> int:
    args = parse_args()
    root = Path(args.project_path).expanduser().resolve()
    tokens_path = resolve_path(root, args.tokens)
    schema_path = resolve_path(root, args.schema)

    if not tokens_path.exists():
        print(f"design-token schema validation: missing tokens file: {tokens_path}", file=sys.stderr)
        return 2
    if not schema_path.exists():
        print(f"design-token schema validation: missing schema file: {schema_path}", file=sys.stderr)
        return 2

    yaml, validator_class = load_dependencies()
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = validator_class(schema)
    token_files = collect_token_files(root, tokens_path, args.all)
    all_errors: list[tuple[Path, object]] = []

    for token_file in token_files:
        if not token_file.exists():
            print(f"design-token schema validation: missing tokens file: {token_file}", file=sys.stderr)
            return 2
        data = yaml.safe_load(token_file.read_text(encoding="utf-8"))
        errors = sorted(
            validator.iter_errors(data),
            key=lambda error: list(error.path),
        )
        all_errors.extend((token_file, error) for error in errors)

    if not all_errors:
        if len(token_files) == 1:
            print(f"design-token schema validation: ok ({display_path(tokens_path, root)})")
        else:
            print(f"design-token schema validation: ok ({len(token_files)} files)")
        return 0

    print(f"design-token schema validation: failed ({len(all_errors)} errors)")
    for token_file, error in all_errors:
        path = ".".join(str(part) for part in error.path) or "<root>"
        print(f"- {display_path(token_file, root)}:{path}: {error.message}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
