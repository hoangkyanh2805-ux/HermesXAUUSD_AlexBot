"""AI Brain Room — learn from journal data only."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any

from src.common import data_path, save_json
from src.journal import list_entries

MIN_ENTRIES = 3


def _empty_insights() -> dict[str, Any]:
    return {
        "best_session": None,
        "worst_session": None,
        "repeated_mistake": None,
        "best_setup_note": None,
        "rule_improvement_suggestion": None,
        "not_enough_data": True,
    }


def summarize() -> dict[str, Any]:
    """Read journal and produce lesson summary. Never invent performance."""
    entries = list_entries()

    if len(entries) < MIN_ENTRIES:
        insights = _empty_insights()
        insights["rule_improvement_suggestion"] = (
            f"Not enough data ({len(entries)}/{MIN_ENTRIES} closed signals). "
            "Continue journaling before trusting session/setup patterns."
        )
        payload = {
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "insights": insights,
            "source": "journal_only",
            "entry_count": len(entries),
        }
        save_json(data_path("ai_brain.json"), payload)
        return payload

    session_pnl: dict[str, list[float]] = defaultdict(list)
    session_wins: Counter = Counter()
    session_losses: Counter = Counter()
    mistakes: Counter = Counter()
    wins_by_setup: Counter = Counter()

    for e in entries:
        sess = e.get("session", "unknown")
        pnl = float(e.get("pnl", 0))
        session_pnl[sess].append(pnl)
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

    insights = {
        "best_session": best_session,
        "worst_session": worst_session,
        "repeated_mistake": repeated_mistake,
        "best_setup_note": best_setup_note,
        "rule_improvement_suggestion": rule_suggestion,
        "not_enough_data": False,
    }

    payload = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "insights": insights,
        "source": "journal_only",
        "entry_count": len(entries),
    }
    save_json(data_path("ai_brain.json"), payload)
    return payload


def print_brain() -> None:
    data = summarize()
    ins = data["insights"]
    print("=" * 50)
    print("  XAUUSD AI BRAIN (journal only)")
    print("=" * 50)
    if ins.get("not_enough_data"):
        print(f"  {ins['rule_improvement_suggestion']}")
    else:
        print(f"  Best session:      {ins['best_session']}")
        print(f"  Worst session:     {ins['worst_session']}")
        print(f"  Repeated mistake:  {ins['repeated_mistake'] or 'none noted'}")
        print(f"  Best setup note:   {ins['best_setup_note'] or 'n/a'}")
        print(f"  Suggestion:        {ins['rule_improvement_suggestion']}")
    print("=" * 50)
