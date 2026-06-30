"""Dashboard Room — terminal summary + state export."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from typing import Any

from src.common import DASHBOARD_DIR, data_path, load_json, save_json
from src.journal import list_entries
from src.reporting_audit import evaluate_audit_warnings
from src.safety_locks import refresh_risk_state
from src.supabase_sync import maybe_sync_after_pipeline
from src.spread_audit import summarize_audit
from src.volume_tracker import get_summary as volume_summary


def _signals() -> list[dict]:
    data = load_json(data_path("signals.json"), {"signals": []})
    return data.get("signals", [])


def _gate_stats() -> dict[str, int]:
    audit = load_json(data_path("signal_audit.json"), {"decisions": []})
    counts = Counter(d.get("decision", "unknown") for d in audit.get("decisions", []))
    return {
        "approved": counts.get("APPROVE", 0),
        "rejected": counts.get("REJECT", 0),
        "waiting": counts.get("WAIT", 0) + counts.get("REDUCE_RISK", 0),
    }


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
    risk_state = refresh_risk_state()
    volume = volume_summary()
    spread = summarize_audit()
    gate_stats = _gate_stats()
    audit_warnings = evaluate_audit_warnings(volume=volume, risk_metrics=risk_state)

    lots_closed = [
        float(e.get("lots", 0) or 0) for e in entries if float(e.get("lots", 0) or 0) > 0
    ]
    avg_lot = round(sum(lots_closed) / len(lots_closed), 2) if lots_closed else 0.0

    correlation_high = sum(
        1 for e in entries if e.get("correlation_risk_tag") in ("high", "medium")
    )

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
        "risk_metrics": {
            "equity": risk_state.get("last_equity", 0),
            "floating_risk_pct": risk_state.get("floating_risk_pct", 0),
            "daily_drawdown_pct": risk_state.get("daily_drawdown_pct", 0),
            "open_trades": risk_state.get("open_trades", 0),
            "trades_today": risk_state.get("trades_today", 0),
            "signals_approved": gate_stats["approved"],
            "signals_rejected": gate_stats["rejected"],
            "signals_waiting": gate_stats["waiting"],
        },
        "volume_metrics": {
            **volume,
            "avg_lot_per_signal": avg_lot,
            "signals_needed_at_avg_lot": (
                round(volume["remaining_to_kpi"] / avg_lot, 1)
                if avg_lot > 0 and volume.get("remaining_to_kpi", 0) > 0
                else None
            ),
            "kpi_note": "Display only — does not trigger trades.",
        },
        "spread_audit": spread,
        "audit_warnings": audit_warnings,
        "signal_quality": {
            "high_correlation_outcomes": correlation_high,
        },
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
    maybe_sync_after_pipeline()
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
    print(f"  Monthly lots:      {s['volume_metrics']['monthly_lots']}")
    print(f"  KPI progress:      {s['volume_metrics']['kpi_progress'] * 100:.1f}%")
    print("-" * width)
    print("  Latest lessons:")
    if s["latest_lessons"]:
        for lesson in s["latest_lessons"]:
            print(f"    - {lesson}")
    else:
        print("    (none yet)")
    print(f"\n  HTML dashboard: dashboard/ib-signals/index.html")
    print("=" * width)
