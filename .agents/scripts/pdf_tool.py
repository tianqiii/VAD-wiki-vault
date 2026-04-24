#!/usr/bin/env python3
"""PDF 工具层：抽文本、找锚点、渲染页面、按查询或矩形裁图。"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import cast

import pymupdf


PRESET_MARGINS: dict[str, tuple[float, float, float, float]] = {
    "exact": (0.0, 0.0, 0.0, 0.0),
    "generic": (24.0, 16.0, 24.0, 64.0),
    "figure": (36.0, 32.0, 36.0, 180.0),
    "table": (28.0, 16.0, 28.0, 140.0),
    "equation": (18.0, 12.0, 18.0, 42.0),
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
            "rect": [round(self.rect.x0, 2), round(self.rect.y0, 2), round(self.rect.x1, 2), round(self.rect.y1, 2)],
            "snippet": self.snippet,
        }


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


def expand_rect(rect: pymupdf.Rect, page_rect: pymupdf.Rect, preset: str) -> pymupdf.Rect:
    left, top, right, bottom = PRESET_MARGINS[preset]
    expanded = pymupdf.Rect(rect.x0 - left, rect.y0 - top, rect.x1 + right, rect.y1 + bottom)
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
    query_tokens = [normalize_token(token) for token in query.split() if normalize_token(token)]
    if not query_tokens:
        return []
    grouped: dict[tuple[int, int], list[tuple[float, float, float, float, str]]] = {}
    raw_words = cast(list[tuple[float, float, float, float, str, int, int, int]], page.get_text("words"))
    for x0, y0, x1, y1, word, block_no, line_no, _word_no in raw_words:
        grouped.setdefault((int(block_no), int(line_no)), []).append((float(x0), float(y0), float(x1), float(y1), str(word)))
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


def search_page(page: pymupdf.Page, query: str) -> list[pymupdf.Rect]:
    hits = page.search_for(query)
    if hits:
        return hits
    return line_hits_from_words(page, query)


def build_snippet(page: pymupdf.Page, rect: pymupdf.Rect) -> str:
    clip = expand_rect(rect, page.rect, "equation")
    snippet_text = str(page.get_text("text", clip=clip))
    snippet = re.sub(r"\s+", " ", snippet_text).strip()
    return snippet or page.get_textbox(clip).strip() or ""


def find_query(pdf_path: Path, query: str, max_results: int = 20) -> list[SearchHit]:
    hits: list[SearchHit] = []
    with pymupdf.open(pdf_path) as doc:
        for page_index in range(doc.page_count):
            page = doc.load_page(page_index)
            for rect in search_page(page, query):
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


def render_clip(pdf_path: Path, page_index: int, output_path: Path, dpi: int = 200, clip: pymupdf.Rect | None = None) -> dict[str, object]:
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


def snapshot_query(pdf_path: Path, query: str, output_path: Path, preset: str = "generic", page: int | None = None, dpi: int = 200) -> dict[str, object]:
    if preset not in PRESET_MARGINS:
        raise ValueError(f"不支持的 preset: {preset}")
    with pymupdf.open(pdf_path) as doc:
        page_indices = [page - 1] if page is not None else list(range(doc.page_count))
        for page_index in page_indices:
            if page_index < 0 or page_index >= doc.page_count:
                continue
            pdf_page = doc[page_index]
            matches = search_page(pdf_page, query)
            if not matches:
                continue
            base_rect = matches[0]
            clip = expand_rect(base_rect, pdf_page.rect, preset)
            result = render_clip(pdf_path, page_index, output_path, dpi=dpi, clip=clip)
            result.update({
                "query": query,
                "preset": preset,
                "base_rect": rect_to_list(base_rect),
                "snippet": build_snippet(pdf_page, base_rect),
            })
            return result
    raise ValueError(f"未找到 query: {query}")


def snapshot_rect(pdf_path: Path, page: int, rect: pymupdf.Rect, output_path: Path, preset: str = "exact", dpi: int = 200) -> dict[str, object]:
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
        metadata = {str(key): value for key, value in raw_metadata.items() if value is not None}
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
    extract_parser.add_argument("--engine", choices=["auto", "pdftotext", "pymupdf"], default="auto")
    extract_parser.add_argument("--output")
    extract_parser.add_argument("--json", action="store_true", dest="output_json")

    find_parser = subparsers.add_parser("find", help="查找 query 的页码与矩形")
    find_parser.add_argument("pdf")
    find_parser.add_argument("query")
    find_parser.add_argument("--max-results", type=int, default=20)

    render_parser = subparsers.add_parser("render-page", help="渲染整页 PNG")
    render_parser.add_argument("pdf")
    render_parser.add_argument("--page", type=int, required=True)
    render_parser.add_argument("--output", required=True)
    render_parser.add_argument("--dpi", type=int, default=200)

    snapshot_query_parser = subparsers.add_parser("snapshot-query", help="按查询裁图")
    snapshot_query_parser.add_argument("pdf")
    snapshot_query_parser.add_argument("query")
    snapshot_query_parser.add_argument("--output", required=True)
    snapshot_query_parser.add_argument("--preset", choices=sorted(PRESET_MARGINS), default="generic")
    snapshot_query_parser.add_argument("--page", type=int)
    snapshot_query_parser.add_argument("--dpi", type=int, default=200)

    snapshot_rect_parser = subparsers.add_parser("snapshot-rect", help="按矩形裁图")
    snapshot_rect_parser.add_argument("pdf")
    snapshot_rect_parser.add_argument("--page", type=int, required=True)
    snapshot_rect_parser.add_argument("--rect", required=True)
    snapshot_rect_parser.add_argument("--output", required=True)
    snapshot_rect_parser.add_argument("--preset", choices=sorted(PRESET_MARGINS), default="exact")
    snapshot_rect_parser.add_argument("--dpi", type=int, default=200)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    pdf_path = Path(args.pdf).resolve()
    if not pdf_path.exists():
        print(json.dumps({"status": "error", "message": f"PDF 不存在: {pdf_path}"}, ensure_ascii=False, indent=2))
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
                    "output_path": str(Path(args.output).resolve()) if args.output else None,
                    "char_count": len(text),
                }
                print(json.dumps(payload, ensure_ascii=False, indent=2))
            else:
                print(text)
            return

        if args.command == "find":
            hits = [hit.to_dict() for hit in find_query(pdf_path, args.query, max_results=args.max_results)]
            print(json.dumps({"pdf_path": str(pdf_path), "query": args.query, "hits": hits}, ensure_ascii=False, indent=2))
            return

        if args.command == "render-page":
            result = render_clip(pdf_path, args.page - 1, Path(args.output).resolve(), dpi=args.dpi)
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
        print(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False, indent=2))
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
