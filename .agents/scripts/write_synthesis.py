#!/usr/bin/env python3
"""将高价值回答固化为 wiki/syntheses 页面，并同步 index/log。"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from write_index import update_index_file
from write_log import append_entry, build_entry, parse_detail


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="写入 synthesis 页面并同步 index/log")
    parser.add_argument("--workspace-root", required=True, help="仓库根目录")
    parser.add_argument("--slug", required=True, help="synthesis 文件名（kebab-case，无 .md）")
    parser.add_argument("--title", help="frontmatter title；默认沿用 slug")
    parser.add_argument("--summary", required=True, help="写入 index.md 的一句话摘要")
    parser.add_argument("--content-file", required=True, help="正文内容文件路径")
    parser.add_argument("--tag", action="append", default=[], help="frontmatter tags；可重复传入")
    parser.add_argument("--source", action="append", default=[], help="frontmatter sources；可重复传入 raw 相对路径")
    parser.add_argument("--related", action="append", default=[], help="关联连接中的页面名；可重复传入")
    parser.add_argument("--log-summary", required=True, help="write_log.py 的 summary")
    parser.add_argument("--nav-section", action="append", default=[], choices=("快速入口", "按主题浏览"), help="可选：同步补导航层")
    parser.add_argument("--nav-description", help="导航层描述；默认沿用 summary")
    return parser.parse_args()


def normalize_slug(slug: str) -> str:
    normalized = slug.strip().removesuffix(".md")
    if not normalized:
        raise SystemExit("--slug 不能为空")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", normalized):
        raise SystemExit("--slug 必须是 kebab-case")
    return normalized


def validate_tag(tag: str) -> None:
    if not re.fullmatch(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*", tag):
        raise SystemExit(f"frontmatter tag 必须是 kebab-case: {tag}")


def quote_yaml(value: str) -> str:
    escaped = value.replace('"', '\\"')
    return f'"{escaped}"'


def render_yaml_list(items: list[str]) -> str:
    if not items:
        return "[]"
    return "[" + ", ".join(quote_yaml(item) for item in items) + "]"


def build_related_section(related: list[str]) -> str:
    if not related:
        return "## 关联连接\n- 待补充与本页相关的实体、概念或来源页面。"
    lines = ["## 关联连接"]
    for page in related:
        lines.append(f"- [[{page}]]")
    return "\n".join(lines)


def ensure_related_section(body: str, related: list[str]) -> str:
    if "## 关联连接" in body:
        return body.rstrip() + "\n"
    return body.rstrip() + "\n\n" + build_related_section(related) + "\n"


def build_document(title: str, tags: list[str], sources: list[str], body: str) -> str:
    frontmatter = "\n".join(
        [
            "---",
            f"title: {quote_yaml(title)}",
            "type: synthesis",
            f"tags: {render_yaml_list(tags)}",
            f"sources: {render_yaml_list(sources)}",
            "last_updated: 2026-04-30",
            "---",
            "",
        ]
    )
    return frontmatter + body.rstrip() + "\n"


def write_synthesis_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> None:
    args = parse_args()
    workspace_root = Path(args.workspace_root).resolve()
    wiki_dir = workspace_root / "wiki"
    syntheses_dir = wiki_dir / "syntheses"
    index_path = wiki_dir / "index.md"
    log_path = wiki_dir / "log.md"

    slug = normalize_slug(args.slug)
    title = (args.title or slug).strip() or slug
    body_text = Path(args.content_file).read_text(encoding="utf-8").strip()
    if not body_text:
        raise SystemExit("正文内容不能为空")

    normalized_tags = [tag.strip() for tag in args.tag if tag.strip()]
    if not normalized_tags:
        raise SystemExit("至少需要提供一个 frontmatter tag")
    for tag in normalized_tags:
        validate_tag(tag)
    normalized_sources = [source.strip() for source in args.source if source.strip()]
    normalized_related = [page.strip() for page in args.related if page.strip()]

    document = build_document(
        title,
        normalized_tags,
        normalized_sources,
        ensure_related_section(body_text, normalized_related),
    )
    synthesis_path = syntheses_dir / f"{slug}.md"
    write_synthesis_file(synthesis_path, document)

    update_index_file(
        index_path,
        section="Syntheses",
        page=slug,
        description=args.summary.strip(),
        action="upsert",
        nav_sections=args.nav_section,
        nav_description=(args.nav_description or args.summary).strip(),
    )

    entry = build_entry(
        "query",
        args.log_summary.strip(),
        [parse_detail(f"输出=已保存至 [[{slug}]]")],
    )
    append_entry(log_path, entry)
    print(f"已写入 synthesis: {synthesis_path}")


if __name__ == "__main__":
    main()
