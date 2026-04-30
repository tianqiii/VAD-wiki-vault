#!/usr/bin/env python3
"""以结构化方式更新 wiki/index.md 的导航层、完整注册表与规模统计。"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

REGISTRY_SECTIONS = ("Sources", "Entities", "Concepts", "Syntheses")
NAV_SECTIONS = ("快速入口", "按主题浏览")
VALID_ACTIONS = ("upsert", "remove")


@dataclass(frozen=True)
class IndexEntry:
    page: str
    description: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="更新 wiki/index.md 的注册表与导航层")
    parser.add_argument("--index-path", required=True, help="wiki/index.md 的路径")
    parser.add_argument("--section", required=True, choices=REGISTRY_SECTIONS, help="完整注册表目标分区")
    parser.add_argument("--page", required=True, help="页面名，不带 [[ ]]")
    parser.add_argument("--description", help="完整注册表条目描述；upsert 时必填")
    parser.add_argument("--action", default="upsert", choices=VALID_ACTIONS, help="默认 upsert")
    parser.add_argument(
        "--nav-section",
        action="append",
        default=[],
        choices=NAV_SECTIONS,
        help="可重复传入：同时维护导航层中的指定分区",
    )
    parser.add_argument(
        "--nav-description",
        help="导航层描述；缺省时沿用 --description",
    )
    return parser.parse_args()


def read_text(path: Path) -> str:
    if not path.exists():
        raise SystemExit(f"index 文件不存在: {path}")
    return path.read_text(encoding="utf-8")


def get_section_body(text: str, heading: str) -> str:
    pattern = rf"(?ms)^###{re.escape(' ' + heading)}\n(.*?)(?=^### |^## |\Z)"
    match = re.search(pattern, text)
    if not match:
        raise SystemExit(f"index.md 缺少三级分区: {heading}")
    return match.group(1)


def replace_section_body(text: str, heading: str, body: str) -> str:
    pattern = rf"(?ms)^(###{re.escape(' ' + heading)}\n)(.*?)(?=^### |^## |\Z)"
    if not re.search(pattern, text):
        raise SystemExit(f"index.md 缺少三级分区: {heading}")
    normalized = body.rstrip() + "\n\n"
    return re.sub(pattern, rf"\1{normalized}", text, count=1)


def get_nav_body(text: str, heading: str) -> str:
    pattern = rf"(?ms)^## {re.escape(heading)}\n(.*?)(?=^## |\Z)"
    match = re.search(pattern, text)
    if not match:
        raise SystemExit(f"index.md 缺少二级分区: {heading}")
    return match.group(1)


def replace_nav_body(text: str, heading: str, body: str) -> str:
    pattern = rf"(?ms)^(## {re.escape(heading)}\n)(.*?)(?=^## |\Z)"
    if not re.search(pattern, text):
        raise SystemExit(f"index.md 缺少二级分区: {heading}")
    normalized = body.rstrip() + "\n\n"
    return re.sub(pattern, rf"\1{normalized}", text, count=1)


ENTRY_PATTERN = re.compile(r"^- \[\[(?P<page>[^\]]+)\]\](?: — (?P<description>.*))?$")


def parse_entries(body: str) -> list[IndexEntry]:
    entries: list[IndexEntry] = []
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        match = ENTRY_PATTERN.match(line)
        if not match:
            continue
        entries.append(IndexEntry(page=match.group("page").strip(), description=(match.group("description") or "").strip()))
    return entries


def render_entries(entries: list[IndexEntry]) -> str:
    lines = [f"- [[{entry.page}]] — {entry.description}" for entry in entries]
    return "\n".join(lines)


def sort_entries(entries: list[IndexEntry]) -> list[IndexEntry]:
    return sorted(entries, key=lambda item: item.page.casefold())


def upsert_entry(entries: list[IndexEntry], page: str, description: str) -> list[IndexEntry]:
    updated: list[IndexEntry] = []
    replaced = False
    for entry in entries:
        if entry.page == page:
            updated.append(IndexEntry(page=page, description=description))
            replaced = True
            continue
        updated.append(entry)
    if not replaced:
        updated.append(IndexEntry(page=page, description=description))
    return sort_entries(updated)


def remove_entry(entries: list[IndexEntry], page: str) -> list[IndexEntry]:
    return [entry for entry in entries if entry.page != page]


def update_entries(entries: list[IndexEntry], action: str, page: str, description: str | None) -> list[IndexEntry]:
    if action == "remove":
        return remove_entry(entries, page)
    if not description:
        raise SystemExit("upsert 动作要求提供 --description")
    return upsert_entry(entries, page, description)


def replace_scale_stats(text: str) -> str:
    counts = {section: len(parse_entries(get_section_body(text, section))) for section in REGISTRY_SECTIONS}
    replacement = (
        "当前知识库规模：\n"
        f"- Sources：{counts['Sources']}\n"
        f"- Entities：{counts['Entities']}\n"
        f"- Concepts：{counts['Concepts']}\n"
        f"- Syntheses：{counts['Syntheses']}"
    )
    pattern = r"(?m)^当前知识库规模：\n(?:- [^\n]+\n){4}"
    if re.search(pattern, text):
        return re.sub(pattern, replacement + "\n", text, count=1)
    raise SystemExit("index.md 缺少顶部规模统计区块")


def update_index_text(
    text: str,
    *,
    section: str,
    page: str,
    description: str | None,
    action: str,
    nav_sections: list[str],
    nav_description: str | None,
) -> str:
    if "## 完整注册表" not in text:
        raise SystemExit("index.md 缺少 `## 完整注册表` 区块")

    registry_entries = parse_entries(get_section_body(text, section))
    updated_registry_entries = update_entries(registry_entries, action, page, description)
    text = replace_section_body(text, section, render_entries(updated_registry_entries))

    effective_nav_description = nav_description or description
    for nav_section in nav_sections:
        nav_entries = parse_entries(get_nav_body(text, nav_section))
        updated_nav_entries = update_entries(nav_entries, action, page, effective_nav_description)
        text = replace_nav_body(text, nav_section, render_entries(updated_nav_entries))

    return replace_scale_stats(text)


def update_index_file(
    index_path: Path,
    *,
    section: str,
    page: str,
    description: str | None,
    action: str = "upsert",
    nav_sections: list[str] | None = None,
    nav_description: str | None = None,
) -> bool:
    nav_sections = nav_sections or []
    original = read_text(index_path)
    updated = update_index_text(
        original,
        section=section,
        page=page.strip(),
        description=description.strip() if description else None,
        action=action,
        nav_sections=nav_sections,
        nav_description=nav_description.strip() if nav_description else None,
    )
    if updated == original:
        return False
    index_path.write_text(updated, encoding="utf-8")
    return True


def main() -> None:
    args = parse_args()
    changed = update_index_file(
        Path(args.index_path),
        section=args.section,
        page=args.page,
        description=args.description,
        action=args.action,
        nav_sections=args.nav_section,
        nav_description=args.nav_description,
    )
    message = "已更新 index" if changed else "index 无变化"
    print(f"{message}: {Path(args.index_path)}")


if __name__ == "__main__":
    main()
