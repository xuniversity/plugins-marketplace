from __future__ import annotations

import json
import re
import shutil
from collections import defaultdict
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from typing import Any


def local_now() -> datetime:
    return datetime.now().astimezone()


def epoch_ms_to_iso(epoch_ms: int | None) -> str | None:
    if not epoch_ms:
        return None
    return datetime.fromtimestamp(epoch_ms / 1000, tz=timezone.utc).isoformat()


def normalize_run_date(run_date: str | None) -> str:
    return run_date or local_now().date().isoformat()


def build_run_paths(output_root: str | Path, run_date: str) -> dict[str, Path]:
    export_root = Path(output_root).resolve() / "yunxiao-bugs"
    run_dir = export_root / run_date
    return {
        "export_root": export_root,
        "run_dir": run_dir,
        "list_cache": run_dir / "yunxiao-bug-list-cache.json",
        "full_json": run_dir / "yunxiao-bugs-full.json",
        "summary_json": run_dir / "yunxiao-bugs-summary.json",
        "grouped_md": run_dir / "yunxiao-bugs-grouped.md",
        "readme_md": run_dir / "README.md",
        "run_meta_json": run_dir / "run-meta.json",
        "bugs_dir": run_dir / "bugs",
        "images_dir": run_dir / "yunxiao-bug-images",
        "latest_file": export_root / "LATEST",
    }


def clean_html_text(html: str | None) -> str:
    if not html:
        return ""
    text = re.sub(r"<br\s*/?>", "\n", html, flags=re.I)
    text = re.sub(r"</p\s*>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    text = unescape(text)
    text = text.replace("\ufeff", "").replace("\u200b", "")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = "\n".join(line.strip() for line in text.splitlines())
    text = "\n".join(line for line in text.splitlines() if line)
    return text.strip()


def iter_srcs(node: Any):
    if isinstance(node, dict):
        src = node.get("src")
        if isinstance(src, str):
            yield src
        for value in node.values():
            yield from iter_srcs(value)
    elif isinstance(node, list):
        for item in node:
            yield from iter_srcs(item)


def extract_document_payload(workitem_result: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    document = workitem_result.get("document") or {}
    raw_content = document.get("content")
    payload = {}
    if isinstance(raw_content, str) and raw_content.strip():
        try:
            payload = json.loads(raw_content)
        except json.JSONDecodeError:
            payload = {}
    return document, payload


def extract_image_urls(payload: dict[str, Any]) -> list[str]:
    image_urls: list[str] = []
    jsonml = payload.get("jsonMLValue") or []
    for src in iter_srcs(jsonml):
        if src not in image_urls:
            image_urls.append(src)

    if image_urls:
        return image_urls

    html_value = payload.get("htmlValue") or ""
    for match in re.findall(r'<img[^>]+src="([^"]+)"', html_value):
        if match not in image_urls:
            image_urls.append(match)
    return image_urls


def ensure_clean_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def markdown_escape(text: Any) -> str:
    return str(text or "").replace("|", "\\|").replace("\n", "<br>")


def compact_text(text: str | None, limit: int = 120) -> str:
    value = " ".join((text or "").split())
    if len(value) <= limit:
        return value
    return value[: limit - 3].rstrip() + "..."


def build_image_lookup(
    image_map: dict[str, dict[str, Any]] | None,
    image_urls: list[str],
) -> tuple[list[str], list[str | None]]:
    if not image_map:
        return [], []

    local_paths = []
    file_ids = []
    for url in image_urls:
        image_info = image_map.get(url) or {}
        if image_info.get("localPath"):
            local_paths.append(str(image_info["localPath"]))
            file_ids.append(image_info.get("fileId"))
    return local_paths, file_ids


def normalize_person_name(value: dict[str, Any] | None) -> str | None:
    if not value:
        return None
    return value.get("displayName") or value.get("name") or value.get("username") or value.get("userName")


def normalize_status_name(value: dict[str, Any] | None) -> str | None:
    if not value:
        return None
    return value.get("displayName") or value.get("name")


def derive_workitem_code(workitem_result: dict[str, Any]) -> tuple[str, Any]:
    serial_number = workitem_result.get("serialNumber")
    space = workitem_result.get("space") or {}
    custom_code = space.get("customCode") or "WORKITEM"

    if isinstance(serial_number, str):
        if re.fullmatch(r"[A-Za-z0-9_]+-\d+", serial_number):
            return serial_number, serial_number.rsplit("-", 1)[1]
        if serial_number.isdigit():
            return f"{custom_code}-{serial_number}", serial_number
        return serial_number, serial_number

    if isinstance(serial_number, (int, float)):
        normalized = int(serial_number)
        return f"{custom_code}-{normalized}", normalized

    identifier = workitem_result.get("id") or "unknown"
    return f"{custom_code}-{identifier}", identifier


def summarize_item(
    item: dict[str, Any],
    image_map: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    workitem_result = item["workitem"]["result"]
    attachments_result = item["attachments"].get("result") or []
    document, payload = extract_document_payload(workitem_result)
    html_value = payload.get("htmlValue")
    image_urls = extract_image_urls(payload)
    local_image_paths, file_ids = build_image_lookup(image_map, image_urls)
    workitem_code, serial_value = derive_workitem_code(workitem_result)
    description_text = clean_html_text(html_value)

    return {
        "id": item["id"],
        "serialNumber": serial_value,
        "rawSerialNumber": workitem_result.get("rawSerialNumber"),
        "workitemCode": workitem_code,
        "subject": workitem_result.get("subject"),
        "status": normalize_status_name(workitem_result.get("status")),
        "creator": normalize_person_name(workitem_result.get("creator")),
        "assignee": normalize_person_name(workitem_result.get("assignedTo")),
        "gmtCreate": workitem_result.get("gmtCreate"),
        "gmtCreateIso": epoch_ms_to_iso(workitem_result.get("gmtCreate")),
        "gmtModified": workitem_result.get("gmtModified"),
        "gmtModifiedIso": epoch_ms_to_iso(workitem_result.get("gmtModified")),
        "documentIdentifier": document.get("identifier"),
        "descriptionText": description_text,
        "descriptionHasText": bool(description_text),
        "descriptionImageCount": len(image_urls),
        "descriptionImageUrls": image_urls,
        "descriptionImageFileIds": file_ids,
        "descriptionImagePaths": local_image_paths,
        "attachmentCount": len(attachments_result),
        "attachments": attachments_result,
    }


def write_bug_markdown(bugs_dir: Path, item: dict[str, Any]) -> Path:
    code = item["workitemCode"] or f"WORKITEM-{item['id']}"
    path = bugs_dir / f"{code}-fix.md"
    attachments = item.get("attachments") or []
    image_paths = item.get("descriptionImagePaths") or []
    image_urls = item.get("descriptionImageUrls") or []
    description = item.get("descriptionText") or "无文本描述，仅截图或附件。"

    lines = [
        f"# {code} - {item.get('subject') or 'Untitled'}",
        "",
        "## 基本信息",
        "",
        f"- ID：`{item['id']}`",
        f"- 状态：{item.get('status') or '未知'}",
        f"- 创建人：{item.get('creator') or '未知'}",
        f"- 负责人：{item.get('assignee') or '未分配'}",
        f"- 创建时间：{item.get('gmtCreateIso') or '未知'}",
        f"- 最后修改：{item.get('gmtModifiedIso') or '未知'}",
        "",
        "## 描述",
        "",
        description,
        "",
    ]

    if image_paths or image_urls:
        lines.extend(
            [
                "## 描述截图",
                "",
            ]
        )
        for image_path in image_paths:
            lines.append(f"- [{Path(image_path).name}]({image_path})")
        for image_url in image_urls[len(image_paths) :]:
            lines.append(f"- 远程截图：{image_url}")
        lines.append("")

    if attachments:
        lines.extend(
            [
                "## 附件",
                "",
            ]
        )
        for attachment in attachments:
            name = (
                attachment.get("name")
                or attachment.get("fileName")
                or attachment.get("identifier")
                or "未命名附件"
            )
            identifier = attachment.get("identifier") or attachment.get("id") or "-"
            lines.append(f"- `{identifier}` {name}")
        lines.append("")

    path.write_text("\n".join(lines).rstrip() + "\n")
    return path.resolve()


def build_grouped_markdown(summary_items: list[dict[str, Any]], summary_json_path: Path) -> str:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in summary_items:
        groups[item.get("status") or "未标记状态"].append(item)

    lines = [
        "# Yunxiao Bugs Grouped",
        "",
        f"基于 `{summary_json_path}` 生成。",
        "",
        "## 状态分组",
        "",
    ]

    for status in sorted(groups.keys()):
        items = sorted(
            groups[status],
            key=lambda value: (value.get("gmtModified") or 0, str(value.get("serialNumber") or 0)),
            reverse=True,
        )
        lines.extend(
            [
                f"### {status}",
                "",
                "| 编号 | 标题 | 负责人 | 最后修改 | 详情 |",
                "| --- | --- | --- | --- | --- |",
            ]
        )
        for item in items:
            code = item.get("workitemCode") or f"WORKITEM-{item['id']}"
            detail_path = item.get("localBugMarkdownPath", "")
            detail_link = f"[查看]({detail_path})" if detail_path else "-"
            lines.append(
                "| "
                + " | ".join(
                    [
                        markdown_escape(code),
                        markdown_escape(item.get("subject") or ""),
                        markdown_escape(item.get("assignee") or "未分配"),
                        markdown_escape(item.get("gmtModifiedIso") or "未知"),
                        detail_link,
                    ]
                )
                + " |"
            )
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def build_readme(
    run_date: str,
    list_url: str,
    paths: dict[str, Path],
    summary_items: list[dict[str, Any]],
) -> str:
    status_counts: dict[str, int] = defaultdict(int)
    for item in summary_items:
        status_counts[item.get("status") or "未标记状态"] += 1

    lines = [
        f"# Yunxiao Bug Export - {run_date}",
        "",
        "## 本次导出",
        "",
        f"- 生成时间：{local_now().isoformat()}",
        f"- 列表引用：`{list_url}`",
        f"- 缺陷数量：{len(summary_items)}",
        "",
        "## 目录说明",
        "",
        f"- [yunxiao-bug-list-cache.json]({paths['list_cache']})：列表缓存原始数据",
        f"- [yunxiao-bugs-full.json]({paths['full_json']})：逐条详情原始数据",
        f"- [yunxiao-bugs-summary.json]({paths['summary_json']})：扁平化摘要，适合自动化消费",
        f"- [yunxiao-bugs-grouped.md]({paths['grouped_md']})：按状态汇总的人工阅读入口",
        f"- [bugs]({paths['bugs_dir']})：单条缺陷 Markdown",
        f"- [yunxiao-bug-images]({paths['images_dir']})：描述截图本地副本",
        "",
        "## 状态统计",
        "",
    ]

    for status in sorted(status_counts.keys()):
        lines.append(f"- {status}：{status_counts[status]}")

    lines.extend(
        [
            "",
            "## 缺陷列表",
            "",
            "| 编号 | 状态 | 标题 | 负责人 | 摘要 | 详情 |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )

    sorted_items = sorted(
        summary_items,
        key=lambda item: (item.get("gmtModified") or 0, str(item.get("serialNumber") or 0)),
        reverse=True,
    )
    for item in sorted_items:
        code = item.get("workitemCode") or f"WORKITEM-{item['id']}"
        detail_link = f"[查看]({item.get('localBugMarkdownPath', '')})"
        lines.append(
            "| "
            + " | ".join(
                [
                    markdown_escape(code),
                    markdown_escape(item.get("status") or "未标记状态"),
                    markdown_escape(item.get("subject") or ""),
                    markdown_escape(item.get("assignee") or "未分配"),
                    markdown_escape(
                        compact_text(item.get("descriptionText") or "无文本描述，仅截图或附件。")
                    ),
                    detail_link,
                ]
            )
            + " |"
        )

    lines.append("")
    return "\n".join(lines)


def materialize_run(
    *,
    output_dir: str | Path,
    run_date: str | None,
    list_url: str,
    list_data: list[dict[str, Any]],
    full_items: list[dict[str, Any]],
    image_map: dict[str, dict[str, Any]] | None = None,
    source: str,
) -> dict[str, Any]:
    resolved_run_date = normalize_run_date(run_date)
    paths = build_run_paths(output_dir, resolved_run_date)
    paths["run_dir"].mkdir(parents=True, exist_ok=True)
    ensure_clean_dir(paths["bugs_dir"])
    if image_map:
        paths["images_dir"].mkdir(parents=True, exist_ok=True)
    else:
        ensure_clean_dir(paths["images_dir"])

    paths["list_cache"].write_text(json.dumps(list_data, ensure_ascii=False, indent=2) + "\n")
    paths["full_json"].write_text(json.dumps(full_items, ensure_ascii=False, indent=2) + "\n")

    summary_items = [summarize_item(item, image_map=image_map) for item in full_items]
    for item in summary_items:
        item["localBugMarkdownPath"] = str(write_bug_markdown(paths["bugs_dir"], item))

    paths["summary_json"].write_text(json.dumps(summary_items, ensure_ascii=False, indent=2) + "\n")
    paths["grouped_md"].write_text(
        build_grouped_markdown(summary_items, paths["summary_json"])
    )
    paths["readme_md"].write_text(build_readme(resolved_run_date, list_url, paths, summary_items))
    paths["run_meta_json"].write_text(
        json.dumps(
            {
                "runDate": resolved_run_date,
                "generatedAt": local_now().isoformat(),
                "listUrl": list_url,
                "source": source,
                "count": len(summary_items),
                "runDirectory": str(paths["run_dir"]),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n"
    )
    paths["latest_file"].write_text(str(paths["run_dir"]) + "\n")

    return {
        "run_date": resolved_run_date,
        "paths": paths,
        "summary_items": summary_items,
    }
