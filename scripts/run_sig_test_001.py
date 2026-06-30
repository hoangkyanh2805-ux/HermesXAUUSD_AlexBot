#!/usr/bin/env python3
"""Run sig-test-001 end-to-end pipeline (dry-run by default)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.pipeline_test_flow import run_sig_test_001


def main() -> int:
    parser = argparse.ArgumentParser(description="Run sig-test-001 pipeline flow")
    parser.add_argument(
        "--live",
        action="store_true",
        help="Write to Supabase if credentials exist (default: dry-run payloads)",
    )
    parser.add_argument(
        "--no-reset",
        action="store_true",
        help="Do not remove existing sig-test-001 rows before run",
    )
    args = parser.parse_args()

    result = run_sig_test_001(dry_run=not args.live, reset=not args.no_reset)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
