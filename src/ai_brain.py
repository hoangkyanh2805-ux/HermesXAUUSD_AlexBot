"""AI Brain Room — learn from journal + spread + correlation + volume."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any

from src.common import data_path, save_json
from src.journal import list_entries
from src.spread_audit import summarize_audit
from src.volume_tracker import get_summary as volume_summary

MIN_ENTRIES = 3
MIN_CORRELATION_SAMPLES = 3


def _empty_insights() -> dict[str, Any]:
    return {
        "best_session": None,
        "worst_session": None,
        "repeated_mistake": None,
        "best_setup_note": None,
        "rule_improvement_suggestion": None,
        "high_correlation_loss_rate": None,
        "spread_block_rate": None,
        "avg_entry_spread": None,
        "monthly_volume_lots": None,
        "volume_kpi_progress": None,
        "sustainable_volume_note": None,
        "overtrading_warning": False,
        "not_enough_data": True,
    }


def summarize() -> dict[str, Any]:
    """Read journal and produce lesson summary. Never invent performance."""
    entries = list_entries()
    spread = summarize_audit()
    volume = volume_summary()

    if len(entries) < MIN_ENTRIES:
        insights = _empty_insights()
        insights["avg_entry_spread"] = spread.get("avg_entry_spread")
        insights["monthly_volume_lots"] = volume.get("monthly_lots")
        insights["volume_kpi_progress"] = volume.get("kpi_progress")
        insights["rule_improvement_suggestion"] = (
            f"Not enough data ({len(entries)}/{MIN_ENTRIES} closed signals). "
            "Continue journaling before trusting session/setup patterns."
        )
        payload = {
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "insights": insights,
            "source": "journal_spread_volume",
            "entry_count": len(entries),
        }
        save_json(data_path("ai_brain.json"), payload)
        return payload

    session_pnl: dict[str, list[float]] = defaultdict(list)
    session_wins: Counter = Counter()
    session_losses: Counter = Counter()
    mistakes: Counter = Counter()
    wins_by_setup: Counter = Counter()
    corr_losses = 0
    corr_total = 0

    for e in entries:
        sess = e.get("session", "unknown")
        pnl = float(e.get("pnl", 0))
        session_pnl[sess].append(pnl)
        tag = e.get("correlation_risk_tag")
        if tag in ("high", "medium"):
            corr_total += 1
            if e.get("result") == "loss":
                corr_losses += 1
        if e.get("result") == "win":
            session_wins[sess] += 1
            if e.get("lesson"):
                wins_by_setup[e.get("lesson", "")[:40]] += 1
        elif e.get("result") == "loss":
            session_losses[sess] += 1
        if e.get("mistake"):
            mistakes[e["mistake"]] += 1

    def avg_pnl(sess: str) -> float:
        vals = session_pnl[sess]
        return sum(vals) / len(vals) if vals else 0.0

    sessions = list(session_pnl.keys())
    best_session = max(sessions, key=avg_pnl) if sessions else None
    worst_session = min(sessions, key=avg_pnl) if sessions else None

    repeated_mistake = mistakes.most_common(1)[0][0] if mistakes else None
    best_setup_note = wins_by_setup.most_common(1)[0][0] if wins_by_setup else None

    rule_suggestion = (
        f"Favour {best_session} session setups when conditions match journal winners."
        if best_session
        else "Keep recording lessons per session."
    )
    if worst_session and session_losses[worst_session] > session_wins[worst_session]:
        rule_suggestion += f" Tighten filters during {worst_session} session."

    high_corr_rate = (
        round(corr_losses / corr_total, 2) if corr_total >= MIN_CORRELATION_SAMPLES else None
    )
    spread_warn = spread.get("spread_warning_count", 0)
    spread_total = max(spread.get("count", 1), 1)
    spread_block_rate = round(spread_warn / spread_total, 2) if spread_total else None

    avg_risk = sum(float(e.get("risk_percent_used", 0) or 0) for e in entries) / len(entries)
    overtrade = len(entries) > 10 and avg_risk > 2.0
    sustainable = (
        "Volume tracked separately from risk; no overtrade pattern detected."
        if not overtrade
        else "Review trade frequency — risk% elevated relative to journal size."
    )

    insights = {
        "best_session": best_session,
        "worst_session": worst_session,
        "repeated_mistake": repeated_mistake,
        "best_setup_note": best_setup_note,
        "rule_improvement_suggestion": rule_suggestion,
        "high_correlation_loss_rate": high_corr_rate,
        "spread_block_rate": spread_block_rate,
        "avg_entry_spread": spread.get("avg_entry_spread"),
        "monthly_volume_lots": volume.get("monthly_lots"),
        "volume_kpi_progress": volume.get("kpi_progress"),
        "sustainable_volume_note": sustainable,
        "overtrading_warning": overtrade,
        "not_enough_data": False,
    }

    payload = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "insights": insights,
        "source": "journal_spread_volume",
        "entry_count": len(entries),
    }
    save_json(data_path("ai_brain.json"), payload)
    return payload


def print_brain() -> None:
    data = summarize()
    ins = data["insights"]
    print("=" * 50)
    print("  XAUUSD AI BRAIN (journal + spread + volume)")
    print("=" * 50)
    if ins.get("not_enough_data"):
        print(f"  {ins['rule_improvement_suggestion']}")
    else:
        print(f"  Best session:      {ins['best_session']}")
        print(f"  Worst session:     {ins['worst_session']}")
        print(f"  Repeated mistake:  {ins['repeated_mistake'] or 'none noted'}")
        print(f"  Avg entry spread:  {ins['avg_entry_spread']}")
        print(f"  Monthly volume:    {ins['monthly_volume_lots']} lots")
        print(f"  KPI progress:      {ins['volume_kpi_progress']}")
        print(f"  Suggestion:        {ins['rule_improvement_suggestion']}")
    print("=" * 50)
