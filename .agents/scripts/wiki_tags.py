#!/usr/bin/env python3
"""扫描 Wiki frontmatter，生成 tag 池、tag 索引并报告 tag 质量问题。"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path


CONTENT_DIRS = ("sources", "entities", "concepts", "syntheses")
VALID_TYPES = {"source", "entity", "concept", "synthesis"}
TYPE_TO_DIR = {
    "source": "sources",
    "entity": "entities",
    "concept": "concepts",
    "synthesis": "syntheses",
}
TAG_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
INDEX_ENTRY_RE = re.compile(r"^- \[\[(?P<page>[^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\](?: — (?P<summary>.*))?$")

TAG_ALIASES = {
    "来源": None,
    "论文": None,
    "深读草稿": None,
    "综述": None,
    "概念": None,
    "方法": None,
    "视频异常检测": "video-anomaly-detection",
    "vad": "video-anomaly-detection",
    "VAD": "video-anomaly-detection",
    "无监督学习": "unsupervised-learning",
    "计算机视觉": "computer-vision",
    "机器视觉": "machine-vision",
    "监控": "surveillance",
    "帧预测": "frame-prediction",
    "注意力机制": "attention-mechanism",
    "语义一致性": "semantic-consistency",
    "多属性特征": "multi-attribute-feature",
    "异常检测": "anomaly-detection",
    "目标检测": "object-detection",
    "铁路安全": "railway-safety",
    "铁路入侵检测": "railway-intrusion-detection",
    "代码对照": "code-alignment",
    "模型分析": "model-analysis",
}

KNOWN_MISSPELLINGS = {
    "intrution": "intrusion",
    "anomoly": "anomaly",
    "detction": "detection",
    "dectection": "detection",
    "suprvised": "supervised",
    "unsuprvised": "unsupervised",
}


@dataclass(frozen=True)
class PageRecord:
    path: Path
    wiki_dir: Path
    title: str
    page_type: str
    tags: list[str]
    sources: list[str]
    last_updated: str

    @property
    def page(self) -> str:
        return self.path.stem

    @property
    def rel_path(self) -> str:
        return str(self.path.relative_to(self.wiki_dir))

    def to_dict(self, summary: str | None = None) -> dict:
        data = {
            "page": self.page,
            "title": self.title,
            "type": self.page_type,
            "tags": self.tags,
            "sources": self.sources,
            "last_updated": self.last_updated,
            "path": self.rel_path,
        }
        if summary is not None:
            data["summary"] = summary
        return data


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def issue(level: str, issue_type: str, file: str, detail: str) -> dict:
    return {"level": level, "type": issue_type, "file": file, "detail": detail}


def strip_yaml_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def parse_inline_list(value: str) -> list[str]:
    value = value.strip()
    if not (value.startswith("[") and value.endswith("]")):
        return [strip_yaml_quotes(value)] if value else []
    inner = value[1:-1].strip()
    if not inner:
        return []
    reader = csv.reader(io.StringIO(inner), skipinitialspace=True)
    return [strip_yaml_quotes(item.strip()) for item in next(reader) if strip_yaml_quotes(item.strip())]


def parse_frontmatter(path: Path) -> tuple[dict | None, str]:
    text = read_text(path)
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
    if not match:
        return None, text

    raw_frontmatter, body = match.groups()
    meta: dict[str, object] = {}
    lines = raw_frontmatter.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            index += 1
            continue
        key, raw_value = line.split(":", 1)
        key = key.strip()
        value = raw_value.strip()
        if value:
            meta[key] = parse_inline_list(value) if value.startswith("[") else strip_yaml_quotes(value)
            index += 1
            continue

        block_items: list[str] = []
        index += 1
        while index < len(lines):
            child = lines[index]
            if child and not child.startswith((" ", "\t")):
                break
            child_value = child.strip()
            if child_value.startswith("- "):
                block_items.append(strip_yaml_quotes(child_value[2:].strip()))
            index += 1
        meta[key] = [item for item in block_items if item]
    return meta, body


def as_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    if text.startswith("[") and text.endswith("]"):
        return parse_inline_list(text)
    return [text] if text else []


def get_pages(wiki_dir: Path) -> list[Path]:
    pages: list[Path] = []
    for subdir in CONTENT_DIRS:
        root = wiki_dir / subdir
        if root.exists():
            pages.extend(sorted(root.rglob("*.md")))
    return sorted(pages)


def load_pages(wiki_dir: Path) -> list[PageRecord]:
    records: list[PageRecord] = []
    for path in get_pages(wiki_dir):
        meta, _ = parse_frontmatter(path)
        if not meta:
            continue
        records.append(
            PageRecord(
                path=path,
                wiki_dir=wiki_dir,
                title=str(meta.get("title", "")).strip(),
                page_type=str(meta.get("type", "")).strip().strip('"\''),
                tags=as_list(meta.get("tags")),
                sources=as_list(meta.get("sources")),
                last_updated=str(meta.get("last_updated", "")).strip(),
            )
        )
    return records


def extract_index_summaries(index_path: Path) -> dict[str, str]:
    if not index_path.exists():
        return {}
    text = read_text(index_path)
    if "## 完整注册表" in text:
        text = text.split("## 完整注册表", 1)[1]
    summaries: dict[str, str] = {}
    for raw_line in text.splitlines():
        match = INDEX_ENTRY_RE.match(raw_line.strip())
        if match:
            summaries[match.group("page").strip()] = (match.group("summary") or "").strip()
    return summaries


def extract_index_frontmatter_tags(index_path: Path) -> list[str]:
    if not index_path.exists():
        return []
    meta, _ = parse_frontmatter(index_path)
    if not meta:
        return []
    return as_list(meta.get("tags"))


def tag_pool(records: list[PageRecord]) -> list[str]:
    return sorted({tag for record in records for tag in record.tags}, key=str.casefold)


def build_tag_index(records: list[PageRecord], summaries: dict[str, str]) -> dict[str, list[dict]]:
    index: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        summary = summaries.get(record.page, "")
        for tag in record.tags:
            index[tag].append(record.to_dict(summary=summary))
    return {tag: sorted(items, key=lambda item: (item["type"], item["page"].casefold())) for tag, items in sorted(index.items())}


def is_kebab_case(tag: str) -> bool:
    return bool(TAG_RE.fullmatch(tag))


def suggest_tag(tag: str, pool: list[str] | None = None) -> str | None:
    if tag in TAG_ALIASES:
        return TAG_ALIASES[tag]
    lowered = tag.lower().strip()
    if lowered in TAG_ALIASES:
        return TAG_ALIASES[lowered]
    for wrong, correct in KNOWN_MISSPELLINGS.items():
        if wrong in lowered:
            return lowered.replace(wrong, correct)
    if pool:
        valid_pool = [item for item in pool if is_kebab_case(item)]
        matches = sorted(
            ((SequenceMatcher(None, lowered, candidate).ratio(), candidate) for candidate in valid_pool),
            reverse=True,
        )
        if matches and matches[0][0] >= 0.84:
            return matches[0][1]
    return None


def collect_tag_issues(wiki_dir: Path, index_path: Path | None = None) -> list[dict]:
    index_path = index_path or (wiki_dir / "index.md")
    records = load_pages(wiki_dir)
    summaries = extract_index_summaries(index_path)
    pool = tag_pool(records)
    issues: list[dict] = []

    for record in records:
        if not record.tags:
            issues.append(issue("P0", "empty_tags", record.rel_path, "frontmatter tags 为空；每个页面至少需要一个 kebab-case tag"))
        for tag in record.tags:
            if not is_kebab_case(tag):
                suggestion = suggest_tag(tag, pool)
                detail = f"tag `{tag}` 不是 kebab-case"
                if suggestion:
                    detail += f"；建议规范化为 `{suggestion}`"
                issues.append(issue("P1", "invalid_tag", record.rel_path, detail))
            typo_suggestion = suggest_tag(tag, pool)
            if typo_suggestion and typo_suggestion != tag and is_kebab_case(tag):
                issues.append(issue("P1", "suspected_tag_typo", record.rel_path, f"tag `{tag}` 疑似拼写错误；建议 `{typo_suggestion}`"))

        if record.page not in summaries:
            issues.append(issue("P1", "missing_index_summary", "index.md", f"[[{record.page}]] 缺少完整注册表一句话描述"))
        elif not summaries[record.page]:
            issues.append(issue("P1", "empty_index_summary", "index.md", f"[[{record.page}]] 的完整注册表描述为空"))

    for left_index, left in enumerate(pool):
        for right in pool[left_index + 1 :]:
            if left == right:
                continue
            ratio = SequenceMatcher(None, left.casefold(), right.casefold()).ratio()
            if ratio >= 0.88:
                issues.append(issue("P1", "near_duplicate_tag", "tag-pool", f"`{left}` 与 `{right}` 高度相似，需人工确认是否重复"))

    index_tags = extract_index_frontmatter_tags(index_path)
    if not index_tags:
        issues.append(issue("P1", "missing_tag_index", "index.md", "index 顶部缺少由 frontmatter tag 池生成的 `tags: [...]` 区块"))
    else:
        actual = set(pool)
        indexed = set(index_tags)
        for tag in sorted(actual - indexed):
            issues.append(issue("P1", "tag_index_missing_tag", "index.md", f"index tag 区块缺少实际 tag `{tag}`"))
        for tag in sorted(indexed - actual):
            issues.append(issue("P1", "tag_index_extra_tag", "index.md", f"index tag 区块包含未被页面使用的 tag `{tag}`"))

    return issues


def quote_yaml(value: str) -> str:
    escaped = value.replace('"', '\\"')
    return f'"{escaped}"'


def render_yaml_list(items: list[str]) -> str:
    return "[" + ", ".join(quote_yaml(item) for item in items) + "]"


def render_index_frontmatter(tags: list[str]) -> str:
    return "---\n" + f"tags: {render_yaml_list(tags)}\n" + "---\n\n"


def update_index_frontmatter(text: str, tags: list[str]) -> str:
    rendered_tags = f"tags: {render_yaml_list(tags)}"
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        return render_index_frontmatter(tags) + text
    raw = match.group(1)
    if re.search(r"(?m)^tags:\s*.*$", raw):
        raw = re.sub(r"(?m)^tags:\s*.*$", rendered_tags, raw, count=1)
    else:
        raw = raw.rstrip() + "\n" + rendered_tags
    return "---\n" + raw.strip() + "\n---\n" + text[match.end() :]


def render_tag_browse_section(tag_index: dict[str, list[dict]]) -> str:
    lines = ["## 按 Tag 反查", "", "该区块由 `.agents/scripts/wiki_tags.py --print-tag-index` 从页面 frontmatter 临时生成；页面摘要来自 `wiki/index.md` 的 `## 完整注册表`。", ""]
    for tag, items in tag_index.items():
        lines.append(f"### {tag}")
        for item in items:
            summary = item.get("summary") or "缺少完整注册表摘要"
            lines.append(f"- [[{item['page']}]] — {summary}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n\n"


def update_tag_browse_section(text: str, tag_index: dict[str, list[dict]]) -> str:
    section = render_tag_browse_section(tag_index)
    pattern = r"(?ms)^## 按 Tag 浏览\n.*?(?=^## |\Z)"
    if re.search(pattern, text):
        return re.sub(pattern, section, text, count=1)
    marker = "## 完整注册表"
    if marker not in text:
        return text.rstrip() + "\n\n" + section
    return text.replace(marker, section + marker, 1)


def remove_tag_browse_section(text: str) -> str:
    pattern = r"(?ms)^## 按 Tag (?:浏览|反查)\n.*?(?=^## |\Z)"
    return re.sub(pattern, "", text, count=1)


def build_updated_index_text(index_path: Path, records: list[PageRecord]) -> str:
    original = read_text(index_path)
    pool = tag_pool(records)
    updated = update_index_frontmatter(original, pool)
    return remove_tag_browse_section(updated)


def build_result(wiki_dir: Path, index_path: Path) -> dict:
    records = load_pages(wiki_dir)
    summaries = extract_index_summaries(index_path)
    return {
        "wiki_dir": str(wiki_dir),
        "index_path": str(index_path),
        "page_count": len(records),
        "tag_pool": tag_pool(records),
        "pages": [record.to_dict(summary=summaries.get(record.page, "")) for record in records],
        "tag_index": build_tag_index(records, summaries),
        "issues": collect_tag_issues(wiki_dir, index_path),
    }


def print_human(result: dict) -> None:
    print(f"Wiki tag 扫描 — {result['wiki_dir']}")
    print(f"共 {result['page_count']} 个内容页；{len(result['tag_pool'])} 个去重 tag")
    print("\nTag 池:")
    for tag in result["tag_pool"]:
        print(f"- {tag}")
    if result["issues"]:
        print("\n问题:")
        for item in result["issues"]:
            print(f"- {item['level']} [{item['type']}] {item['file']}: {item['detail']}")
    else:
        print("\n未发现 tag 结构问题")


def main() -> None:
    parser = argparse.ArgumentParser(description="扫描 wiki frontmatter tags 并生成 tag 索引")
    parser.add_argument("--wiki-dir", required=True, help="wiki 目录")
    parser.add_argument("--index-path", help="wiki/index.md 路径；默认取 --wiki-dir/index.md")
    parser.add_argument("--json", action="store_true", dest="output_json", help="输出结构化 JSON")
    parser.add_argument("--print-tag-index", action="store_true", help="只打印由 frontmatter + index 完整注册表摘要生成的 tag 反查层")
    parser.add_argument("--update-index", action="store_true", help="只写回 index 顶部 tags 池，并移除旧的冗长 `按 Tag 浏览` 区块")
    parser.add_argument("--suggest-tag", help="为一个候选 tag 输出规范化建议")
    args = parser.parse_args()

    wiki_dir = Path(args.wiki_dir).resolve()
    index_path = Path(args.index_path).resolve() if args.index_path else wiki_dir / "index.md"
    if not wiki_dir.exists():
        print(f"错误: wiki 目录不存在: {wiki_dir}", file=sys.stderr)
        raise SystemExit(2)
    if not index_path.exists():
        print(f"错误: index 文件不存在: {index_path}", file=sys.stderr)
        raise SystemExit(2)

    records = load_pages(wiki_dir)
    if args.suggest_tag:
        pool = tag_pool(records)
        suggestion = suggest_tag(args.suggest_tag, pool)
        print(suggestion if suggestion is not None else "")
        return

    result = build_result(wiki_dir, index_path)
    if args.print_tag_index:
        print(render_tag_browse_section(result["tag_index"]).rstrip())
        return

    if args.update_index:
        updated = build_updated_index_text(index_path, records)
        index_path.write_text(updated, encoding="utf-8")
        print(f"已更新 index 顶部 tags 池: {index_path}")
        return

    if args.output_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_human(result)

    if any(item["level"] == "P0" for item in result["issues"]):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
