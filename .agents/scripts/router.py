#!/usr/bin/env python3
"""
当前仓库 wiki 技能的统一确定性路径引导脚本。

用法：
    python .agents/scripts/router.py ingest
    python .agents/scripts/router.py query "BiSP 和 ABMA 有什么关系？"
    python .agents/scripts/router.py lint
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = SCRIPT_DIR.parents[1]
VALID_SUBCOMMANDS = {"ingest", "query", "lint", "query-with-code", "help"}


def build_result(subcommand: str, args: str) -> dict:
    wiki_dir = WORKSPACE_ROOT / "wiki"
    raw_dir = WORKSPACE_ROOT / "raw"
    index_path = wiki_dir / "index.md"
    log_path = wiki_dir / "log.md"
    result = {
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
