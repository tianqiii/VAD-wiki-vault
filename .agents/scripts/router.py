#!/usr/bin/env python3
"""
当前仓库 wiki 技能的统一确定性路径引导脚本。

用法：
    python .agents/scripts/router.py ingest
    python .agents/scripts/router.py query "BiSP 和 ABMA 有什么关系？"
    python .agents/scripts/router.py query-with-code "STNMamba 和代码仓库如何对齐？"
    python .agents/scripts/router.py paper-deep-reading "raw/02-papers/foo.pdf"
    python .agents/scripts/router.py lint
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


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
VALID_SUBCOMMANDS = {"ingest", "query", "lint", "query-with-code", "paper-deep-reading", "help"}


def build_result(subcommand: str, args: str) -> dict[str, object]:
    wiki_dir = WORKSPACE_ROOT / "wiki"
    raw_dir = WORKSPACE_ROOT / "raw"
    index_path = wiki_dir / "index.md"
    log_path = wiki_dir / "log.md"
    result: dict[str, object] = {
        "status": "ok",
        "subcommand": subcommand,
        "args": args,
        "workspace_root": str(WORKSPACE_ROOT),
        "wiki_dir": str(wiki_dir),
        "raw_dir": str(raw_dir),
        "index_path": str(index_path),
        "log_path": str(log_path),
    }
    missing = [str(p) for p in [wiki_dir, raw_dir, index_path, log_path] if not p.exists()]
    if missing:
        result["status"] = "missing_paths"
        result["missing"] = missing
    return result


def main() -> None:
    subcommand = sys.argv[1].strip().lower() if len(sys.argv) > 1 else "help"
    args = " ".join(sys.argv[2:]).strip()
    if subcommand not in VALID_SUBCOMMANDS:
        print(
            json.dumps(
                {
                    "status": "error",
                    "message": f"未知子命令: {subcommand}",
                    "valid_subcommands": sorted(VALID_SUBCOMMANDS),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        raise SystemExit(2)
    print(json.dumps(build_result(subcommand, args), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
