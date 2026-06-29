"""Human approval gate before simulated Signal Group publish."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.common import data_path, load_json, save_json


def publish_signal(
    *,
    signal_id: str,
    messages: dict[str, str],
    alex_approved: bool,
    approver: str = "alex",
) -> dict[str, Any]:
    """
    Simulate publish to Signal Group.
    Real Telegram API is NOT called in MVP.
    """
    if not alex_approved:
        return {
            "ok": False,
            "error": "G6: Can publish only after Alex approval (alex_approved=True).",
        }

    log = load_json(data_path("publish_log.json"), {"publishes": []})
    entry = {
        "signal_id": signal_id,
        "ts": datetime.now(timezone.utc).isoformat(),
        "approver": approver,
        "channel": "signal_group_simulated",
        "messages": messages,
    }
    log.setdefault("publishes", []).append(entry)
    save_json(data_path("publish_log.json"), log)

    return {
        "ok": True,
        "data": {
            "signal_id": signal_id,
            "published": True,
            "simulated": True,
            "note": "Logged to data/publish_log.json — no real Telegram call.",
        },
    }
