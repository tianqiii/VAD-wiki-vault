#!/usr/bin/env python3
"""适配当前仓库 schema 的统一确定性健康检查脚本。"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

WIKI_DIR: Path
RAW_DIR: Path

REQUIRED_FRONTMATTER = {"title", "type", "tags", "sources", "last_updated"}
VALID_TYPES = {"source", "entity", "concept", "synthesis"}
CONTENT_DIRS = ("sources", "entities", "concepts", "syntheses")
ASSET_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".pdf", ".mp4", ".mov", ".avi"}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_frontmatter(path: Path) -> tuple[dict | None, str]:
    text = read_text(path)
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
    if not m:
        return None, text
    meta_text, body = m.groups()
    meta: dict[str, str] = {}
    for line in meta_text.splitlines():
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip()
    return meta, body


def get_pages() -> list[Path]:
    pages: list[Path] = []
    for subdir in CONTENT_DIRS:
        root = WIKI_DIR / subdir
        if root.exists():
            pages.extend(sorted(root.rglob("*.md")))
    return sorted(pages)


def extract_wikilinks(text: str) -> list[str]:
    return [m.strip() for m in re.findall(r"\[\[([^\]|#]+)(?:#[^\]]+)?(?:\|[^\]]+)?\]\]", text)]


def is_asset_link(target: str) -> bool:
    lowered = target.casefold()
    return any(lowered.endswith(ext) for ext in ASSET_EXTENSIONS)


def extract_registry_links(index_text: str) -> set[str]:
    if "## 完整注册表" not in index_text:
        return set()
    return set(extract_wikilinks(index_text.split("## 完整注册表", 1)[1]))


def extract_scale_stats(index_text: str) -> dict[str, int]:
    stats = {}
    for key in ["Sources", "Entities", "Concepts", "Syntheses"]:
        m = re.search(rf"- {key}：([0-9]+)", index_text)
        if m:
            stats[key] = int(m.group(1))
    return stats


def actual_scale_stats() -> dict[str, int]:
    mapping = {
        "Sources": WIKI_DIR / "sources",
        "Entities": WIKI_DIR / "entities",
        "Concepts": WIKI_DIR / "concepts",
        "Syntheses": WIKI_DIR / "syntheses",
    }
    return {key: len(list(path.glob("*.md"))) if path.exists() else 0 for key, path in mapping.items()}


def issue(level: str, issue_type: str, file: str, detail: str) -> dict:
    return {"level": level, "type": issue_type, "file": file, "detail": detail}


def check_frontmatter(pages: list[Path]) -> list[dict]:
    issues = []
    for page in pages:
        rel = str(page.relative_to(WIKI_DIR))
        fm, _ = parse_frontmatter(page)
        if fm is None:
            issues.append(issue("P0", "no_frontmatter", rel, "缺少 YAML frontmatter"))
            continue
        missing = sorted(REQUIRED_FRONTMATTER - set(fm.keys()))
        if missing:
            issues.append(issue("P0", "incomplete_frontmatter", rel, f"缺少字段: {', '.join(missing)}"))
        if "type" in fm and fm["type"].strip('"\' ') not in VALID_TYPES:
            issues.append(issue("P1", "invalid_type", rel, f"type '{fm['type']}' 不在合法值 {sorted(VALID_TYPES)} 中"))
    return issues


def check_relation_section(pages: list[Path]) -> list[dict]:
    issues = []
    for page in pages:
        if "## 关联连接" not in read_text(page):
            issues.append(issue("P1", "missing_related_section", str(page.relative_to(WIKI_DIR)), "缺少 `## 关联连接` 区块"))
    return issues


def check_broken_links(pages: list[Path]) -> list[dict]:
    issues = []
    page_ids = {p.stem for p in pages}
    for page in pages:
        rel = str(page.relative_to(WIKI_DIR))
        for target in extract_wikilinks(read_text(page)):
            if target.startswith("raw/"):
                continue
            if is_asset_link(target):
                continue
            if target in {"index", "index.md", "log", "log.md"}:
                continue
            if target not in page_ids:
                issues.append(issue("P0", "broken_link", rel, f"[[{target}]] 指向不存在的页面"))
    return issues


def check_orphans(pages: list[Path]) -> list[dict]:
    incoming: dict[str, set[str]] = defaultdict(set)
    for page in pages:
        pid = page.stem
        for target in extract_wikilinks(read_text(page)):
            if target != pid:
                incoming[target].add(pid)
    issues = []
    for page in pages:
        if not incoming.get(page.stem):
            issues.append(issue("P1", "orphan_page", str(page.relative_to(WIKI_DIR)), "没有任何其他 wiki 页面链接到此页"))
    return issues


def check_registry_consistency(pages: list[Path]) -> list[dict]:
    index_path = WIKI_DIR / "index.md"
    if not index_path.exists():
        return [issue("P0", "missing_index", "index.md", "index.md 不存在")]
    registry_links = extract_registry_links(read_text(index_path))
    actual_pages = {p.stem for p in pages}
    issues = []
    for registered in sorted(registry_links - actual_pages):
        issues.append(issue("P0", "registry_dangling", "index.md", f"完整注册表登记了 [[{registered}]]，但文件不存在"))
    for page in sorted(actual_pages - registry_links):
        issues.append(issue("P0", "registry_missing", "index.md", f"文件 [[{page}]] 存在，但未登记到 `## 完整注册表`"))
    return issues


def check_scale_stats() -> list[dict]:
    index_path = WIKI_DIR / "index.md"
    if not index_path.exists():
        return []
    index_stats = extract_scale_stats(read_text(index_path))
    actual_stats = actual_scale_stats()
    issues = []
    for key, actual in actual_stats.items():
        stated = index_stats.get(key)
        if stated is None:
            issues.append(issue("P1", "missing_scale_stat", "index.md", f"顶部规模统计缺少 {key}"))
        elif stated != actual:
            issues.append(issue("P1", "wrong_scale_stat", "index.md", f"{key} 统计写为 {stated}，实际为 {actual}"))
    return issues


def check_stale_raw_paths(pages: list[Path]) -> list[dict]:
    issues = []
    for page in pages:
        if "raw/02-papers/" in read_text(page):
            issues.append(issue("P1", "stale_raw_path", str(page.relative_to(WIKI_DIR)), "仍引用 `raw/02-papers/`，应改为 `raw/09-archive/`"))
    return issues


def check_conflicts(pages: list[Path]) -> list[dict]:
    issues = []
    for page in pages:
        if "## 知识冲突" in read_text(page):
            issues.append(issue("P1", "knowledge_conflict", str(page.relative_to(WIKI_DIR)), "存在 `## 知识冲突` 区块，需人工审阅"))
    return issues


def run_checks() -> list[dict]:
    pages = get_pages()
    issues = []
    issues += check_frontmatter(pages)
    issues += check_relation_section(pages)
    issues += check_broken_links(pages)
    issues += check_orphans(pages)
    issues += check_registry_consistency(pages)
    issues += check_scale_stats()
    issues += check_stale_raw_paths(pages)
    issues += check_conflicts(pages)
    order = {"P0": 0, "P1": 1, "P2": 2}
    issues.sort(key=lambda x: (order.get(x["level"], 9), x["file"], x["type"]))
    return issues


def print_human(issues: list[dict]) -> None:
    pages = get_pages()
    p0 = [i for i in issues if i["level"] == "P0"]
    p1 = [i for i in issues if i["level"] == "P1"]
    p2 = [i for i in issues if i["level"] == "P2"]
    print(f"Wiki 健康检查 — {WIKI_DIR}")
    print(f"共 {len(pages)} 个内容页\n")
    if not issues:
        print("✅ 未发现问题")
        return
    if p0:
        print(f"🔴 P0 — 需要修复 ({len(p0)})")
        for item in p0:
            print(f"  [{item['type']}] {item['file']}: {item['detail']}")
        print()
    if p1:
        print(f"🟡 P1 — 建议改进 ({len(p1)})")
        for item in p1:
            print(f"  [{item['type']}] {item['file']}: {item['detail']}")
        print()
    if p2:
        print(f"🟢 P2 — 可选优化 ({len(p2)})")
        for item in p2:
            print(f"  [{item['type']}] {item['file']}: {item['detail']}")
        print()
    print(f"总计: {len(p0)} P0 / {len(p1)} P1 / {len(p2)} P2")


def main() -> None:
    parser = argparse.ArgumentParser(description="当前仓库 wiki 的确定性健康检查")
    parser.add_argument("--wiki-dir", required=True)
    parser.add_argument("--raw-dir", required=True)
    parser.add_argument("--json", action="store_true", dest="output_json")
    args = parser.parse_args()
    global WIKI_DIR, RAW_DIR
    WIKI_DIR = Path(args.wiki_dir).resolve()
    RAW_DIR = Path(args.raw_dir).resolve()
    if not WIKI_DIR.exists():
        print(f"错误: wiki 目录不存在: {WIKI_DIR}", file=sys.stderr)
        raise SystemExit(2)
    if not RAW_DIR.exists():
        print(f"错误: raw 目录不存在: {RAW_DIR}", file=sys.stderr)
        raise SystemExit(2)
    issues = run_checks()
    if args.output_json:
        print(json.dumps(issues, ensure_ascii=False, indent=2))
    else:
        print_human(issues)
    if any(item["level"] == "P0" for item in issues):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
