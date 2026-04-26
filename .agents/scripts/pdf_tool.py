#!/usr/bin/env python3
"""PDF 工具层：抽文本、找锚点、渲染页面、按查询或矩形裁图。"""

from __future__ import annotations

import argparse
import io
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, cast

import pymupdf

try:
    from PIL import Image as PILImage
except ImportError:  # pragma: no cover
    PILImage = None  # ty:ignore[invalid-assignment]

if TYPE_CHECKING:
    from PIL.Image import Image as PILImageType

try:
    import pytesseract  # type: ignore
    from pytesseract import Output as TesseractOutput  # type: ignore
except ImportError:  # pragma: no cover
    pytesseract = None  # type: ignore[assignment]
    TesseractOutput = None  # type: ignore[assignment]


PRESET_MARGINS: dict[str, tuple[float, float, float, float]] = {
    "exact": (0.0, 0.0, 0.0, 0.0),
    "generic": (24.0, 16.0, 24.0, 64.0),
    "theorem": (24.0, 16.0, 24.0, 64.0),
    "figure": (36.0, 32.0, 36.0, 180.0),
    "figure-column": (20.0, 20.0, 20.0, 40.0),
    "table": (28.0, 16.0, 28.0, 140.0),
    "equation": (18.0, 12.0, 18.0, 42.0),
}

INFERRED_MARGINS: dict[str, tuple[float, float, float, float]] = {
    "generic": (12.0, 12.0, 12.0, 18.0),
    "theorem": (10.0, 10.0, 10.0, 18.0),
    "figure": (16.0, 16.0, 16.0, 20.0),
    "figure-column": (10.0, 12.0, 10.0, 18.0),
    "table": (12.0, 12.0, 12.0, 32.0),
}

MAX_VERTICAL_GAP: dict[str, float] = {
    "generic": 260.0,
    "theorem": 220.0,
    "figure": 340.0,
    "figure-column": 260.0,
    "table": 520.0,
}


@dataclass
class SearchHit:
    page_index: int
    page_number: int
    rect: pymupdf.Rect
    snippet: str

    def to_dict(self) -> dict[str, object]:
        return {
            "page_index": self.page_index,
            "page_number": self.page_number,
            "rect": [
                round(self.rect.x0, 2),
                round(self.rect.y0, 2),
                round(self.rect.x1, 2),
                round(self.rect.y1, 2),
            ],
            "snippet": self.snippet,
        }


@dataclass
class TextBlock:
    rect: pymupdf.Rect
    text: str


@dataclass
class SnapshotCandidate:
    page_index: int
    query: str
    base_rect: pymupdf.Rect
    inferred_rect: pymupdf.Rect | None
    score: float

    def to_preview_dict(self, preset: str) -> dict[str, object]:
        preview = {
            "page_index": self.page_index,
            "page_number": self.page_index + 1,
            "query": self.query,
            "preset": preset,
            "base_rect": rect_to_list(self.base_rect),
            "inferred_rect": rect_to_list(self.inferred_rect)
            if self.inferred_rect is not None
            else None,
            "score": round(self.score, 2),
        }
        return preview


@dataclass
class OCRLine:
    rect: pymupdf.Rect
    text: str


def normalize_token(text: str) -> str:
    return re.sub(r"[^\w]+", "", text, flags=re.UNICODE).casefold()


def rect_to_list(rect: pymupdf.Rect) -> list[float]:
    return [round(rect.x0, 2), round(rect.y0, 2), round(rect.x1, 2), round(rect.y1, 2)]


def clamp_rect(rect: pymupdf.Rect, page_rect: pymupdf.Rect) -> pymupdf.Rect:
    return pymupdf.Rect(
        max(page_rect.x0, rect.x0),
        max(page_rect.y0, rect.y0),
        min(page_rect.x1, rect.x1),
        min(page_rect.y1, rect.y1),
    )


def expand_rect(
    rect: pymupdf.Rect, page_rect: pymupdf.Rect, preset: str
) -> pymupdf.Rect:
    left, top, right, bottom = PRESET_MARGINS[preset]
    expanded = pymupdf.Rect(
        rect.x0 - left, rect.y0 - top, rect.x1 + right, rect.y1 + bottom
    )
    return clamp_rect(expanded, page_rect)


def expand_inferred_rect(
    rect: pymupdf.Rect, page_rect: pymupdf.Rect, preset: str
) -> pymupdf.Rect:
    left, top, right, bottom = INFERRED_MARGINS.get(preset, INFERRED_MARGINS["generic"])
    expanded = pymupdf.Rect(
        rect.x0 - left, rect.y0 - top, rect.x1 + right, rect.y1 + bottom
    )
    return clamp_rect(expanded, page_rect)


def parse_rect_arg(rect_text: str) -> pymupdf.Rect:
    try:
        x0, y0, x1, y1 = [float(part.strip()) for part in rect_text.split(",")]
    except ValueError as exc:
        raise ValueError("rect 必须是 x0,y0,x1,y1") from exc
    rect = pymupdf.Rect(x0, y0, x1, y1)
    if rect.is_empty or rect.is_infinite:
        raise ValueError("rect 非法或为空")
    return rect


def pdftotext_exists() -> bool:
    return shutil.which("pdftotext") is not None


def extract_text_with_pdftotext(pdf_path: Path) -> str:
    result = subprocess.run(
        ["pdftotext", "-layout", str(pdf_path), "-"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def extract_text_with_pymupdf(pdf_path: Path) -> str:
    with pymupdf.open(pdf_path) as doc:
        chunks = []
        for page in doc:
            chunks.append(page.get_text("text"))
        return "\n\n".join(chunks).strip()


def extract_text(pdf_path: Path, engine: str = "auto") -> tuple[str, str]:
    if engine not in {"auto", "pdftotext", "pymupdf"}:
        raise ValueError(f"不支持的 engine: {engine}")
    if engine in {"auto", "pdftotext"} and pdftotext_exists():
        try:
            return extract_text_with_pdftotext(pdf_path), "pdftotext"
        except subprocess.SubprocessError:
            if engine == "pdftotext":
                raise
    return extract_text_with_pymupdf(pdf_path), "pymupdf"


def line_hits_from_words(page: pymupdf.Page, query: str) -> list[pymupdf.Rect]:
    query_tokens = [
        normalize_token(token) for token in query.split() if normalize_token(token)
    ]
    if not query_tokens:
        return []
    grouped: dict[tuple[int, int], list[tuple[float, float, float, float, str]]] = {}
    raw_words = cast(
        list[tuple[float, float, float, float, str, int, int, int]],
        page.get_text("words"),
    )
    for x0, y0, x1, y1, word, block_no, line_no, _word_no in raw_words:
        grouped.setdefault((int(block_no), int(line_no)), []).append(
            (float(x0), float(y0), float(x1), float(y1), str(word))
        )
    hits: list[pymupdf.Rect] = []
    for key in sorted(grouped):
        words = sorted(grouped[key], key=lambda item: item[0])
        normalized = [normalize_token(item[4]) for item in words]
        for start in range(0, max(0, len(words) - len(query_tokens) + 1)):
            window = normalized[start : start + len(query_tokens)]
            if window == query_tokens:
                slice_words = words[start : start + len(query_tokens)]
                x0 = min(item[0] for item in slice_words)
                y0 = min(item[1] for item in slice_words)
                x1 = max(item[2] for item in slice_words)
                y1 = max(item[3] for item in slice_words)
                hits.append(pymupdf.Rect(x0, y0, x1, y1))
    return hits


def search_page_pdf(page: pymupdf.Page, query: str) -> list[pymupdf.Rect]:
    hits = page.search_for(query)
    if hits:
        return hits
    return line_hits_from_words(page, query)


def search_page(
    page: pymupdf.Page, query: str, mode: str = "auto"
) -> list[pymupdf.Rect]:
    if mode not in {"auto", "pdf", "ocr"}:
        raise ValueError(f"不支持的 mode: {mode}")
    if mode in {"auto", "pdf"}:
        hits = search_page_pdf(page, query)
        if hits or mode == "pdf":
            return hits
    if mode == "ocr":
        return ocr_hits_from_lines(page, query)
    if ocr_available():
        return ocr_hits_from_lines(page, query)
    return []


def int_to_roman(value: int) -> str:
    numerals = [
        (1000, "M"),
        (900, "CM"),
        (500, "D"),
        (400, "CD"),
        (100, "C"),
        (90, "XC"),
        (50, "L"),
        (40, "XL"),
        (10, "X"),
        (9, "IX"),
        (5, "V"),
        (4, "IV"),
        (1, "I"),
    ]
    result: list[str] = []
    remaining = value
    for number, token in numerals:
        while remaining >= number:
            result.append(token)
            remaining -= number
    return "".join(result)


def query_variants(query: str) -> list[str]:
    variants: list[str] = []
    seen: set[str] = set()

    def add(value: str) -> None:
        cleaned = value.strip()
        if not cleaned or cleaned in seen:
            return
        seen.add(cleaned)
        variants.append(cleaned)

    add(query)

    match = re.match(
        r"^(Figure|Fig\.|TABLE|Table|Tab\.)\s+([A-Za-z0-9]+)$", query.strip()
    )
    if not match:
        return variants

    prefix = match.group(1)
    index_token = match.group(2)
    normalized_prefix = "figure" if prefix.lower().startswith("fig") else "table"
    arabic_token = index_token
    roman_token: str | None = None

    if index_token.isdigit():
        roman_token = int_to_roman(int(index_token))
    else:
        roman_candidate = index_token.upper()
        if re.fullmatch(r"[IVXLCDM]+", roman_candidate):
            roman_token = roman_candidate

    if normalized_prefix == "figure":
        figure_prefixes = ["Figure", "FIGURE", "Fig.", "FIG."]
        for figure_prefix in figure_prefixes:
            add(f"{figure_prefix} {arabic_token}")
            if roman_token is not None:
                add(f"{figure_prefix} {roman_token}")
    else:
        table_prefixes = ["Table", "TABLE", "Tab.", "TAB."]
        for table_prefix in table_prefixes:
            add(f"{table_prefix} {arabic_token}")
            if roman_token is not None:
                add(f"{table_prefix} {roman_token}")

    return variants


def ocr_available() -> bool:
    return (
        PILImage is not None and pytesseract is not None and TesseractOutput is not None
    )


def require_ocr() -> None:
    if not ocr_available():
        raise ValueError("OCR 不可用：请安装 Pillow、pytesseract 与系统 tesseract")


def render_page_pil(page: pymupdf.Page, scale: float = 2.5) -> "PILImageType":
    if PILImage is None:
        raise ValueError("Pillow 不可用")
    pix = page.get_pixmap(
        matrix=pymupdf.Matrix(scale, scale), alpha=False, annots=False
    )
    return PILImage.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")


def ocr_lines_from_page(page: pymupdf.Page, scale: float = 2.5) -> list[OCRLine]:
    require_ocr()
    assert pytesseract is not None
    assert TesseractOutput is not None
    data = cast(
        dict[str, list[object]],
        pytesseract.image_to_data(
            render_page_pil(page, scale=scale), output_type=TesseractOutput.DICT
        ),
    )
    grouped: dict[
        tuple[int, int, int], list[tuple[float, float, float, float, str]]
    ] = {}
    total = len(cast(list[object], data["text"]))
    for index in range(total):
        text = str(cast(list[object], data["text"])[index]).strip()
        if not text:
            continue
        width = int(str(cast(list[object], data["width"])[index]))
        height = int(str(cast(list[object], data["height"])[index]))
        if width <= 0 or height <= 0:
            continue
        left = float(str(cast(list[object], data["left"])[index])) / scale
        top = float(str(cast(list[object], data["top"])[index])) / scale
        right = left + width / scale
        bottom = top + height / scale
        block_num = int(str(cast(list[object], data["block_num"])[index]))
        par_num = int(str(cast(list[object], data["par_num"])[index]))
        line_num = int(str(cast(list[object], data["line_num"])[index]))
        grouped.setdefault((block_num, par_num, line_num), []).append(
            (left, top, right, bottom, text)
        )

    lines: list[OCRLine] = []
    for key in sorted(grouped):
        words = sorted(grouped[key], key=lambda item: item[0])
        lines.append(
            OCRLine(
                rect=pymupdf.Rect(
                    min(item[0] for item in words),
                    min(item[1] for item in words),
                    max(item[2] for item in words),
                    max(item[3] for item in words),
                ),
                text=" ".join(item[4] for item in words),
            )
        )
    return lines


def ocr_hits_from_lines(
    page: pymupdf.Page, query: str, scale: float = 2.5
) -> list[pymupdf.Rect]:
    variants = [normalize_token(item) for item in query_variants(query)]
    hits: list[pymupdf.Rect] = []
    for line in ocr_lines_from_page(page, scale=scale):
        normalized = normalize_token(line.text)
        if any(variant and variant in normalized for variant in variants):
            hits.append(line.rect)
    return hits


def get_text_blocks(page: pymupdf.Page) -> list[TextBlock]:
    blocks: list[TextBlock] = []
    raw_blocks = cast(
        list[tuple[float, float, float, float, str, int, int]], page.get_text("blocks")
    )
    for x0, y0, x1, y1, text, *_ in raw_blocks:
        cleaned = re.sub(r"\s+", " ", str(text)).strip()
        if not cleaned:
            continue
        blocks.append(
            TextBlock(
                rect=pymupdf.Rect(float(x0), float(y0), float(x1), float(y1)),
                text=cleaned,
            )
        )
    return blocks


def infer_column_band(page: pymupdf.Page, caption_rect: pymupdf.Rect) -> pymupdf.Rect:
    page_mid = (page.rect.x0 + page.rect.x1) / 2.0
    significant_blocks = [
        block.rect
        for block in get_text_blocks(page)
        if block.rect.width >= 40.0 and len(block.text) >= 20
    ]
    left_blocks = [
        rect for rect in significant_blocks if (rect.x0 + rect.x1) / 2.0 < page_mid
    ]
    right_blocks = [
        rect for rect in significant_blocks if (rect.x0 + rect.x1) / 2.0 >= page_mid
    ]

    def build_band(rects: list[pymupdf.Rect]) -> pymupdf.Rect | None:
        union = union_rects(rects)
        if union is None:
            return None
        return clamp_rect(
            pymupdf.Rect(union.x0 - 18.0, page.rect.y0, union.x1 + 18.0, page.rect.y1),
            page.rect,
        )

    caption_width = caption_rect.width
    if caption_width >= page.rect.width * 0.7:
        return page.rect

    left_band = build_band(left_blocks)
    right_band = build_band(right_blocks)
    caption_center = (caption_rect.x0 + caption_rect.x1) / 2.0
    candidate_bands = [band for band in [left_band, right_band] if band is not None]
    for band in candidate_bands:
        if band is not None and band.x0 - 12.0 <= caption_center <= band.x1 + 12.0:
            return band
    if caption_center < page_mid and left_band is not None:
        return left_band
    if caption_center >= page_mid and right_band is not None:
        return right_band
    return page.rect


def overlaps_horizontally(rect: pymupdf.Rect, band: pymupdf.Rect) -> bool:
    overlap = min(rect.x1, band.x1) - max(rect.x0, band.x0)
    if overlap <= 0:
        return False
    center_x = (rect.x0 + rect.x1) / 2.0
    band_margin = 20.0
    if band.x0 - band_margin <= center_x <= band.x1 + band_margin:
        return True
    rect_width = max(1.0, rect.x1 - rect.x0)
    return overlap / rect_width >= 0.45


def select_caption_rect(
    page: pymupdf.Page, query: str, matches: list[pymupdf.Rect]
) -> pymupdf.Rect:
    normalized_queries = [normalize_token(item) for item in query_variants(query)]
    caption_candidates: list[pymupdf.Rect] = []
    for block in get_text_blocks(page):
        normalized_text = normalize_token(block.text)
        if any(
            normalized_text.startswith(normalized_query)
            for normalized_query in normalized_queries
        ):
            caption_candidates.append(block.rect)
    if caption_candidates:
        caption_candidates.sort(key=lambda rect: (rect.y0, rect.x0))
        return caption_candidates[0]
    return matches[0]


def collect_visual_rects(page: pymupdf.Page) -> list[pymupdf.Rect]:
    rects: list[pymupdf.Rect] = []
    page_area = max(1.0, page.rect.width * page.rect.height)

    def is_reasonable_visual_rect(rect: pymupdf.Rect) -> bool:
        if rect.is_empty or rect.width < 4 or rect.height < 4:
            return False
        area_ratio = (rect.width * rect.height) / page_area
        if area_ratio > 0.55:
            return False
        if (
            rect.width >= page.rect.width * 0.92
            and rect.height >= page.rect.height * 0.45
        ):
            return False
        return True

    page_dict = cast(dict[str, object], page.get_text("dict"))
    for block in cast(list[dict[str, object]], page_dict.get("blocks", [])):
        if block.get("type") != 1:
            continue
        bbox = cast(
            tuple[float, float, float, float] | list[float] | None, block.get("bbox")
        )
        if not bbox:
            continue
        rect = pymupdf.Rect(*bbox)
        if is_reasonable_visual_rect(rect):
            rects.append(rect)
    for drawing in page.get_drawings():
        rect = cast(pymupdf.Rect | None, drawing.get("rect"))
        if rect is None:
            continue
        if is_reasonable_visual_rect(rect):
            rects.append(rect)
    return rects


def collect_candidate_rects(
    page: pymupdf.Page, caption_rect: pymupdf.Rect, preset: str
) -> tuple[list[pymupdf.Rect], list[pymupdf.Rect]]:
    max_gap = MAX_VERTICAL_GAP.get(preset, MAX_VERTICAL_GAP["generic"])
    column_band = infer_column_band(page, caption_rect)
    horizontal_band = pymupdf.Rect(
        max(column_band.x0, caption_rect.x0 - 36.0),
        0.0,
        min(column_band.x1, caption_rect.x1 + 36.0),
        page.rect.y1,
    )
    above: list[pymupdf.Rect] = []
    below: list[pymupdf.Rect] = []

    def maybe_add(rect: pymupdf.Rect, *, is_text: bool = False) -> None:
        if rect.is_empty or rect.is_infinite:
            return
        if not overlaps_horizontally(rect, horizontal_band):
            return
        if rect.y1 <= caption_rect.y0:
            gap = caption_rect.y0 - rect.y1
            if gap <= max_gap:
                above.append(rect)
            return
        if rect.y0 >= caption_rect.y1:
            gap = rect.y0 - caption_rect.y1
            if gap <= max_gap / 2.0:
                below.append(rect)
            return
        if is_text and rect.intersects(caption_rect):
            return

    for rect in collect_visual_rects(page):
        maybe_add(rect)

    max_text_length = 80 if preset == "figure" else None
    for block in get_text_blocks(page):
        if normalize_token(block.text).startswith(
            normalize_token("Figure")
        ) or normalize_token(block.text).startswith(normalize_token("Table")):
            if block.rect.intersects(caption_rect):
                continue
        if max_text_length is not None and len(block.text) > max_text_length:
            continue
        maybe_add(block.rect, is_text=True)

    return above, below


def union_rects(rects: list[pymupdf.Rect]) -> pymupdf.Rect | None:
    if not rects:
        return None
    current = pymupdf.Rect(rects[0])
    for rect in rects[1:]:
        current |= rect
    return current


def infer_snapshot_rect(
    page: pymupdf.Page, caption_rect: pymupdf.Rect, preset: str
) -> pymupdf.Rect | None:
    above, below = collect_candidate_rects(page, caption_rect, preset)
    if preset == "table":
        preferred = below if below else above
        fallback = above if preferred is below else below
    else:
        preferred = above if above else below
        fallback = below if preferred is above else above
    chosen = union_rects(preferred) or union_rects(fallback)
    if chosen is None:
        return None
    return clamp_rect(chosen, page.rect)


def score_snapshot_candidate(
    page: pymupdf.Page,
    caption_rect: pymupdf.Rect,
    inferred_rect: pymupdf.Rect | None,
    preset: str,
) -> float:
    score = 0.0
    normalized_caption_width = caption_rect.width / max(1.0, page.rect.width)
    score += min(normalized_caption_width, 1.0) * 80.0
    score -= caption_rect.y0 / max(1.0, page.rect.height) * 12.0
    if inferred_rect is None:
        return score - 200.0
    area_ratio = (inferred_rect.width * inferred_rect.height) / max(
        1.0, page.rect.width * page.rect.height
    )
    score += min(area_ratio, 1.0) * 220.0
    if inferred_rect.y1 <= caption_rect.y0:
        score += 45.0 if preset == "figure" else 10.0
    if inferred_rect.y0 >= caption_rect.y1:
        score += 50.0 if preset == "table" else 8.0
    if preset == "figure" and inferred_rect.height > 80.0:
        score += 25.0
    if preset == "table" and inferred_rect.width > page.rect.width * 0.55:
        score += 35.0
    gap = min(
        abs(caption_rect.y0 - inferred_rect.y1), abs(inferred_rect.y0 - caption_rect.y1)
    )
    score -= min(gap, 200.0) * 0.08
    return score


def choose_snapshot_candidate(
    pdf_page: pymupdf.Page, query: str, preset: str, page_index: int, mode: str = "auto"
) -> SnapshotCandidate | None:
    best_candidate: SnapshotCandidate | None = None
    for variant in query_variants(query):
        matches = search_page(pdf_page, variant, mode=mode)
        if not matches:
            continue
        for match in matches:
            base_rect = select_caption_rect(pdf_page, variant, [match])
            inferred_rect = infer_snapshot_rect(pdf_page, base_rect, preset)
            score = score_snapshot_candidate(pdf_page, base_rect, inferred_rect, preset)
            candidate = SnapshotCandidate(
                page_index=page_index,
                query=variant,
                base_rect=base_rect,
                inferred_rect=inferred_rect,
                score=score,
            )
            if best_candidate is None or candidate.score > best_candidate.score:
                best_candidate = candidate
    return best_candidate


def build_snapshot_query_preview(
    pdf_path: Path,
    query: str,
    preset: str = "generic",
    page: int | None = None,
    mode: str = "auto",
) -> dict[str, object]:
    if preset not in PRESET_MARGINS:
        raise ValueError(f"不支持的 preset: {preset}")
    with pymupdf.open(pdf_path) as doc:
        page_indices = [page - 1] if page is not None else list(range(doc.page_count))
        best_candidate: SnapshotCandidate | None = None
        for page_index in page_indices:
            if page_index < 0 or page_index >= doc.page_count:
                continue
            pdf_page = doc[page_index]
            candidate = choose_snapshot_candidate(
                pdf_page, query, preset, page_index, mode=mode
            )
            if candidate is None:
                continue
            if best_candidate is None or candidate.score > best_candidate.score:
                best_candidate = candidate
        if best_candidate is None:
            raise ValueError(f"未找到 query: {query}")

        pdf_page = doc[best_candidate.page_index]
        clip = (
            expand_inferred_rect(best_candidate.inferred_rect, pdf_page.rect, preset)
            if best_candidate.inferred_rect is not None
            else expand_rect(best_candidate.base_rect, pdf_page.rect, preset)
        )
        preview = best_candidate.to_preview_dict(preset)
        preview["clip"] = rect_to_list(clip)
        preview["snippet"] = build_snippet(pdf_page, best_candidate.base_rect)
        return preview


def snapshot_query_preview(
    pdf_path: Path,
    query: str,
    preset: str = "generic",
    page: int | None = None,
    mode: str = "auto",
) -> dict[str, object]:
    return build_snapshot_query_preview(
        pdf_path, query, preset=preset, page=page, mode=mode
    )


def render_snapshot_preview(
    pdf_path: Path,
    preview: dict[str, object],
    output_path: Path,
    dpi: int = 200,
) -> dict[str, object]:
    clip_values = preview.get("clip")
    clip = (
        pymupdf.Rect(*[float(value) for value in clip_values])
        if isinstance(clip_values, list)
        else None
    )
    if clip is None:
        raise ValueError("preview 缺少可渲染的 clip")
    page_index = preview.get("page_index")
    if not isinstance(page_index, int):
        raise ValueError("preview 缺少合法的 page_index")
    result = render_clip(
        pdf_path,
        page_index,
        output_path,
        dpi=dpi,
        clip=clip,
    )
    result.update({
        "query": preview.get("query"),
        "preset": preview.get("preset"),
        "base_rect": preview.get("base_rect"),
        "inferred_rect": preview.get("inferred_rect"),
        "score": preview.get("score"),
        "snippet": preview.get("snippet"),
    })
    return result


def build_snippet(page: pymupdf.Page, rect: pymupdf.Rect) -> str:
    clip = expand_rect(rect, page.rect, "equation")
    snippet_text = str(page.get_text("text", clip=clip))
    snippet = re.sub(r"\s+", " ", snippet_text).strip()
    return snippet or page.get_textbox(clip).strip() or ""


def find_query(
    pdf_path: Path, query: str, max_results: int = 20, mode: str = "auto"
) -> list[SearchHit]:
    hits: list[SearchHit] = []
    with pymupdf.open(pdf_path) as doc:
        for page_index in range(doc.page_count):
            page = doc.load_page(page_index)
            seen_rects: set[tuple[float, float, float, float]] = set()
            for variant in query_variants(query):
                for rect in search_page(page, variant, mode=mode):
                    rect_values = rect_to_list(rect)
                    rect_key = (
                        rect_values[0],
                        rect_values[1],
                        rect_values[2],
                        rect_values[3],
                    )
                    if rect_key in seen_rects:
                        continue
                    seen_rects.add(rect_key)
                    hits.append(
                        SearchHit(
                            page_index=page_index,
                            page_number=page_index + 1,
                            rect=rect,
                            snippet=build_snippet(page, rect),
                        )
                    )
                    if len(hits) >= max_results:
                        return hits
    return hits


def render_clip(
    pdf_path: Path,
    page_index: int,
    output_path: Path,
    dpi: int = 200,
    clip: pymupdf.Rect | None = None,
) -> dict[str, object]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with pymupdf.open(pdf_path) as doc:
        if page_index < 0 or page_index >= doc.page_count:
            raise ValueError(f"page 越界: {page_index + 1}/{doc.page_count}")
        page = doc[page_index]
        matrix = pymupdf.Matrix(dpi / 72.0, dpi / 72.0)
        pix = page.get_pixmap(matrix=matrix, clip=clip, annots=False)
        pix.save(output_path)
        return {
            "page_index": page_index,
            "page_number": page_index + 1,
            "output_path": str(output_path),
            "dpi": dpi,
            "clip": rect_to_list(clip) if clip else None,
        }


def snapshot_query(
    pdf_path: Path,
    query: str,
    output_path: Path,
    preset: str = "generic",
    page: int | None = None,
    dpi: int = 200,
    mode: str = "auto",
) -> dict[str, object]:
    preview = build_snapshot_query_preview(
        pdf_path, query, preset=preset, page=page, mode=mode
    )
    pdf_page_result = render_snapshot_preview(pdf_path, preview, output_path, dpi=dpi)
    return pdf_page_result


def snapshot_rect(
    pdf_path: Path,
    page: int,
    rect: pymupdf.Rect,
    output_path: Path,
    preset: str = "exact",
    dpi: int = 200,
) -> dict[str, object]:
    if preset not in PRESET_MARGINS:
        raise ValueError(f"不支持的 preset: {preset}")
    with pymupdf.open(pdf_path) as doc:
        page_index = page - 1
        if page_index < 0 or page_index >= doc.page_count:
            raise ValueError(f"page 越界: {page}/{doc.page_count}")
        pdf_page = doc[page_index]
        clip = expand_rect(rect, pdf_page.rect, preset)
        result = render_clip(pdf_path, page_index, output_path, dpi=dpi, clip=clip)
        result.update({"preset": preset, "base_rect": rect_to_list(rect)})
        return result


def probe(pdf_path: Path) -> dict[str, object]:
    with pymupdf.open(pdf_path) as doc:
        raw_metadata = doc.metadata or {}
        metadata = {
            str(key): value for key, value in raw_metadata.items() if value is not None
        }
        return {
            "pdf_path": str(pdf_path),
            "page_count": doc.page_count,
            "metadata": metadata,
        }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PDF 工具层")
    subparsers = parser.add_subparsers(dest="command", required=True)

    probe_parser = subparsers.add_parser("probe", help="输出 PDF 基本信息")
    probe_parser.add_argument("pdf")

    extract_parser = subparsers.add_parser("extract-text", help="抽取 PDF 全文")
    extract_parser.add_argument("pdf")
    extract_parser.add_argument(
        "--engine", choices=["auto", "pdftotext", "pymupdf"], default="auto"
    )
    extract_parser.add_argument("--output")
    extract_parser.add_argument("--json", action="store_true", dest="output_json")

    find_parser = subparsers.add_parser("find", help="查找 query 的页码与矩形")
    find_parser.add_argument("pdf")
    find_parser.add_argument("query")
    find_parser.add_argument("--max-results", type=int, default=20)
    find_parser.add_argument("--mode", choices=["auto", "pdf", "ocr"], default="auto")

    render_parser = subparsers.add_parser("render-page", help="渲染整页 PNG")
    render_parser.add_argument("pdf")
    render_parser.add_argument("--page", type=int, required=True)
    render_parser.add_argument("--output", required=True)
    render_parser.add_argument("--dpi", type=int, default=200)

    snapshot_query_parser = subparsers.add_parser("snapshot-query", help="按查询裁图")
    snapshot_query_parser.add_argument("pdf")
    snapshot_query_parser.add_argument("query")
    snapshot_query_parser.add_argument("--output", required=True)
    snapshot_query_parser.add_argument(
        "--preset", choices=sorted(PRESET_MARGINS), default="generic"
    )
    snapshot_query_parser.add_argument("--page", type=int)
    snapshot_query_parser.add_argument("--dpi", type=int, default=200)
    snapshot_query_parser.add_argument(
        "--mode", choices=["auto", "pdf", "ocr"], default="auto"
    )

    snapshot_query_preview_parser = subparsers.add_parser(
        "snapshot-query-preview", help="按查询返回候选元数据，不渲染 PNG"
    )
    snapshot_query_preview_parser.add_argument("pdf")
    snapshot_query_preview_parser.add_argument("query")
    snapshot_query_preview_parser.add_argument(
        "--preset", choices=sorted(PRESET_MARGINS), default="generic"
    )
    snapshot_query_preview_parser.add_argument("--page", type=int)
    snapshot_query_preview_parser.add_argument(
        "--mode", choices=["auto", "pdf", "ocr"], default="auto"
    )

    snapshot_rect_parser = subparsers.add_parser("snapshot-rect", help="按矩形裁图")
    snapshot_rect_parser.add_argument("pdf")
    snapshot_rect_parser.add_argument("--page", type=int, required=True)
    snapshot_rect_parser.add_argument("--rect", required=True)
    snapshot_rect_parser.add_argument("--output", required=True)
    snapshot_rect_parser.add_argument(
        "--preset", choices=sorted(PRESET_MARGINS), default="exact"
    )
    snapshot_rect_parser.add_argument("--dpi", type=int, default=200)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    pdf_path = Path(args.pdf).resolve()
    if not pdf_path.exists():
        print(
            json.dumps(
                {"status": "error", "message": f"PDF 不存在: {pdf_path}"},
                ensure_ascii=False,
                indent=2,
            )
        )
        raise SystemExit(2)

    try:
        if args.command == "probe":
            print(json.dumps(probe(pdf_path), ensure_ascii=False, indent=2))
            return

        if args.command == "extract-text":
            text, used_engine = extract_text(pdf_path, engine=args.engine)
            if args.output:
                output_path = Path(args.output).resolve()
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(text, encoding="utf-8")
            if args.output_json:
                payload = {
                    "pdf_path": str(pdf_path),
                    "engine": used_engine,
                    "output_path": str(Path(args.output).resolve())
                    if args.output
                    else None,
                    "char_count": len(text),
                }
                print(json.dumps(payload, ensure_ascii=False, indent=2))
            else:
                print(text)
            return

        if args.command == "find":
            hits = [
                hit.to_dict()
                for hit in find_query(
                    pdf_path, args.query, max_results=args.max_results, mode=args.mode
                )
            ]
            print(
                json.dumps(
                    {"pdf_path": str(pdf_path), "query": args.query, "hits": hits},
                    ensure_ascii=False,
                    indent=2,
                )
            )
            return

        if args.command == "render-page":
            result = render_clip(
                pdf_path, args.page - 1, Path(args.output).resolve(), dpi=args.dpi
            )
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return

        if args.command == "snapshot-query":
            result = snapshot_query(
                pdf_path,
                args.query,
                Path(args.output).resolve(),
                preset=args.preset,
                page=args.page,
                dpi=args.dpi,
                mode=args.mode,
            )
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return

        if args.command == "snapshot-query-preview":
            result = snapshot_query_preview(
                pdf_path,
                args.query,
                preset=args.preset,
                page=args.page,
                mode=args.mode,
            )
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return

        if args.command == "snapshot-rect":
            result = snapshot_rect(
                pdf_path,
                args.page,
                parse_rect_arg(args.rect),
                Path(args.output).resolve(),
                preset=args.preset,
                dpi=args.dpi,
            )
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return
    except Exception as exc:  # pragma: no cover - CLI 收口
        print(
            json.dumps(
                {"status": "error", "message": str(exc)}, ensure_ascii=False, indent=2
            )
        )
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
