#!/usr/bin/env python3
"""把论文 PDF 的证据层落为 wiki/source 草稿与 assets 图片骨架。"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import date
from pathlib import Path
from typing import cast

import pymupdf

from pdf_tool import extract_text, probe, query_variants, snapshot_query, snapshot_query_preview
from write_index import update_index_file


def find_workspace_root() -> Path:
    """识别当前 vault 根目录，避免符号链接脚本把根目录解析到模板仓库。"""
    candidates = [Path.cwd(), *Path.cwd().parents]
    script_path = Path(__file__)
    if not script_path.is_absolute():
        script_path = Path.cwd() / script_path
    candidates.extend(script_path.parents)
    candidates.extend(script_path.resolve().parents)
    for candidate in candidates:
        if (candidate / "wiki").is_dir() and (candidate / "raw").is_dir():
            return candidate
    return script_path.resolve().parents[2]


WORKSPACE_ROOT = find_workspace_root()
WIKI_DIR = WORKSPACE_ROOT / "wiki"
ASSETS_DIR = WORKSPACE_ROOT / "assets"
CACHE_DIR = WORKSPACE_ROOT / ".cache" / "agents" / "papers"
INDEX_PATH = WIKI_DIR / "index.md"
LOG_PATH = WIKI_DIR / "log.md"
TARGET_FIGURE_QUOTA = 2
KIND_PRIORITY = {"figure": 0}
BODY_BOUNDARY_MARKERS = (
    "references",
    "appendix",
    "appendices",
    "supplementary",
    "supplementary materials",
    "supplemental",
)
BODY_LABEL_PATTERN = re.compile(
    r"(Figure|Fig\.|Table|Tab\.|图|表)\s*([0-9]+|[IVXLCDM]+)\b", re.IGNORECASE
)


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


def replace_section(text: str, heading: str, body: str) -> str:
    pattern = rf"(?ms)^{re.escape(heading)}\n.*?(?=^##\s+|\Z)"
    replacement = f"{heading}\n{body.strip()}\n"
    if re.search(pattern, text):
        return re.sub(pattern, replacement, text, count=1)
    return ensure_section(text, heading, body)


def update_last_updated(text: str, today: str) -> str:
    pattern = r"(?m)^(last_updated:\s*)(.+)$"
    if re.search(pattern, text):
        return re.sub(pattern, rf"\g<1>{today}", text, count=1)
    return text


def detect_main_body_page_limit(pdf_path: Path) -> int:
    with pymupdf.open(pdf_path) as doc:
        for page_index in range(doc.page_count):
            page = doc[page_index]
            text = str(page.get_text("text")).casefold()
            if not text.strip():
                continue
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            for line in lines:
                if any(
                    re.fullmatch(rf"{re.escape(marker)}\.?", line)
                    for marker in BODY_BOUNDARY_MARKERS
                ):
                    return page_index
    with pymupdf.open(pdf_path) as doc:
        return doc.page_count


def roman_to_int(token: str) -> int | None:
    values = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    normalized = token.upper().strip()
    if not normalized or not re.fullmatch(r"[IVXLCDM]+", normalized):
        return None
    total = 0
    previous = 0
    for character in reversed(normalized):
        value = values.get(character)
        if value is None:
            return None
        if value < previous:
            total -= value
        else:
            total += value
            previous = value
    return total if total > 0 else None


def parse_label_number(token: str) -> int | None:
    if token.isdigit():
        return int(token)
    return roman_to_int(token)


def normalize_caption_prefix(prefix: str) -> tuple[str, str]:
    lowered = prefix.casefold()
    if lowered.startswith("fig") or prefix == "图":
        return "figure", "zh" if prefix == "图" else "en"
    return "table", "zh" if prefix == "表" else "en"


def build_caption_query(prefix: str, token: str) -> str:
    normalized = prefix.strip()
    if normalized in {"图", "表"}:
        return f"{normalized}{token}"
    return f"{normalized} {token}"


def listify_strings(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item).strip()]


def collect_body_candidates(pdf_path: Path, page_limit: int) -> list[dict[str, object]]:
    discovered: list[dict[str, object]] = []
    seen_slots: set[tuple[str, int]] = set()
    with pymupdf.open(pdf_path) as doc:
        for page_index in range(min(doc.page_count, page_limit)):
            page = doc[page_index]
            text = str(page.get_text("text"))
            for match in BODY_LABEL_PATTERN.finditer(text):
                prefix = match.group(1)
                token = match.group(2)
                number = parse_label_number(token)
                if number is None:
                    continue
                kind, language_hint = normalize_caption_prefix(prefix)
                slot = (kind, number)
                if slot in seen_slots:
                    continue
                query = build_caption_query(prefix, token)
                discovered.append(
                    {
                        "kind": kind,
                        "query": query,
                        "query_variants": query_variants(query),
                        "semantic_slot": f"{kind}-{number:02d}",
                        "page_number": page_index + 1,
                        "label_text": prefix,
                        "language_hint": language_hint,
                        "original_index": len(discovered),
                    }
                )
                seen_slots.add(slot)
    return discovered


def preview_score(value: object) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return float("-inf")
    return float("-inf")


def selection_sort_key(capture: dict[str, object]) -> tuple[float, int, float, int, int]:
    kind = str(capture.get("kind", "figure"))
    page_number = capture.get("page_number")
    original_index = capture.get("original_index")
    return (
        -preview_score(capture.get("value_score")),
        KIND_PRIORITY.get(kind, 99),
        -preview_score(capture.get("score")),
        page_number if isinstance(page_number, int) else 10**9,
        original_index if isinstance(original_index, int) else 10**9,
    )


def preview_query_candidates(
    pdf_path: Path,
    variants: list[str],
    preset: str,
    page_number: int | None = None,
    mode: str = "auto",
    preview_timeout: float | None = None,
) -> tuple[dict[str, object] | None, list[dict[str, object]]]:
    best_result: dict[str, object] | None = None
    best_score = float("-inf")
    attempts: list[dict[str, object]] = []
    started_at = time.monotonic()
    for variant in variants:
        if preview_timeout is not None and time.monotonic() - started_at > preview_timeout:
            attempts.append({"query": variant, "error": "PreviewTimeout"})
            break
        try:
            result = snapshot_query_preview(pdf_path, variant, preset=preset, page=page_number, mode=mode)
        except Exception as exc:
            attempts.append({"query": variant, "error": type(exc).__name__})
            continue
        score = preview_score(result.get("score"))
        attempts.append({"query": variant, "page_number": result.get("page_number"), "score": result.get("score")})
        if best_result is None or score > best_score:
            best_result = dict(result)
            best_score = score
    return best_result, attempts


def build_selection_deficit(
    selected: list[dict[str, object]], target_figure_quota: int
) -> dict[str, object]:
    selected_figures = sum(1 for capture in selected if str(capture.get("kind")) == "figure")
    deficit = {
        "target": {"figure": target_figure_quota},
        "selected": {"figure": selected_figures},
        "missing": {
            "figure": max(0, target_figure_quota - selected_figures),
        },
        "policy": {
            "kind_priority": ["figure"],
            "sort_key": [
                "value_score desc",
                "kind priority",
                "score desc",
                "page asc",
                "original index asc",
            ],
        },
    }
    if deficit["missing"]["figure"] == 0:
        return {}
    return deficit


def format_formula_source_hint(capture: dict[str, object]) -> tuple[str, str]:
    page_number = capture.get("page_number")
    page_hint = f"第{page_number}页" if isinstance(page_number, int) else "未知页码"
    label = caption_label_for_capture(capture)
    snippet = re.sub(r"\s+", " ", str(capture.get("snippet", "")).strip())[:180].rstrip(" ,.;:-")
    if snippet:
        return (
            f"优先回看 {label} 所在的{page_hint}附近段落与相邻公式。",
            f"{label} 的原文描述里提到：{snippet}。",
        )
    reason = re.sub(r"\s+", " ", str(capture.get("selection_reason", "")).strip()).rstrip("。.;:-")
    if reason:
        return (
            f"优先回看 {label} 所在的{page_hint}附近段落与相邻公式。",
            f"自动筛选线索：{reason}。",
        )
    return (f"优先回看 {label} 所在的{page_hint}附近段落与相邻公式。", "")


def select_formula_reference(
    captures: list[dict[str, object]], preferred_buckets: tuple[str, ...], preferred_tokens: tuple[str, ...]
) -> dict[str, object] | None:
    if not captures:
        return None
    for capture in captures:
        if str(capture.get("value_bucket", "")) in preferred_buckets:
            return capture
    for capture in captures:
        haystack = _normalize_capture_text(capture)
        if any(token in haystack for token in preferred_tokens):
            return capture
    return captures[0]


def build_formula_block(captures: list[dict[str, object]]) -> str:
    formula_slots = [
        {
            "title": "总训练目标（待补）",
            "placeholder": "% 在这里补充总训练目标",
            "fallback_location": "优先在方法或训练章节搜索 `loss`、`objective`、`objective function`、`equation` 等字样。",
            "fallback_description": "原文通常会先用训练目标/损失函数的自然语言描述引出正式公式，可先顺着损失图、目标图或方法总览图附近的段落回查。",
            "preferred_buckets": ("loss/objective/anomaly-score",),
            "preferred_tokens": ("loss", "objective", "objective function", "equation", "formula", "training"),
        },
        {
            "title": "异常分数 / 检索分数（待补）",
            "placeholder": "% 在这里补充异常分数或检索分数",
            "fallback_location": "优先在推理、evaluation 或 anomaly score 相关段落搜索 `score`、`anomaly score`、`distance`、`psnr` 等字样。",
            "fallback_description": "原文往往会先解释帧级/片段级分数如何由误差项与距离项组合，再给出正式打分公式。",
            "preferred_buckets": ("loss/objective/anomaly-score",),
            "preferred_tokens": ("anomaly score", "score", "distance", "psnr", "reconstruction", "retrieval"),
        },
        {
            "title": "关键模块约束（待补，可删）",
            "placeholder": "% 在这里补充关键模块公式",
            "fallback_location": "优先在模块定义、memory / encoder / decoder / regularization 段落搜索 `constraint`、`module`、`memory`、`regularization` 等字样。",
            "fallback_description": "如果论文没有单独写模块约束公式，可删除本槽位；若有，通常出现在方法细节或子模块说明附近。",
            "preferred_buckets": ("architecture/training-framework", "loss/objective/anomaly-score"),
            "preferred_tokens": ("memory", "module", "encoder", "decoder", "regularization", "constraint", "architecture"),
        },
    ]
    blocks = [
        "> [!todo]",
        "> 你计划自己写公式，这里先预留稳定空位。每个槽位下都附了原文定位与描述线索，方便回到论文中找到对应公式。",
        "",
    ]
    for index, slot in enumerate(formula_slots, start=1):
        capture = select_formula_reference(captures, slot["preferred_buckets"], slot["preferred_tokens"])
        if capture is None:
            location_hint = slot["fallback_location"]
            description_hint = slot["fallback_description"]
        else:
            location_hint, description_hint = format_formula_source_hint(capture)
        blocks.extend(
            [
                f"### 公式 {index}：{slot['title']}",
                f"- 原文定位：{location_hint}",
                f"- 原文描述：{description_hint}",
                "$$",
                slot["placeholder"],
                "$$",
                "",
            ]
        )
    return "\n".join(blocks).rstrip()


def build_new_source(
    title_slug: str,
    pdf_name: str,
    today: str,
    metadata: dict[str, object],
    figure_embeds: list[str],
    captures: list[dict[str, object]],
    table_descriptions: str = "",
) -> str:
    author = metadata.get("author") or "未在 PDF metadata 中找到"
    subject = metadata.get("subject") or "未在 PDF metadata 中找到"
    page_count = metadata.get("page_count") or "未在 PDF metadata 中找到"
    figure_block = "\n".join(figure_embeds) if figure_embeds else "> [!todo]\n> 还没有自动捕获到图示；可用 `pdf_tool.py snapshot-query` 针对 `Figure 1` / `Table 1` 补抓。"
    return f'''---
title: "摘要-{title_slug}"
type: source
tags: [needs-topic-tag]
sources: ["raw/09-archived/{pdf_name}"]
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

## 表格速览
{table_descriptions}

## 关键公式
{build_formula_block(captures)}

## 代码对照线索
- `loss`：优先对照训练脚本中的总损失聚合位置。
- `score`：优先对照推理阶段的异常分数计算位置。
- `module`：优先把结构图中的编码器、记忆模块、head 映射到代码类/函数。

## 关联连接
- [[index.md]] — 注册表入口。
- [[log.md]] — 深读与后续 ingest/query 记录。
'''


def ensure_source_page(
    source_path: Path,
    title_slug: str,
    pdf_name: str,
    today: str,
    metadata: dict[str, object],
    figure_embeds: list[str],
    captures: list[dict[str, object]],
    table_descriptions: str = "",
) -> None:
    if not source_path.exists():
        source_path.write_text(
            build_new_source(title_slug, pdf_name, today, metadata, figure_embeds, captures, table_descriptions), encoding="utf-8"
        )
        return

    text = source_path.read_text(encoding="utf-8")
    text = update_last_updated(text, today)
    figure_block = "\n".join(figure_embeds) if figure_embeds else "> [!todo]\n> 还没有自动捕获到图示；可用 `pdf_tool.py snapshot-query` 补抓。"
    text = replace_section(text, "## 关键图示", figure_block)
    text = replace_section(
        text,
        "## 表格速览",
        table_descriptions,
    )
    text = replace_section(
        text,
        "## 关键公式",
        build_formula_block(captures),
    )
    text = replace_section(
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
    return update_index_file(
        INDEX_PATH,
        section="Sources",
        page=source_link,
        description=description,
        action="upsert",
    )


def append_log(today: str, source_link: str, asset_dir: Path) -> bool:
    if not LOG_PATH.exists():
        return False
    existing = LOG_PATH.read_text(encoding="utf-8")
    block_head = f"## [{today}] ingest | paper-deep-reading 为 {source_link} 生成图示与公式骨架"
    if block_head in existing:
        return False
    summary_line = f"- **变更**: 新增或更新 [[{source_link}]]；新增 `{asset_dir.relative_to(WORKSPACE_ROOT)}/...`"
    if summary_line in existing:
        return False
    block = f"\n## [{today}] ingest | paper-deep-reading 为 {source_link} 生成图示与公式骨架\n- **变更**: 新增或更新 [[{source_link}]]；新增 `{asset_dir.relative_to(WORKSPACE_ROOT)}/...`\n- **冲突**: 无\n"
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(block)
    return True


def build_capture_pool(
    pdf_path: Path,
    max_candidates: int | None = None,
    preview_timeout: float | None = None,
    progress: bool = False,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    page_limit = detect_main_body_page_limit(pdf_path)
    body_candidates = collect_body_candidates(pdf_path, page_limit)
    if max_candidates is not None:
        body_candidates = body_candidates[:max_candidates]

    ordered_candidates: list[dict[str, object]] = []
    skipped_candidates: list[dict[str, object]] = []
    total_candidates = len(body_candidates)
    for index, candidate in enumerate(body_candidates, start=1):
        page_number = candidate.get("page_number")
        if progress:
            print(
                f"[paper-deep-reading] preview {index}/{total_candidates}: "
                f"{candidate.get('semantic_slot')} {candidate.get('query')} page={page_number}",
                file=sys.stderr,
                flush=True,
            )
        result, attempts = preview_query_candidates(
            pdf_path,
            listify_strings(candidate.get("query_variants", [])),
            preset="generic" if candidate["kind"] == "table" else "figure",
            page_number=page_number if isinstance(page_number, int) else None,
            mode="pdf",
            preview_timeout=preview_timeout,
        )
        if result is None:
            skipped_candidates.append(
                {
                    "kind": candidate["kind"],
                    "query": candidate["query"],
                    "query_variants": candidate.get("query_variants", []),
                    "page_number": candidate["page_number"],
                    "original_index": candidate["original_index"],
                    "attempts": attempts,
                }
            )
            continue
        page_number = result.get("page_number")
        if not isinstance(page_number, int) or page_number > page_limit:
            continue
        enriched = dict(result)
        enriched["kind"] = candidate["kind"]
        enriched["query"] = candidate["query"]
        enriched["query_variants"] = candidate.get("query_variants", [])
        enriched["semantic_slot"] = candidate["semantic_slot"]
        enriched["label_text"] = candidate.get("label_text")
        enriched["language_hint"] = candidate.get("language_hint")
        enriched["preview_attempts"] = attempts
        enriched["original_index"] = candidate["original_index"]
        enriched["value_bucket"], enriched["value_score"], enriched["selection_reason"] = infer_value_label(enriched)
        ordered_candidates.append(enriched)

    ordered_candidates.sort(key=selection_sort_key)

    return ordered_candidates, skipped_candidates


def apply_rule_selection(
    ordered_candidates: list[dict[str, object]], max_figures: int
) -> tuple[list[dict[str, object]], dict[str, object]]:
    selected: list[dict[str, object]] = []
    figure_count = 0
    for candidate in ordered_candidates:
        kind = str(candidate.get("kind", "figure"))
        if kind == "figure":
            if len(selected) >= max_figures:
                continue
            selected.append(candidate)
            figure_count += 1

    selected.sort(key=selection_sort_key)
    for selection_rank, capture in enumerate(selected, start=1):
        capture["selection_rank"] = selection_rank

    return selected, {
        "selection_deficit": build_selection_deficit(selected, TARGET_FIGURE_QUOTA),
    }


def _normalize_capture_text(capture: dict[str, object]) -> str:
    parts = [
        str(capture.get("kind", "")),
        str(capture.get("query", "")),
        str(capture.get("snippet", "")),
    ]
    page_number = capture.get("page_number")
    if isinstance(page_number, int):
        parts.append(f"page {page_number}")
    return re.sub(r"\s+", " ", " ".join(parts)).casefold()


def caption_label_for_capture(capture: dict[str, object]) -> str:
    query = str(capture.get("query", "")).strip()
    if query:
        return query
    kind = str(capture.get("kind", "figure"))
    rank = capture.get("selection_rank")
    if isinstance(rank, int):
        if kind == "table":
            return f"入选第 {rank} 项表格"
        return f"入选第 {rank} 项图示"
    return "入选图示"


def infer_value_label(capture: dict[str, object]) -> tuple[str, int, str]:
    kind = str(capture.get("kind", "figure"))
    text = _normalize_capture_text(capture)
    page_number = capture.get("page_number")
    page_hint = f"第{page_number}页" if isinstance(page_number, int) else "未知页码"

    figure_rules = [
        (
            "architecture/training-framework",
            (
                "architecture",
                "framework",
                "encoder",
                "decoder",
                "memory",
                "module",
                "pipeline",
                "backbone",
                "network",
                "teacher",
                "student",
                "shared encoder",
                "training",
            ),
            330,
            "最适合作为方法总览或训练框架图，便于先解释模块边界与信息流",
        ),
        (
            "loss/objective/anomaly-score",
            (
                "loss",
                "objective",
                "anomaly score",
                "anomaly-score",
                "reconstruction",
                "separation",
                "compactness",
                "regularization",
                "equation",
                "formula",
                "objective function",
                "score",
            ),
            240,
            "最适合解释训练目标、损失项或异常分数构成",
        ),
        (
            "trade-off/performance",
            (
                "trade-off",
                "performance",
                "benchmark",
                "auc",
                "fps",
                "latency",
                "accuracy",
                "robustness",
                "ablation",
                "efficiency",
                "speed",
                "throughput",
            ),
            180,
            "最适合说明效果-效率权衡或性能趋势",
        ),
    ]
    for bucket, tokens, base_score, rationale in figure_rules:
        if any(token in text for token in tokens):
            score = base_score
            if bucket == "architecture/training-framework" and isinstance(page_number, int) and page_number <= 4:
                score += 12
            if bucket == "loss/objective/anomaly-score" and isinstance(page_number, int) and page_number <= 6:
                score += 8
            if bucket == "trade-off/performance" and isinstance(page_number, int) and page_number >= 6:
                score += 8
            return bucket, score, f"命中图示关键词；{rationale}。{page_hint}"

    return "generic-figure", 50, f"未命中架构、损失或性能线索，先按通用图示处理。{page_hint}"


def add_value_metadata(capture: dict[str, object]) -> dict[str, object]:
    value_bucket, value_score, selection_reason = infer_value_label(capture)
    enriched = dict(capture)
    enriched["value_bucket"] = value_bucket
    enriched["value_score"] = value_score
    enriched["selection_reason"] = selection_reason
    return enriched


def serialize_candidate_pool(candidates: list[dict[str, object]]) -> list[dict[str, object]]:
    serialized: list[dict[str, object]] = []
    for candidate in candidates:
        serialized.append(
            {
                "semantic_slot": candidate.get("semantic_slot"),
                "kind": candidate.get("kind"),
                "page_number": candidate.get("page_number"),
                "query": candidate.get("query"),
                "query_variants": candidate.get("query_variants"),
                "label_text": candidate.get("label_text"),
                "language_hint": candidate.get("language_hint"),
                "snippet": candidate.get("snippet"),
                "score": candidate.get("score"),
                "value_bucket": candidate.get("value_bucket"),
                "value_score": candidate.get("value_score"),
                "selection_reason": candidate.get("selection_reason"),
                "preview_attempts": candidate.get("preview_attempts"),
            }
        )
    return serialized


def select_candidates_by_slot(
    ordered_candidates: list[dict[str, object]], selected_slots: list[str]
) -> list[dict[str, object]]:
    wanted = {slot.strip() for slot in selected_slots if slot.strip()}
    return [candidate for candidate in ordered_candidates if str(candidate.get("semantic_slot")) in wanted]


def auto_capture_figures(
    pdf_path: Path,
    asset_dir: Path,
    max_figures: int,
    max_candidates: int | None = None,
    preview_timeout: float | None = None,
    progress: bool = False,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    ensure_dir(asset_dir)
    ordered_candidates, skipped_candidates = build_capture_pool(
        pdf_path,
        max_candidates=max_candidates,
        preview_timeout=preview_timeout,
        progress=progress,
    )
    capture_pool, selection_meta = apply_rule_selection(ordered_candidates, max_figures)
    selection_deficit = selection_meta.get("selection_deficit")
    captured: list[dict[str, object]] = []
    capture_errors: list[dict[str, object]] = []
    seen_outputs: set[str] = set()
    kind_counts: dict[str, int] = {}

    # 从候选池中收集表格（apply_rule_selection 只选图，表格单独处理）
    table_candidates = [
        c for c in ordered_candidates
        if str(c.get("kind", "")) == "table"
    ]

    for capture in capture_pool:
        kind = str(capture.get("kind", "figure"))
        page_number = capture.get("page_number")
        if not isinstance(page_number, int):
            continue
        kind_counts[kind] = kind_counts.get(kind, 0) + 1
        output = asset_dir / f"{kind}-{kind_counts[kind]:02d}.png"
        if str(output) in seen_outputs:
            continue
        try:
            result = snapshot_query(
                pdf_path,
                str(capture.get("query", "Figure 1")),
                output,
                preset=kind if kind in ("figure", "figure-column", "generic") else "figure",
                page=page_number,
                dpi=200,
            )
        except Exception as exc:
            capture_errors.append(
                {
                    "kind": kind,
                    "query": capture.get("query"),
                    "page_number": page_number,
                    "file_name": output.name,
                    "error": type(exc).__name__,
                }
            )
            continue
        result["kind"] = kind
        result["file_name"] = output.name
        result["query"] = str(capture.get("query", ""))
        result["query_variants"] = capture.get("query_variants", [])
        result["semantic_slot"] = str(capture.get("semantic_slot", ""))
        result["label_text"] = capture.get("label_text")
        result["language_hint"] = capture.get("language_hint")
        result["score"] = capture.get("score", result.get("score"))
        result["selection_rank"] = capture.get("selection_rank")
        captured.append(add_value_metadata(result))
        seen_outputs.add(str(output))

    # 表格不截图，直接以元数据形式加入 captured 列表供后续描述生成
    for table_candidate in table_candidates:
        table_result = dict(table_candidate)
        table_result["file_name"] = ""
        captured.append(add_value_metadata(table_result))

    return captured, {
        "selection_deficit": selection_deficit,
        "capture_errors": capture_errors or None,
        "skipped_candidates": skipped_candidates,
        "candidate_pool": serialize_candidate_pool(ordered_candidates),
        "recommended_slots": [str(candidate.get("semantic_slot", "")) for candidate in capture_pool],
    }


def capture_with_selected_slots(
    pdf_path: Path, asset_dir: Path, selected_candidates: list[dict[str, object]]
) -> tuple[list[dict[str, object]], dict[str, object]]:
    ensure_dir(asset_dir)
    selected = list(selected_candidates)
    selected.sort(key=selection_sort_key)
    for selection_rank, capture in enumerate(selected, start=1):
        capture["selection_rank"] = selection_rank

    captured: list[dict[str, object]] = []
    capture_errors: list[dict[str, object]] = []
    seen_outputs: set[str] = set()
    kind_counts: dict[str, int] = {}
    for capture in selected:
        kind = str(capture.get("kind", "figure"))
        page_number = capture.get("page_number")
        if not isinstance(page_number, int):
            continue

        # 表格：不截图，只保留元数据供后续生成文字描述
        if kind == "table":
            table_capture = dict(capture)
            table_capture["file_name"] = ""
            table_capture["query"] = str(capture.get("query", ""))
            table_capture["query_variants"] = capture.get("query_variants", [])
            table_capture["semantic_slot"] = str(capture.get("semantic_slot", ""))
            table_capture["label_text"] = capture.get("label_text")
            table_capture["language_hint"] = capture.get("language_hint")
            table_capture["score"] = capture.get("score")
            table_capture["selection_rank"] = capture.get("selection_rank")
            captured.append(add_value_metadata(table_capture))
            continue

        kind_counts[kind] = kind_counts.get(kind, 0) + 1
        output = asset_dir / f"{kind}-{kind_counts[kind]:02d}.png"
        if str(output) in seen_outputs:
            continue
        try:
            result = snapshot_query(
                pdf_path,
                str(capture.get("query", "Figure 1")),
                output,
                preset="table" if kind == "table" else "figure",
                page=page_number,
                dpi=200,
            )
        except Exception as exc:
            capture_errors.append(
                {
                    "kind": kind,
                    "query": capture.get("query"),
                    "page_number": page_number,
                    "file_name": output.name,
                    "error": type(exc).__name__,
                }
            )
            continue
        result["kind"] = kind
        result["file_name"] = output.name
        result["query"] = str(capture.get("query", ""))
        result["query_variants"] = capture.get("query_variants", [])
        result["semantic_slot"] = str(capture.get("semantic_slot", ""))
        result["label_text"] = capture.get("label_text")
        result["language_hint"] = capture.get("language_hint")
        result["score"] = capture.get("score", result.get("score"))
        result["selection_rank"] = capture.get("selection_rank")
        captured.append(add_value_metadata(result))
        seen_outputs.add(str(output))

    return captured, {
        "selection_deficit": build_selection_deficit(selected, TARGET_FIGURE_QUOTA),
        "capture_errors": capture_errors or None,
    }


def build_figure_embeds(slug: str, captures: list[dict[str, object]]) -> list[str]:
    def describe_capture(capture: dict[str, object]) -> str:
        kind = str(capture.get("kind", "figure"))
        bucket = str(capture.get("value_bucket", ""))
        reason = re.sub(r"\s+", " ", str(capture.get("selection_reason", "")).strip()).rstrip("。.;:-")
        snippet = re.sub(r"\s+", " ", str(capture.get("snippet", "")).strip())[:120].rstrip(" ,.;:-")
        label = caption_label_for_capture(capture)

        if bucket == "architecture/training-framework":
            label = "方法图"
            body = "优先帮助理解整体架构、模块边界与信息流"
        elif bucket == "loss/objective/anomaly-score":
            label = "损失/目标图"
            body = "优先解释训练目标、约束项或异常分数构成"
        elif bucket == "trade-off/performance":
            label = "权衡图"
            body = "优先展示效果、效率或鲁棒性的变化趋势"
        else:
            label = "通用图"
            body = "先作为整体方法或实验证据来读"

        detail = f"{label}：{body}。"
        if snippet:
            detail = f"{detail} 线索：{snippet}。"
        elif reason and label == "通用图":
            detail = f"{detail} {reason}。"
        return detail

    embeds = []
    ordered_captures = sorted(
        captures,
        key=lambda capture: (
            capture.get("selection_rank") if isinstance(capture.get("selection_rank"), int) else 10**9,
            str(capture.get("kind", "figure")),
            str(capture.get("file_name", "")),
        ),
    )
    for capture in ordered_captures:
        rank = capture.get("selection_rank")
        prefix = f"入选第 {rank} 项图示" if isinstance(rank, int) else "入选图示"
        caption_text = caption_label_for_capture(capture)
        embeds.append(
            f"- ![[papers/{slug}/{capture['file_name']}]]\n- {prefix}（{caption_text}）：{describe_capture(capture)}"
        )
    return embeds


def build_table_descriptions(
    slug: str, captures: list[dict[str, object]], max_tables: int = 1
) -> str:
    table_captures = [
        cap for cap in captures
        if str(cap.get("kind", "")) == "table"
    ]
    if not table_captures or max_tables <= 0:
        return (
            "> [!todo]\n"
            "> 本文未自动发现表格，可手动从 PDF 对应页码附近补录。"
        )

    # 按 snippet 长度降序（信息量优先），相同则 value_score 降序
    sorted_tables = sorted(
        table_captures,
        key=lambda cap: (
            -len(str(cap.get("snippet", ""))),
            -preview_score(cap.get("value_score")),
        ),
    )
    selected = sorted_tables[:max_tables]

    descriptions: list[str] = []
    for idx, cap in enumerate(selected, start=1):
        query = str(cap.get("query", "Table ?"))
        page_number = cap.get("page_number")
        page_hint = f"第{page_number}页" if isinstance(page_number, int) else "未知页码"
        snippet = str(cap.get("snippet", ""))

        table_md = _parse_snippet_to_markdown_table(snippet, query, page_hint)
        descriptions.append(table_md)

    return "\n\n".join(descriptions)


_SKIP_LINE_PATTERNS = [
    re.compile(r"Pattern Recognition", re.IGNORECASE),
    re.compile(r"^\d+\s*$", re.IGNORECASE),
    re.compile(r"contents lists available", re.IGNORECASE),
]
_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
_JOURNAL_META = re.compile(
    r"(Received|Accepted|Available online|https?://|doi:|journal homepage)",
    re.IGNORECASE,
)


def _parse_snippet_to_markdown_table(
    snippet: str, query: str, page_hint: str
) -> str:
    clean = _CONTROL_CHARS.sub("", snippet)
    lines = [
        line for line in clean.splitlines()
        if line.strip()
        and not any(pat.search(line) for pat in _SKIP_LINE_PATTERNS)
        and not _JOURNAL_META.search(line)
    ]

    all_rows: list[list[str]] = []
    for line in lines:
        cols = [c.strip() for c in re.split(r"\s{2,}", line) if c.strip()]
        if cols:
            all_rows.append(cols)

    # 如果只拆出 1 行且列数过多（pdftotext 把多行数据拼到一行），
    # 尝试按 每 7~8 个 token 切分为逻辑行（VAD 论文表格通常 Method|Ref|Venue|Object|数据列...）
    if len(all_rows) == 1 and len(all_rows[0]) > 15:
        cells = all_rows[0]
        # 找 header 行结束位置：第一个纯数字/符号 token 出现前
        header_end = 0
        for i, c in enumerate(cells):
            if re.match(r"^-?[\d.]+%?$", c) or c in {"–", "—", "-", "✓"}:
                header_end = i
                break
        header = cells[:header_end] if header_end > 1 else cells[:8]
        body_cells = cells[header_end:] if header_end > 1 else cells[8:]
        rows = [header] + [
            body_cells[i : i + len(header)]
            for i in range(0, len(body_cells), len(header))
        ]
        all_rows = [r for r in rows if r]

    data_rows: list[list[str]] = []
    for row in all_rows:
        numeric_count = sum(
            1 for c in row
            if re.match(r"^-?[\d.]+%?$", c) or c in {"–", "—", "-", "✓"}
        )
        if len(row) >= 3 and numeric_count >= 2:
            data_rows.append(row)

    if len(data_rows) < 2:
        clean_snippet = re.sub(r"\s+", " ", clean).strip()[:300]
        return (
            f"### {query}（{page_hint}）\n"
            f"> [!warning] pdftotext 未能拆分为列，保留原文块待人工整理。\n"
            f"\n"
            f"```text\n"
            f"{clean_snippet}\n"
            f"```\n"
            f"\n"
            f"- **来源**: {page_hint} {query}"
        )

    max_cols = max(len(row) for row in data_rows)
    header = "| " + " | ".join(f"列{i + 1}" for i in range(max_cols)) + " |"
    sep = "|" + "|".join(" --- " for _ in range(max_cols)) + "|"
    body_rows = [
        "| " + " | ".join(row + [""] * (max_cols - len(row))) + " |"
        for row in data_rows
    ]

    return (
        f"### {query}（{page_hint}）\n"
        f"{header}\n"
        f"{sep}\n"
        + "\n".join(body_rows)
        + f"\n\n"
        f"- **来源**: {page_hint} {query}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="生成论文深读草稿与图示骨架")
    parser.add_argument("pdf")
    parser.add_argument("--max-figures", type=int, default=3)
    parser.add_argument("--max-candidates", type=int, default=None, help="候选池阶段最多预览多少个正文图表候选；默认不限制")
    parser.add_argument("--max-tables", type=int, default=1, help="source 页最多生成几张表格的 Markdown 描述；0 表示关闭；默认 1")
    parser.add_argument("--preview-timeout", type=float, default=None, help="单个候选预览的秒级软超时；默认不限制")
    parser.add_argument("--progress", action="store_true", help="向 stderr 输出候选池/截图进度，避免长时间无输出")
    parser.add_argument("--engine", choices=["auto", "pdftotext", "pymupdf"], default="auto")
    parser.add_argument(
        "--selection-mode",
        choices=["rule", "agent"],
        default="rule",
        help="rule=脚本直接选图；agent=先输出候选池，再由 agent 回传 selected-slot 落盘",
    )
    parser.add_argument(
        "--selected-slot",
        action="append",
        default=[],
        help="agent 模式第二阶段使用：指定要真正落盘的 semantic slot，可重复传入",
    )
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

    if args.selection_mode == "agent":
        ordered_candidates, skipped_candidates = build_capture_pool(
            pdf_path,
            max_candidates=args.max_candidates,
            preview_timeout=args.preview_timeout,
            progress=args.progress,
        )
        rule_candidates, rule_meta = apply_rule_selection(ordered_candidates, args.max_figures)
        recommended_slots = [str(candidate.get("semantic_slot", "")) for candidate in rule_candidates]

        if not args.selected_slot:
            result = {
                "status": "needs_agent_selection",
                "pdf_path": str(pdf_path),
                "title": title,
                "slug": slug,
                "asset_dir": str(asset_dir),
                "text_cache": str(text_cache),
                "text_engine": used_engine,
                "candidate_pool": serialize_candidate_pool(ordered_candidates),
                "recommended_slots": recommended_slots,
                "selection_deficit": rule_meta.get("selection_deficit") or None,
                "skipped_candidates": skipped_candidates or None,
            }
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return

        selected_candidates = select_candidates_by_slot(ordered_candidates, args.selected_slot)
        if not selected_candidates:
            print(
                json.dumps(
                    {
                        "status": "error",
                        "message": "agent 模式下未选中任何有效 slot",
                        "available_slots": [candidate.get("semantic_slot") for candidate in ordered_candidates],
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
            raise SystemExit(2)

        captures, selection_meta = capture_with_selected_slots(pdf_path, asset_dir, selected_candidates)
        selection_deficit_payload = selection_meta.get("selection_deficit")
        capture_errors = selection_meta.get("capture_errors")
        candidate_pool_payload = serialize_candidate_pool(ordered_candidates)
        recommended_slots_payload = recommended_slots
        skipped_candidates_payload = skipped_candidates or None
        selected_by = "agent"
    else:
        captures, selection_meta = auto_capture_figures(
            pdf_path,
            asset_dir,
            args.max_figures,
            max_candidates=args.max_candidates,
            preview_timeout=args.preview_timeout,
            progress=args.progress,
        )
        selection_deficit_payload = selection_meta.get("selection_deficit") if isinstance(selection_meta, dict) else selection_meta
        capture_errors = selection_meta.get("capture_errors") if isinstance(selection_meta, dict) else None
        skipped_candidates_payload = selection_meta.get("skipped_candidates") if isinstance(selection_meta, dict) else None
        candidate_pool_payload = selection_meta.get("candidate_pool") if isinstance(selection_meta, dict) else None
        recommended_slots_payload = selection_meta.get("recommended_slots") if isinstance(selection_meta, dict) else None
        selected_by = "rule"

    figure_embeds = build_figure_embeds(slug, captures)
    table_descriptions = build_table_descriptions(slug, captures, args.max_tables)
    ensure_source_page(source_path, slug, pdf_path.name, today, metadata, figure_embeds, captures, table_descriptions)
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
        "selection_mode": args.selection_mode,
        "selected_by": selected_by,
        "candidate_pool": candidate_pool_payload,
        "recommended_slots": recommended_slots_payload,
        "captures": captures,
        "selection_deficit": selection_deficit_payload or None,
        "capture_errors": capture_errors,
        "skipped_candidates": skipped_candidates_payload,
        "index_changed": index_changed,
        "log_changed": log_changed,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
