"""Forward test monitor — notify only (no auto-publish)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.common import data_path, load_json, save_json

FORWARD_TEST_DAYS = 7


def check_forward_test_stale() -> dict[str, Any]:
    """
    Check setups in forward_test for stale paper track.
    Returns notifications for operator — does not auto-promote.
    """
    setups = load_json(data_path("setups.json"), {"setups": {}}).get("setups", {})
    log = load_json(data_path("forward_test.json"), {"entries": []})
    now = datetime.now(timezone.utc)
    notifications: list[str] = []

    for name, info in setups.items():
        if info.get("status") != "forward_test":
            continue
        started = info.get("forward_test_started")
        if not started:
            notifications.append(
                f"Setup '{name}' is forward_test but no start date — set in setups.json"
            )
            continue
        started_dt = datetime.fromisoformat(started.replace("Z", "+00:00"))
        days = (now - started_dt).days
        if days >= FORWARD_TEST_DAYS:
            notifications.append(
                f"Setup '{name}' forward test {days}d — review for live promotion (manual /promote_setup)"
            )
        else:
            notifications.append(
                f"Setup '{name}' forward test day {days}/{FORWARD_TEST_DAYS}"
            )

    result = {
        "ok": True,
        "checked_at": now.isoformat(),
        "notifications": notifications,
        "forward_test_days_required": FORWARD_TEST_DAYS,
    }
    log.setdefault("entries", []).append(
        {"ts": now.isoformat(), "notifications": notifications}
    )
    log["entries"] = log["entries"][-50:]
    save_json(data_path("forward_test.json"), log)
    return result


def start_forward_test(setup_name: str) -> dict[str, Any]:
    store = load_json(data_path("setups.json"), {"setups": {}})
    if setup_name not in store.get("setups", {}):
        return {"ok": False, "error": f"Unknown setup: {setup_name}"}
    entry = store["setups"][setup_name]
    if entry.get("status") != "replay_passed":
        return {"ok": False, "error": "Setup must be replay_passed before forward_test."}
    entry["status"] = "forward_test"
    entry["forward_test_started"] = datetime.now(timezone.utc).isoformat()
    save_json(data_path("setups.json"), store)
    return {"ok": True, "setup_name": setup_name, "status": "forward_test"}
