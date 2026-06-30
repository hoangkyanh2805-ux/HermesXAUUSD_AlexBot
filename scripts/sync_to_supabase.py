#!/usr/bin/env python3
"""Sync local desk JSON to Supabase."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.supabase_sync import build_sync_payloads, sync_all


def main() -> int:
    dry_run = "--dry-run" in sys.argv
    if "--payloads" in sys.argv:
        print(json.dumps(build_sync_payloads(), indent=2, ensure_ascii=False))
        return 0
    result = sync_all(dry_run=dry_run)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
