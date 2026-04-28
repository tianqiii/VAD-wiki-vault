#!/usr/bin/env python3
"""
以 append-only 方式向 wiki/log.md 追加结构化日志条目。

示例：
    python .agents/scripts/write_log.py \
      --log-path wiki/log.md \
      --action ingest \
      --summary "摄入新论文并更新索引" \
      --detail "变更=新增 [[Foo]]；更新 [[index.md]]" \
      --detail "冲突=无"
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

VALID_ACTIONS = ("ingest", "query", "lint", "sync")
DEFAULT_DETAIL_LABEL = "细节"
SHANGHAI_TZ = ZoneInfo("Asia/Shanghai")


@dataclass(frozen=True)
class DetailItem:
    label: str
    content: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="追加写入 wiki/log.md")
    parser.add_argument("--log-path", required=True, help="wiki/log.md 的路径")
    parser.add_argument("--action", required=True, choices=VALID_ACTIONS, help="日志动作类型")
    parser.add_argument("--summary", required=True, help="操作简述")
    parser.add_argument(
        "--detail",
        action="append",
        default=[],
        help="日志细节，格式为 标签=内容；可重复传入多次",
    )
    return parser.parse_args()


def parse_detail(raw: str) -> DetailItem:
    text = raw.strip()
    if not text:
        raise ValueError("--detail 不能为空")

    if "=" not in text:
        return DetailItem(label=DEFAULT_DETAIL_LABEL, content=text)

    label, content = text.split("=", 1)
    label = label.strip() or DEFAULT_DETAIL_LABEL
    content = content.strip()
    if not content:
        raise ValueError(f"--detail 缺少内容: {raw}")
    return DetailItem(label=label, content=content)


def build_entry(action: str, summary: str, details: list[DetailItem]) -> str:
    date_text = datetime.now(SHANGHAI_TZ).strftime("%Y-%m-%d")
    lines = [f"## [{date_text}] {action} | {summary.strip()}"]
    for item in details:
        lines.append(f"- **{item.label}**: {item.content}")
    return "\n".join(lines)


def append_entry(log_path: Path, entry: str) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)

    if log_path.exists():
        existing = log_path.read_text(encoding="utf-8")
        prefix = ""
        if existing and not existing.endswith("\n"):
            prefix = "\n"
        spacer = "\n" if existing.rstrip() else ""
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(prefix)
            handle.write(spacer)
            handle.write(entry)
            handle.write("\n")
        return

    log_path.write_text(f"{entry}\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    summary = args.summary.strip()
    if not summary:
        raise SystemExit("--summary 不能为空")

    try:
        details = [parse_detail(raw) for raw in args.detail]
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    entry = build_entry(args.action, summary, details)
    append_entry(Path(args.log_path), entry)
    print(f"已追加日志: {Path(args.log_path)}")


if __name__ == "__main__":
    main()
