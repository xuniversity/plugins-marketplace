#!/usr/bin/env python3
"""Initialize frontend design-system docs and shared component templates."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
TEMPLATES_ROOT = PLUGIN_ROOT / "assets" / "templates"
COMMON_ROOT = TEMPLATES_ROOT / "common"
IMPLEMENTATIONS_ROOT = TEMPLATES_ROOT / "implementations"
PLUGIN_SKILLS_ROOT = PLUGIN_ROOT / "skills"
PROJECT_SKILLS = (
    "frontend-design-system",
    "frontend-workflow-standards",
    "iconify-governance",
    "vben-component-rules",
)
TEMPLATE_COPY_IGNORE = shutil.ignore_patterns(
    ".DS_Store",
    ".git",
    ".turbo",
    "coverage",
    "dist",
    "node_modules",
    "output",
)
TEMPLATE_COPY_IGNORE_KEEP_GIT = shutil.ignore_patterns(
    ".DS_Store",
    ".turbo",
    "coverage",
    "dist",
    "node_modules",
    "output",
)


@dataclass
class CopyResult:
    copied: int = 0
    skipped: int = 0


def read_manifest_value(manifest: Path, key: str) -> str:
    if not manifest.exists():
        return ""
    prefix = f"{key}:"
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith(prefix):
            return line.split(":", 1)[1].strip().strip('"').strip("'")
    return ""


def read_implementation_metadata(manifest: Path) -> dict[str, object]:
    metadata: dict[str, object] = {
        "expectedAliases": [],
        "runtime": [],
        "versions": {},
    }
    if not manifest.exists():
        return metadata

    in_dependencies = False
    current_key = ""
    for raw_line in manifest.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line == "dependencies:":
            in_dependencies = True
            current_key = ""
            continue
        if not in_dependencies:
            continue
        if line.endswith(":") and not line.startswith("- "):
            current_key = line[:-1]
            continue
        if line.startswith("- ") and isinstance(metadata.get(current_key), list):
            metadata[current_key].append(line[2:].strip().strip("\"'"))
            continue
        if ":" in line and isinstance(metadata.get(current_key), dict):
            key, value = line.split(":", 1)
            metadata[current_key][key.strip().strip("\"'")] = value.strip().strip("\"'")
    return metadata


def list_implementations() -> None:
    for item in sorted(IMPLEMENTATIONS_ROOT.iterdir()):
        manifest = item / "implementation.yaml"
        if not item.is_dir() or not manifest.exists():
            continue
        display_name = read_manifest_value(manifest, "displayName") or item.name
        description = read_manifest_value(manifest, "description")
        suffix = f" - {description}" if description else ""
        print(f"{item.name}: {display_name}{suffix}")


def detect_src_root(target: Path) -> Path:
    candidates = [
        target / "apps" / "web-antd" / "src",
        target / "web-antd" / "src",
        target / "src",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return target / "src"


def is_git_source(source: str) -> bool:
    return (
        source.startswith("git@")
        or "://" in source
        or source.endswith(".git")
    )


def is_empty_dir(path: Path) -> bool:
    return not path.exists() or not any(path.iterdir())


def copy_base_template(
    source: str,
    target: Path,
    *,
    dry_run: bool,
    ref: str,
    keep_git: bool,
) -> None:
    if not source:
        return

    if not is_empty_dir(target):
        print(f"base template skipped: target is not empty: {target}")
        return

    if dry_run:
        print(f"base template: {source} -> {target}")
        return

    target.parent.mkdir(parents=True, exist_ok=True)

    if is_git_source(source):
        command = ["git", "clone", "--depth", "1"]
        if ref:
            command.extend(["--branch", ref])
        command.extend([source, str(target)])
        subprocess.run(command, check=True)
        if not keep_git:
            shutil.rmtree(target / ".git", ignore_errors=True)
        return

    source_path = Path(source).expanduser().resolve()
    if not source_path.exists():
        raise SystemExit(f"Base template not found: {source_path}")
    shutil.copytree(
        source_path,
        target,
        dirs_exist_ok=target.exists(),
        ignore=TEMPLATE_COPY_IGNORE_KEEP_GIT if keep_git else TEMPLATE_COPY_IGNORE,
    )
    if not keep_git:
        shutil.rmtree(target / ".git", ignore_errors=True)


def copy_tree(src: Path, dest: Path, *, dry_run: bool, force: bool) -> CopyResult:
    result = CopyResult()

    for source_file in sorted(src.rglob("*")):
        if source_file.is_dir():
            continue
        if source_file.suffix == ".pyc" or "__pycache__" in source_file.parts:
            continue

        relative_path = source_file.relative_to(src)
        target_file = dest / relative_path

        if target_file.exists() and not force:
            print(f"skip existing: {target_file}")
            result.skipped += 1
            continue

        action = "overwrite" if target_file.exists() else "copy"
        print(f"{action}: {source_file} -> {target_file}")
        result.copied += 1

        if dry_run:
            continue

        target_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_file, target_file)

    return result


def copy_project_skills(skills_root: Path, *, dry_run: bool, force: bool) -> CopyResult:
    result = CopyResult()

    for skill_name in PROJECT_SKILLS:
        skill_source = PLUGIN_SKILLS_ROOT / skill_name
        if not skill_source.exists():
            raise SystemExit(f"Project skill not found: {skill_source}")
        skill_result = copy_tree(
            skill_source,
            skills_root / skill_name,
            dry_run=dry_run,
            force=force,
        )
        result.copied += skill_result.copied
        result.skipped += skill_result.skipped

    return result


def ensure_codex_skills_bridge(
    *,
    agents_skills_dir: Path,
    codex_skills_dir: Path,
    dry_run: bool,
    force: bool,
) -> CopyResult:
    """Expose canonical .agents skills to Codex without duplicating when possible."""

    result = CopyResult()

    if codex_skills_dir.is_symlink():
        print(f"codex skills bridge: existing symlink {codex_skills_dir}")
        return result

    if codex_skills_dir.exists():
        print(f"codex skills bridge: mirror into existing directory {codex_skills_dir}")
        return copy_project_skills(codex_skills_dir, dry_run=dry_run, force=force)

    relative_target = os.path.relpath(
        agents_skills_dir,
        start=codex_skills_dir.parent,
    )
    print(f"codex skills bridge: {codex_skills_dir} -> {relative_target}")
    result.copied += 1

    if dry_run:
        return result

    codex_skills_dir.parent.mkdir(parents=True, exist_ok=True)
    try:
        codex_skills_dir.symlink_to(relative_target, target_is_directory=True)
        return result
    except OSError as error:
        print(f"codex skills bridge fallback: symlink failed ({error}); copying skills")
        return copy_project_skills(codex_skills_dir, dry_run=dry_run, force=force)


def find_package_root(target: Path, src_root: Path) -> Path:
    current = src_root.resolve()
    if current.is_file():
        current = current.parent
    while current != current.parent:
        if (current / "package.json").exists():
            return current
        if current == target:
            break
        current = current.parent
    return target


def load_package_json(package_root: Path) -> tuple[Path, dict[str, object] | None]:
    package_json = package_root / "package.json"
    if not package_json.exists():
        return package_json, None
    return package_json, json.loads(package_json.read_text(encoding="utf-8"))


def find_workspace_file(package_root: Path, target: Path) -> Path | None:
    current = package_root.resolve()
    target = target.resolve()
    while current != current.parent:
        workspace_file = current / "pnpm-workspace.yaml"
        if workspace_file.exists():
            return workspace_file
        if current == target:
            break
        current = current.parent
    return None


def package_uses_catalog(package_data: dict[str, object]) -> bool:
    for key in ("dependencies", "devDependencies", "peerDependencies"):
        value = package_data.get(key)
        if not isinstance(value, dict):
            continue
        if any(version == "catalog:" for version in value.values()):
            return True
    return False


def add_catalog_versions(
    workspace_file: Path,
    versions: dict[str, str],
    *,
    dry_run: bool,
) -> None:
    if not versions:
        return

    lines = workspace_file.read_text(encoding="utf-8").splitlines()
    catalog_start = next(
        (index for index, line in enumerate(lines) if line.strip() == "catalog:"),
        -1,
    )
    if catalog_start < 0:
        lines.append("catalog:")
        catalog_start = len(lines) - 1

    catalog_end = len(lines)
    for index in range(catalog_start + 1, len(lines)):
        line = lines[index]
        if line and not line.startswith((" ", "\t", "#")):
            catalog_end = index
            break

    existing: set[str] = set()
    for line in lines[catalog_start + 1 : catalog_end]:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        existing.add(stripped.split(":", 1)[0].strip().strip("\"'"))

    missing = {
        dependency: version
        for dependency, version in versions.items()
        if dependency not in existing
    }
    if not missing:
        return

    print(f"update pnpm catalog: {workspace_file}")
    for dependency, version in sorted(missing.items()):
        print(f"  - {dependency}: {version}")

    if dry_run:
        return

    insertion = [f"  {dependency}: {version}" for dependency, version in sorted(missing.items())]
    lines[catalog_end:catalog_end] = insertion
    workspace_file.write_text("\n".join(lines) + "\n", encoding="utf-8")


def report_dependencies(
    target: Path,
    package_root: Path,
    dependencies: list[str],
    versions: dict[str, str],
    *,
    dry_run: bool,
    update_package_json: bool,
) -> None:
    if not dependencies:
        return

    package_json, package_data = load_package_json(package_root)
    if package_data is None:
        print("")
        print("dependency check: package.json not found; install these runtime packages manually:")
        for dependency in dependencies:
            print(f"  - {dependency}")
        return

    existing: set[str] = set()
    for key in ("dependencies", "devDependencies", "peerDependencies"):
        value = package_data.get(key)
        if isinstance(value, dict):
            existing.update(value.keys())

    missing = [dependency for dependency in dependencies if dependency not in existing]
    if not missing:
        print("")
        print("dependency check: ok")
        return

    print("")
    print("dependency check: missing runtime dependencies:")
    for dependency in missing:
        print(f"  - {dependency}")

    if not update_package_json:
        print("Run with --update-package-json to add missing dependencies.")
        return

    package_data.setdefault("dependencies", {})
    dependencies_block = package_data["dependencies"]
    if not isinstance(dependencies_block, dict):
        raise SystemExit("package.json dependencies must be an object before it can be updated.")

    workspace_file = find_workspace_file(package_root, target)
    use_catalog = workspace_file is not None and package_uses_catalog(package_data)
    catalog_versions: dict[str, str] = {}
    for dependency in missing:
        version = versions.get(dependency, "latest")
        if use_catalog:
            dependencies_block[dependency] = "catalog:"
            catalog_versions[dependency] = version
        else:
            dependencies_block[dependency] = version

    print(f"update package.json: {package_json}")
    if not dry_run:
        package_json.write_text(
            json.dumps(package_data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    if workspace_file is not None:
        add_catalog_versions(workspace_file, catalog_versions, dry_run=dry_run)


def report_aliases(target: Path, package_root: Path, aliases: list[str]) -> None:
    if not aliases:
        return

    candidates = [
        package_root / "tsconfig.json",
        package_root / "tsconfig.app.json",
        package_root / "vite.config.ts",
        package_root / "vite.config.mts",
        package_root / "vite.config.js",
        target / "tsconfig.json",
        target / "tsconfig.app.json",
        target / "vite.config.ts",
        target / "vite.config.mts",
        target / "vite.config.js",
    ]
    haystack = "\n".join(
        candidate.read_text(encoding="utf-8", errors="ignore")
        for candidate in candidates
        if candidate.exists()
    )

    def has_alias(alias: str) -> bool:
        if alias in haystack:
            return True
        if alias.startswith("#/") and ("#/*" in haystack or '"#"' in haystack or "'#'" in haystack):
            return True
        return False

    missing = [alias for alias in aliases if not has_alias(alias)]
    print("")
    if not missing:
        print("alias check: ok")
        return

    print("alias check: review these expected aliases in tsconfig/vite config:")
    for alias in missing:
        print(f"  - {alias}")
    print("Typical Vben projects map #/ to the selected src root.")


def init_project(args: argparse.Namespace) -> None:
    target = Path(args.target).expanduser().resolve()
    copy_base_template(
        args.base_template,
        target,
        dry_run=args.dry_run,
        ref=args.base_template_ref,
        keep_git=args.keep_template_git,
    )
    docs_dir = (target / args.docs_dir).resolve()
    skills_dir = (target / args.skills_dir).resolve()
    codex_skills_dir = (target / args.codex_skills_dir).resolve()
    src_root = (
        Path(args.src_root).expanduser().resolve()
        if args.src_root
        else detect_src_root(target)
    )

    implementation_root = IMPLEMENTATIONS_ROOT / args.implementation
    implementation_manifest = implementation_root / "implementation.yaml"
    implementation_src = implementation_root / "src"

    if not implementation_src.exists():
        available = ", ".join(
            item.name
            for item in sorted(IMPLEMENTATIONS_ROOT.iterdir())
            if (item / "implementation.yaml").exists()
        )
        raise SystemExit(
            f"Unknown implementation '{args.implementation}'. Available: {available}",
        )

    print(f"target: {target}")
    print(f"docs:   {docs_dir}")
    print(f"src:    {src_root}")
    if args.include_skills:
        print(f"skills: {skills_dir}")
        if args.include_codex_skills:
            print(f"codex:  {codex_skills_dir}")
    print(f"impl:   {args.implementation}")
    if args.base_template:
        print(f"base:   {args.base_template}")
    package_root = find_package_root(target, src_root)
    print(f"pkg:    {package_root}")

    total = CopyResult()

    common_docs = COMMON_ROOT / "docs"
    if args.include_docs and common_docs.exists():
        docs_result = copy_tree(
            common_docs,
            docs_dir,
            dry_run=args.dry_run,
            force=args.force,
        )
        total.copied += docs_result.copied
        total.skipped += docs_result.skipped

    common_project = COMMON_ROOT / "project"
    if args.include_project_rules and common_project.exists():
        project_result = copy_tree(
            common_project,
            target,
            dry_run=args.dry_run,
            force=args.force,
        )
        total.copied += project_result.copied
        total.skipped += project_result.skipped

    if args.include_skills:
        skills_result = copy_project_skills(
            skills_dir,
            dry_run=args.dry_run,
            force=args.force,
        )
        total.copied += skills_result.copied
        total.skipped += skills_result.skipped

        if args.include_codex_skills:
            codex_result = ensure_codex_skills_bridge(
                agents_skills_dir=skills_dir,
                codex_skills_dir=codex_skills_dir,
                dry_run=args.dry_run,
                force=args.force,
            )
            total.copied += codex_result.copied
            total.skipped += codex_result.skipped

    if args.include_components:
        src_result = copy_tree(
            implementation_src,
            src_root,
            dry_run=args.dry_run,
            force=args.force,
        )
        total.copied += src_result.copied
        total.skipped += src_result.skipped

    implementation_metadata = read_implementation_metadata(implementation_manifest)
    runtime_dependencies = implementation_metadata["runtime"]
    expected_aliases = implementation_metadata["expectedAliases"]
    dependency_versions = implementation_metadata["versions"]
    if not isinstance(runtime_dependencies, list):
        raise SystemExit("implementation.yaml dependencies.runtime must be a list.")
    if not isinstance(expected_aliases, list):
        raise SystemExit("implementation.yaml dependencies.expectedAliases must be a list.")
    if not isinstance(dependency_versions, dict):
        raise SystemExit("implementation.yaml dependencies.versions must be an object.")
    report_dependencies(
        target,
        package_root,
        runtime_dependencies,
        dependency_versions,
        dry_run=args.dry_run,
        update_package_json=args.update_package_json,
    )
    report_aliases(target, package_root, expected_aliases)

    print("")
    print(f"done: copied={total.copied}, skipped={total.skipped}")
    if total.skipped and not args.force:
        print("Re-run with --force to overwrite existing files.")
    print("Next: wire API adapters, confirm aliases such as #/, and run the target project's formatter/typecheck.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Initialize frontend docs and shared components from this plugin.",
    )
    parser.add_argument(
        "--target",
        default=".",
        help="Target project root. Defaults to current directory.",
    )
    parser.add_argument(
        "--implementation",
        default="vben",
        help="Component implementation to install. Defaults to vben.",
    )
    parser.add_argument(
        "--base-template",
        default="",
        help="Optional git URL or local template directory to copy before applying plugin templates.",
    )
    parser.add_argument(
        "--base-template-ref",
        default="",
        help="Optional git branch or tag for --base-template when it is a git source.",
    )
    parser.add_argument(
        "--keep-template-git",
        action="store_true",
        help="Keep .git from the base template clone/copy. Defaults to removing it for a fresh project.",
    )
    parser.add_argument(
        "--src-root",
        default="",
        help="Target source root. Defaults to apps/web-antd/src when present, otherwise src.",
    )
    parser.add_argument(
        "--docs-dir",
        default="docs",
        help="Docs directory relative to target root. Defaults to docs.",
    )
    parser.add_argument(
        "--skills-dir",
        "--agents-skills-dir",
        default=".agents/skills",
        help="Canonical project skills directory relative to target root. Defaults to .agents/skills.",
    )
    parser.add_argument(
        "--codex-skills-dir",
        default=".codex/skills",
        help="Codex compatibility skills path relative to target root. Defaults to .codex/skills.",
    )
    parser.add_argument(
        "--skip-docs",
        action="store_false",
        dest="include_docs",
        help="Do not copy design-system and standards docs.",
    )
    parser.add_argument(
        "--skip-project-rules",
        action="store_false",
        dest="include_project_rules",
        help="Do not copy root project AI instructions such as AGENTS.md.",
    )
    parser.add_argument(
        "--skip-skills",
        action="store_false",
        dest="include_skills",
        help="Do not copy project-level skills into the target project.",
    )
    parser.add_argument(
        "--skip-codex-skills",
        action="store_false",
        dest="include_codex_skills",
        help="Do not expose project skills through .codex/skills.",
    )
    parser.add_argument(
        "--skip-components",
        action="store_false",
        dest="include_components",
        help="Do not copy component implementation templates.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files.",
    )
    parser.add_argument(
        "--update-package-json",
        action="store_true",
        help="Add missing implementation runtime dependencies to package.json, preserving pnpm catalog style when detected.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned copies without writing files.",
    )
    parser.add_argument(
        "--list-implementations",
        action="store_true",
        help="List available component implementations and exit.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.list_implementations:
        list_implementations()
        return

    init_project(args)


if __name__ == "__main__":
    main()
