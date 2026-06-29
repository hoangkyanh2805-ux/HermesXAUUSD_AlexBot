"""Journal Room — record closed signals."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.common import data_path, load_json, save_json


def _journal() -> dict:
    return load_json(data_path("journal.json"), {"entries": []})


def _find_entry(entries: list, signal_id: str) -> dict | None:
    for e in entries:
        if e.get("signal_id") == signal_id:
            return e
    return None


def append_journal(
    *,
    signal_id: str,
    pair: str,
    direction: str,
    entry: float,
    stop_loss: float,
    take_profits: list[float],
    result: str,
    session: str,
    lot_category: str,
    pnl: float,
    mistake: str = "",
    lesson: str = "",
    date: str | None = None,
) -> dict[str, Any]:
    """Append a closed signal to data/journal.json."""
    store = _journal()
    entries = store.get("entries", [])

    if _find_entry(entries, signal_id):
        return {"ok": False, "error": f"Signal {signal_id} already closed in journal."}

    entry_row = {
        "signal_id": signal_id,
        "date": date or datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "pair": pair,
        "direction": direction,
        "entry": entry,
        "stop_loss": stop_loss,
        "take_profits": take_profits,
        "result": result.lower(),
        "session": session,
        "lot_category": lot_category,
        "pnl": pnl,
        "mistake": mistake,
        "lesson": lesson,
    }
    entries.append(entry_row)
    store["entries"] = entries
    save_json(data_path("journal.json"), store)
    return {"ok": True, "entry": entry_row}


def get_entry(signal_id: str) -> dict | None:
    return _find_entry(_journal().get("entries", []), signal_id)


def list_entries() -> list[dict]:
    return _journal().get("entries", [])
