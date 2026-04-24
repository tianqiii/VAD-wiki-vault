#!/usr/bin/env python3
"""把论文 PDF 的证据层落为 wiki/source 草稿与 assets 图片骨架。"""

from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path
from typing import cast

import pymupdf

from pdf_tool import extract_text, probe, snapshot_query


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
WIKI_DIR = WORKSPACE_ROOT / "wiki"
ASSETS_DIR = WORKSPACE_ROOT / "assets"
CACHE_DIR = WORKSPACE_ROOT / ".agents" / "cache" / "papers"
INDEX_PATH = WIKI_DIR / "index.md"
LOG_PATH = WIKI_DIR / "log.md"


def slugify(text: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", text).strip("-").lower()
    return slug or "untitled-paper"


def derive_title(stem: str, metadata_title: str | None) -> str:
    if metadata_title:
        cleaned = metadata_title.strip()
        if cleaned:
            return cleaned
    parts = [part.strip() for part in stem.split(" - ") if part.strip()]
    if len(parts) >= 3:
        return parts[-1]
    return stem


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def ensure_section(text: str, heading: str, body: str) -> str:
    if heading in text:
        return text
    anchor = "## 关联连接"
    insertion = f"\n{heading}\n{body.strip()}\n"
    if anchor in text:
        return text.replace(anchor, insertion + "\n" + anchor, 1)
    return text.rstrip() + insertion + "\n"


def update_last_updated(text: str, today: str) -> str:
    pattern = r"(?m)^(last_updated:\s*)(.+)$"
    if re.search(pattern, text):
        return re.sub(pattern, rf"\g<1>{today}", text, count=1)
    return text


def build_new_source(title_slug: str, pdf_name: str, today: str, metadata: dict[str, object], figure_embeds: list[str]) -> str:
    author = metadata.get("author") or "未在 PDF metadata 中找到"
    subject = metadata.get("subject") or "未在 PDF metadata 中找到"
    page_count = metadata.get("page_count") or "未在 PDF metadata 中找到"
    figure_block = "\n".join(figure_embeds) if figure_embeds else "> [!todo]\n> 还没有自动捕获到图示；可用 `pdf_tool.py snapshot-query` 针对 `Figure 1` / `Table 1` 补抓。"
    return f'''---
title: "摘要-{title_slug}"
type: source
tags: [来源, 论文, 深读草稿]
sources: ["raw/09-archive/{pdf_name}"]
last_updated: {today}
---

## Metadata
- **作者**: {author}
- **主题/摘要线索**: {subject}
- **页数**: {page_count}
- **深读状态**: 已生成图示/公式占位草稿，待人工补全。

## 核心摘要
> [!todo]
> 在这里补 3-5 句论文核心摘要：问题、方法、证据、局限。

## 关键图示
{figure_block}

## 关键公式
> [!todo]
> 你计划自己写公式，这里先预留稳定空位。建议至少补：总训练目标、异常分数、关键模块约束。

### 公式 1：总训练目标（待补）
$$
% 在这里补充总训练目标
$$

### 公式 2：异常分数 / 检索分数（待补）
$$
% 在这里补充异常分数或检索分数
$$

### 公式 3：关键模块约束（待补，可删）
$$
% 在这里补充关键模块公式
$$

## 代码对照线索
- `loss`：优先对照训练脚本中的总损失聚合位置。
- `score`：优先对照推理阶段的异常分数计算位置。
- `module`：优先把结构图中的编码器、记忆模块、head 映射到代码类/函数。

## 关联连接
- [[index.md]] — 注册表入口。
- [[log.md]] — 深读与后续 ingest/query 记录。
'''


def ensure_source_page(source_path: Path, title_slug: str, pdf_name: str, today: str, metadata: dict[str, object], figure_embeds: list[str]) -> None:
    if not source_path.exists():
        source_path.write_text(build_new_source(title_slug, pdf_name, today, metadata, figure_embeds), encoding="utf-8")
        return

    text = source_path.read_text(encoding="utf-8")
    text = update_last_updated(text, today)
    figure_block = "\n".join(figure_embeds) if figure_embeds else "> [!todo]\n> 还没有自动捕获到图示；可用 `pdf_tool.py snapshot-query` 补抓。"
    text = ensure_section(text, "## 关键图示", figure_block)
    text = ensure_section(
        text,
        "## 关键公式",
        '''> [!todo]
> 你计划自己写公式，这里先预留稳定空位。建议至少补：总训练目标、异常分数、关键模块约束。

### 公式 1：总训练目标（待补）
$$
% 在这里补充总训练目标
$$

### 公式 2：异常分数 / 检索分数（待补）
$$
% 在这里补充异常分数或检索分数
$$

### 公式 3：关键模块约束（待补，可删）
$$
% 在这里补充关键模块公式
$$
''',
    )
    text = ensure_section(
        text,
        "## 代码对照线索",
        '''- `loss`：优先对照训练脚本中的总损失聚合位置。
- `score`：优先对照推理阶段的异常分数计算位置。
- `module`：优先把结构图中的编码器、记忆模块、head 映射到代码类/函数。''',
    )
    source_path.write_text(text, encoding="utf-8")


def add_source_to_index(source_link: str, description: str) -> bool:
    if not INDEX_PATH.exists():
        return False
    text = INDEX_PATH.read_text(encoding="utf-8")
    entry = f"- [[{source_link}]] — {description}"
    if entry in text or f"[[{source_link}]]" in text:
        return False

    pattern = r"(### Sources\n)(.*?)(\n### Entities)"
    match = re.search(pattern, text, flags=re.DOTALL)
    if not match:
        return False
    registry_body = match.group(2).rstrip()
    replacement = match.group(1) + registry_body + "\n" + entry + "\n\n### Entities"
    updated = re.sub(pattern, replacement, text, count=1, flags=re.DOTALL)
    INDEX_PATH.write_text(updated, encoding="utf-8")
    return True


def append_log(today: str, source_link: str, asset_dir: Path) -> bool:
    if not LOG_PATH.exists():
        return False
    marker = f"[[{source_link}]]"
    existing = LOG_PATH.read_text(encoding="utf-8")
    if marker in existing and "paper-deep-reading" in existing:
        return False
    block = f"\n## [{today}] ingest | paper-deep-reading 为 {source_link} 生成图示与公式骨架\n- **变更**: 新增或更新 [[{source_link}]]；新增 `{asset_dir.relative_to(WORKSPACE_ROOT)}/...`\n- **冲突**: 无\n"
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(block)
    return True


def auto_capture_figures(pdf_path: Path, asset_dir: Path, max_figures: int) -> list[dict[str, object]]:
    ensure_dir(asset_dir)
    plans = [
        ("Figure 1", "figure", 1),
        ("Fig. 1", "figure", 1),
        ("Table 1", "table", 1),
        ("Figure 2", "figure", 2),
        ("Fig. 2", "figure", 2),
    ]
    captured: list[dict[str, object]] = []
    seen_outputs: set[str] = set()
    for query, kind, number in plans:
        if len(captured) >= max_figures:
            break
        output = asset_dir / f"{kind}-{number:02d}.png"
        if str(output) in seen_outputs or output.exists():
            continue
        try:
            result = snapshot_query(
                pdf_path,
                query,
                output,
                preset="table" if kind == "table" else "figure",
                dpi=200,
            )
        except Exception:
            continue
        result["kind"] = kind
        result["file_name"] = output.name
        result["query"] = query
        captured.append(result)
        seen_outputs.add(str(output))
    return captured


def build_figure_embeds(slug: str, captures: list[dict[str, object]]) -> list[str]:
    embeds = []
    for capture in captures:
        label = "图" if capture.get("kind") == "figure" else "表"
        embeds.append(
            f"- ![[papers/{slug}/{capture['file_name']}]]\n- {label}示占位：来自 `{capture['query']}` 的自动裁图，后续可补充一句话解释。"
        )
    return embeds


def main() -> None:
    parser = argparse.ArgumentParser(description="生成论文深读草稿与图示骨架")
    parser.add_argument("pdf")
    parser.add_argument("--max-figures", type=int, default=3)
    parser.add_argument("--engine", choices=["auto", "pdftotext", "pymupdf"], default="auto")
    args = parser.parse_args()

    pdf_path = Path(args.pdf).resolve()
    if not pdf_path.exists():
        print(json.dumps({"status": "error", "message": f"PDF 不存在: {pdf_path}"}, ensure_ascii=False, indent=2))
        raise SystemExit(2)

    today = date.today().isoformat()
    pdf_info = probe(pdf_path)
    raw_metadata = pdf_info.get("metadata", {})
    metadata = cast(dict[str, object], raw_metadata if isinstance(raw_metadata, dict) else {})
    metadata = {str(key): value for key, value in metadata.items()}
    page_count_value = pdf_info.get("page_count")
    metadata["page_count"] = page_count_value if isinstance(page_count_value, int) else 0
    title_value = metadata.get("title")
    title = derive_title(pdf_path.stem, title_value if isinstance(title_value, str) else None)
    slug = slugify(title)
    source_name = f"摘要-{slug}"
    source_path = WIKI_DIR / "sources" / f"{source_name}.md"
    asset_dir = ASSETS_DIR / "papers" / slug
    cache_dir = CACHE_DIR / slug

    ensure_dir(asset_dir)
    ensure_dir(cache_dir)

    text, used_engine = extract_text(pdf_path, engine=args.engine)
    text_cache = cache_dir / "source_text.txt"
    text_cache.write_text(text, encoding="utf-8")

    captures = auto_capture_figures(pdf_path, asset_dir, args.max_figures)
    figure_embeds = build_figure_embeds(slug, captures)
    ensure_source_page(source_path, slug, pdf_path.name, today, metadata, figure_embeds)
    index_changed = add_source_to_index(source_name, "论文深读草稿页，预留关键图示、公式空位与代码对照线索。")
    log_changed = append_log(today, source_name, asset_dir)

    result = {
        "status": "ok",
        "pdf_path": str(pdf_path),
        "title": title,
        "slug": slug,
        "source_path": str(source_path),
        "asset_dir": str(asset_dir),
        "text_cache": str(text_cache),
        "text_engine": used_engine,
        "captures": captures,
        "index_changed": index_changed,
        "log_changed": log_changed,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
