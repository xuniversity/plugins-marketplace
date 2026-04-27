#!/usr/bin/env python3
"""
Search Iconify icons from the official search API and print suggestions that are
easy to copy into either runtime Iconify usage or unplugin-icons imports.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

API_URL = "https://api.iconify.design/search"
DEFAULT_PREFIXES = "heroicons,mdi,fluent,ph,tabler,carbon,solar"
FALLBACK_TERMS = {
    "account": ["user", "profile", "person"],
    "alert": ["warning", "alarm", "attention"],
    "academic": ["school", "education", "graduation"],
    "calendar": ["date", "schedule", "event"],
    "chat": ["message", "conversation", "comment"],
    "dashboard": ["chart", "grid", "workspace"],
    "download": ["export", "arrow-down", "tray"],
    "employment": ["career", "briefcase", "job"],
    "profile": ["user", "person", "account"],
    "report": ["document", "file", "chart"],
    "search": ["find", "magnify", "lookup"],
    "settings": ["gear", "cog", "preferences"],
    "student": ["academic", "school", "user", "person"],
    "upload": ["import", "arrow-up", "cloud"],
    "warning": ["alert", "alarm", "attention"],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Search for suitable Iconify icons via the official API.",
    )
    parser.add_argument("query", help="Search query, preferably a short English phrase.")
    parser.add_argument(
        "--prefixes",
        default=DEFAULT_PREFIXES,
        help=(
            "Comma-separated collection prefixes to prefer. "
            "Use an empty string to search all collections."
        ),
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=8,
        help="How many results to display locally. The API itself returns at least 32.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print raw JSON output for scripting.",
    )
    return parser.parse_args()


def fetch_results(query: str, prefixes: str, limit: int) -> dict[str, Any]:
    request_limit = max(32, limit)
    params = {
        "query": query,
        "limit": str(request_limit),
    }
    if prefixes.strip():
        params["prefixes"] = prefixes
    url = f"{API_URL}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "codex-iconify-skill/1.0",
        },
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def build_query_plan(query: str) -> list[str]:
    normalized = query.strip().lower()
    tokens = [token for token in normalized.split() if token]
    plan: list[str] = [normalized]

    for token in tokens:
        if token not in plan:
            plan.append(token)
        for fallback in FALLBACK_TERMS.get(token, []):
            if fallback not in plan:
                plan.append(fallback)

    return plan[:8]


def format_collection_name(item: dict[str, Any]) -> str:
    for key in ("name", "title"):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "Unknown collection"


def main() -> int:
    args = parse_args()
    try:
        payload = {"icons": [], "collections": {}}
        fallback_notes: list[str] = []
        seen_icons: set[str] = set()
        query_plan = build_query_plan(args.query)
        prefix_plan = [args.prefixes]
        if args.prefixes.strip():
            prefix_plan.append("")

        for query_text in query_plan:
            for prefixes in prefix_plan:
                partial = fetch_results(query_text, prefixes, args.limit)
                icons = partial.get("icons") or []
                collections = partial.get("collections") or {}
                if icons:
                    if query_text != args.query.strip().lower():
                        fallback_notes.append(f"query='{query_text}'")
                    if not prefixes.strip():
                        fallback_notes.append("all-collections")
                for icon_name in icons:
                    if icon_name in seen_icons:
                        continue
                    seen_icons.add(icon_name)
                    payload["icons"].append(icon_name)
                payload["collections"].update(collections)
                if len(payload["icons"]) >= max(32, args.limit):
                    break
            if len(payload["icons"]) >= max(32, args.limit):
                break
    except urllib.error.HTTPError as exc:
        print(f"Iconify search failed: HTTP {exc.code}", file=sys.stderr)
        return 1
    except urllib.error.URLError as exc:
        print(f"Iconify search failed: {exc.reason}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    icons = payload.get("icons") or []
    collections = payload.get("collections") or {}
    shown = icons[: max(0, args.limit)]

    print(f"Query: {args.query}")
    if args.prefixes.strip():
        print(f"Preferred collections: {args.prefixes}")
    else:
        print("Preferred collections: all")
    if fallback_notes:
        fallback_text = ", ".join(dict.fromkeys(fallback_notes))
        print(f"Fallbacks used: {fallback_text}")
    print(f"Results shown: {len(shown)} / {len(icons)}")
    print()

    if not shown:
        print("No results found.")
        return 0

    for index, icon_name in enumerate(shown, start=1):
        if ":" not in icon_name:
            continue
        prefix, icon = icon_name.split(":", 1)
        collection_meta = collections.get(prefix, {})
        collection_name = format_collection_name(collection_meta)
        print(f"{index}. {icon_name}  [{collection_name}]")
        print(f"   unplugin-icons: ~icons/{prefix}/{icon}")
        print(f"   runtime id:     {icon_name}")
        print(f"   helper call:    createIconifyIcon('{icon_name}')")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
