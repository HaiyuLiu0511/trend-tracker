"""CLI entry point.

Usage (no packaging framework required)::

    PYTHONPATH=src python3 -m daily_briefing \
        --input tests/fixtures/daily_sample.json \
        --out output/daily-report-2026-10-20.html

Exits non-zero on any contract violation or word-limit breach so failures are
never silent.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from .render import render
from .schema import ContractError, WordLimitExceeded


def _default_output(input_path: Path, document) -> Path:
    """Derive the output path from ``meta.run_date`` (decisions.md D4).

    The file name must use the run date, never the data date, so repeated
    runs never overwrite an earlier report.
    """
    run_date = document["meta"]["run_date"]
    return Path("output") / f"daily-report-{run_date}.html"


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="daily_briefing",
        description="Render Daily Briefing V2 five-tab HTML from a JSON contract.",
    )
    parser.add_argument(
        "--input", required=True, help="Path to the briefing JSON document"
    )
    parser.add_argument(
        "--out",
        default=None,
        help="Output HTML path (default: output/daily-report-<run_date>.html)",
    )
    args = parser.parse_args(argv)

    input_path = Path(args.input)
    if not input_path.is_file():
        print(f"error: input file not found: {input_path}", file=sys.stderr)
        return 2

    try:
        document = json.loads(input_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"error: input is not valid JSON: {exc}", file=sys.stderr)
        return 2

    try:
        # The 500-word gate is mandatory and has no bypass switch.
        html = render(document)
    except WordLimitExceeded as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 3
    except ContractError as exc:
        print(f"error: contract violation: {exc}", file=sys.stderr)
        return 4

    out_path = Path(args.out) if args.out else _default_output(input_path, document)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")

    mode = document["meta"]["data_mode"]
    print(f"wrote {out_path}  ({len(html)} bytes, data_mode={mode})")
    if mode == "mock":
        print("note: input declared data_mode=mock — output is DEMONSTRATION data")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
