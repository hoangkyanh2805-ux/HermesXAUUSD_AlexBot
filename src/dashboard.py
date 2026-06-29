"""Dashboard Room — terminal summary + state export."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from typing import Any

from src.common import DASHBOARD_DIR, data_path, load_json, save_json
from src.journal import list_entries


def _signals() -> list[dict]:
    data = load_json(data_path("signals.json"), {"signals": []})
    return data.get("signals", [])


def get_summary() -> dict[str, Any]:
    signals = _signals()
    entries = list_entries()

    closed_ids = {e["signal_id"] for e in entries}
    open_signals = [
        s for s in signals
        if s.get("signal_id") not in closed_ids and s.get("status") != "closed"
    ]

    results = Counter(e.get("result", "unknown") for e in entries)
    lot_cats = Counter(e.get("lot_category", "unknown") for e in entries)
    total_pnl = sum(float(e.get("pnl", 0)) for e in entries)

    lessons = [e.get("lesson", "") for e in entries if e.get("lesson")]
    latest_lessons = lessons[-5:]

    last_closed = entries[-1] if entries else None

    return {
        "total_signals": len(signals),
        "open_signals": len(open_signals),
        "closed_signals": len(entries),
        "wins": results.get("win", 0),
        "losses": results.get("loss", 0),
        "breakeven": results.get("breakeven", 0),
        "total_pnl": round(total_pnl, 2),
        "lot_category_summary": dict(lot_cats),
        "latest_lessons": latest_lessons,
        "open_signal_ids": [s.get("signal_id") for s in open_signals],
        "last_closed": last_closed,
        "journal_entries": entries,
    }


def export_state() -> dict[str, Any]:
    """Write dashboard/ib-signals/state.json for HTML view."""
    summary = get_summary()
    state = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "desk": "Hermes XAUUSD IB",
        **summary,
    }
    DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
    save_json(DASHBOARD_DIR / "state.json", state)
    return state


def print_dashboard() -> None:
    export_state()
    s = get_summary()
    width = 50
    print("=" * width)
    print("  IB SIGNAL DASHBOARD - Hermes XAUUSD")
    print("=" * width)
    print(f"  Total signals:     {s['total_signals']}")
    print(f"  Open signals:      {s['open_signals']} {s['open_signal_ids']}")
    print(f"  Closed signals:    {s['closed_signals']}")
    print(f"  Win / Loss / BE:   {s['wins']} / {s['losses']} / {s['breakeven']}")
    print(f"  Total PnL:         {s['total_pnl']}")
    print(f"  Lot categories:    {s['lot_category_summary']}")
    print("-" * width)
    print("  Latest lessons:")
    if s["latest_lessons"]:
        for lesson in s["latest_lessons"]:
            print(f"    - {lesson}")
    else:
        print("    (none yet)")
    print(f"\n  HTML dashboard: dashboard/ib-signals/index.html")
    print("=" * width)
