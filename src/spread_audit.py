"""Spread audit — log spread at seed, entry, and close."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.common import data_path
from src.desk_config import load_market_config


def _audit_path() -> Path:
    p = data_path("spread_audit.jsonl")
    p.parent.mkdir(parents=True, exist_ok=True)
    if not p.exists():
        p.write_text("", encoding="utf-8")
    return p


def record_spread(
    *,
    signal_id: str,
    event: str,
    spread_pts: float,
    session: str = "",
    note: str = "",
) -> dict[str, Any]:
    cfg = load_market_config()
    threshold = float(cfg["spread_threshold_pts"])
    row = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "signal_id": signal_id,
        "event": event,
        "spread_pts": spread_pts,
        "threshold": threshold,
        "spread_ok": spread_pts <= threshold,
        "session": session,
        "note": note,
    }
    with _audit_path().open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


def list_events(signal_id: str | None = None) -> list[dict[str, Any]]:
    path = _audit_path()
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if signal_id is None or row.get("signal_id") == signal_id:
            rows.append(row)
    return rows


def summarize_audit() -> dict[str, Any]:
    rows = list_events()
    if not rows:
        return {
            "count": 0,
            "avg_entry_spread": None,
            "avg_close_spread": None,
            "max_spread": None,
            "spread_warning_count": 0,
            "blocked_spread_count": 0,
        }
    entry_spreads = [r["spread_pts"] for r in rows if r.get("event") == "seed"]
    close_spreads = [r["spread_pts"] for r in rows if r.get("event") == "close"]
    all_spreads = [float(r["spread_pts"]) for r in rows]
    warnings = sum(1 for r in rows if not r.get("spread_ok", True))
    return {
        "count": len(rows),
        "avg_entry_spread": round(sum(entry_spreads) / len(entry_spreads), 2) if entry_spreads else None,
        "avg_close_spread": round(sum(close_spreads) / len(close_spreads), 2) if close_spreads else None,
        "max_spread": max(all_spreads) if all_spreads else None,
        "spread_warning_count": warnings,
        "blocked_spread_count": warnings,
    }
