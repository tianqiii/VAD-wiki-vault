#!/usr/bin/env python3
"""
在磁盘上搜索 wiki/index.md 的命中条目，而不是把整篇 index.md 放进 LLM 上下文。

目标：
1. 优先返回导航层与完整注册表中最相关的候选页面
2. 输出结构化 JSON，供 query skill 继续精读少量页面

用法：
    python .agents/scripts/search_index.py --index-path /abs/wiki/index.md --query "BiSP 和 ABMA 有什么关系？"
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from wiki_tags import load_pages


STOPWORDS = {
    "的", "和", "与", "及", "是", "什么", "如何", "为什么", "哪些", "哪个", "对比", "比较", "一下",
    "the", "a", "an", "and", "or", "to", "of", "in", "for", "is", "what", "how", "why", "vs",
}

SECTION_WEIGHTS = {
    "快速入口": 1.8,
    "按主题浏览": 1.5,
    "Sources": 1.1,
    "Entities": 1.4,
    "Concepts": 1.3,
    "Syntheses": 1.35,
}


def tokenize(text: str) -> list[str]:
    parts = re.findall(r"[A-Za-z][A-Za-z0-9_-]*|[\u4e00-\u9fff]{1,8}", text.lower())
    tokens = []
    for part in parts:
        if part in STOPWORDS:
            continue
        tokens.append(part)
    return tokens


def parse_index(index_text: str) -> list[dict]:
    entries: list[dict] = []
    current_section = ""
    in_registry = False

    for lineno, raw_line in enumerate(index_text.splitlines(), start=1):
        line = raw_line.strip()
        if line.startswith("## "):
            current_section = line[3:].strip()
            if current_section == "完整注册表":
                in_registry = True
            continue
        if line.startswith("### "):
            current_section = line[4:].strip()
            continue
        if not line.startswith("- "):
            continue

        match = re.match(r"- \[\[([^\]]+)\]\] — (.+)$", line)
        if not match:
            continue
        title, summary = match.groups()
        entries.append(
            {
                "title": title.strip(),
                "summary": summary.strip(),
                "section": current_section,
                "line": lineno,
                "registry": in_registry,
            }
        )

    return entries


def score_entry(entry: dict, query: str, query_tokens: list[str]) -> tuple[float, list[str]]:
    haystack_title = entry["title"].lower()
    haystack_summary = entry["summary"].lower()
    haystack_tags = " ".join(entry.get("tags", [])).lower()
    haystack = f"{haystack_title} {haystack_summary} {haystack_tags}"
    score = 0.0
    reasons: list[str] = []

    filter_tag_matches = entry.get("filter_tag_matches", [])
    if filter_tag_matches:
        score += 2.5 * len(filter_tag_matches)
        reasons.append("过滤tag命中:" + ",".join(filter_tag_matches))

    if query.lower() in haystack:
        score += 8.0
        reasons.append("完整问题命中标题/摘要")

    for token in query_tokens:
        if token in haystack_title:
            score += 3.5
            reasons.append(f"标题命中:{token}")
        elif token in haystack_summary:
            score += 1.8
            reasons.append(f"摘要命中:{token}")
        elif token in haystack_tags:
            score += 2.2
            reasons.append(f"tag命中:{token}")

    section_weight = SECTION_WEIGHTS.get(entry["section"], 1.0)
    score *= section_weight
    if section_weight != 1.0:
        reasons.append(f"区块加权:{entry['section']}")

    return score, reasons


def main() -> None:
    parser = argparse.ArgumentParser(description="搜索 index.md 中最相关的候选条目")
    parser.add_argument("--index-path", required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--top-k", type=int, default=8)
    parser.add_argument("--wiki-dir", help="wiki 目录；提供后可按 frontmatter type/tag 过滤")
    parser.add_argument("--type", action="append", default=[], choices=("source", "entity", "concept", "synthesis"), help="按页面 type 过滤；可重复")
    parser.add_argument("--tag", action="append", default=[], help="按 frontmatter tag 过滤；可重复，OR 语义")
    args = parser.parse_args()

    index_path = Path(args.index_path).resolve()
    if not index_path.exists():
        print(json.dumps({"status": "error", "message": f"index 文件不存在: {index_path}"}, ensure_ascii=False, indent=2))
        raise SystemExit(2)

    index_text = index_path.read_text(encoding="utf-8")
    entries = parse_index(index_text)
    wiki_dir = Path(args.wiki_dir).resolve() if args.wiki_dir else index_path.parent
    page_meta = {record.page: record for record in load_pages(wiki_dir)} if wiki_dir.exists() else {}
    enriched_entries = []
    for entry in entries:
        record = page_meta.get(entry["title"])
        if record:
            entry = {**entry, "type": record.page_type, "tags": record.tags, "path": record.rel_path}
        else:
            entry = {**entry, "type": "", "tags": [], "path": ""}
        if args.type and entry["type"] not in args.type:
            continue
        filter_tag_matches = sorted(set(args.tag) & set(entry["tags"]))
        if args.tag and not filter_tag_matches:
            continue
        entry["filter_tag_matches"] = filter_tag_matches
        enriched_entries.append(entry)
    entries = enriched_entries
    query_tokens = tokenize(args.query)

    scored = []
    for entry in entries:
        score, reasons = score_entry(entry, args.query, query_tokens)
        if score <= 0:
            continue
        scored.append(
            {
                **entry,
                "score": round(score, 3),
                "reasons": reasons,
            }
        )

    scored.sort(key=lambda x: (-x["score"], x["line"], x["title"]))
    result = {
        "status": "ok",
        "index_path": str(index_path),
        "query": args.query,
        "query_tokens": query_tokens,
        "filters": {"type": args.type, "tag": args.tag},
        "candidates": scored[: args.top_k],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
