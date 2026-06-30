"""Spread monitor — baseline tracking and spread_diff logging on check_signal."""

from __future__ import annotations

import threading
import time
from datetime import datetime, timezone
from typing import Any

from src.activity_log import log_event
from src.common import data_path, load_json, save_json
from src.desk_config import load_market_config
from src.spread_audit import record_spread

_MONITOR_THREAD: threading.Thread | None = None
_MONITOR_STOP = threading.Event()


def _state() -> dict[str, Any]:
    return load_json(
        data_path("spread_monitor_state.json"),
        {
            "baseline_spread": None,
            "last_spread": None,
            "last_check_ts": None,
            "check_count": 0,
            "background_running": False,
        },
    )


def _save_state(state: dict[str, Any]) -> None:
    save_json(data_path("spread_monitor_state.json"), state)


def _baseline_spread(state: dict[str, Any]) -> float:
    cfg = load_market_config()
    threshold = float(cfg.get("spread_threshold_pts", 30))
    baseline = state.get("baseline_spread")
    if baseline is None:
        return threshold * 0.8
    return float(baseline)


def record_at_check(*, signal_id: str, spread_pts: float, session: str = "") -> dict[str, Any]:
    """Log spread_diff whenever check_signal runs."""
    state = _state()
    baseline = _baseline_spread(state)
    spread = float(spread_pts)
    spread_diff = round(spread - baseline, 2)

    audit_row = record_spread(
        signal_id=signal_id,
        event="check",
        spread_pts=spread,
        session=session,
        note=f"spread_diff={spread_diff:+.2f} vs baseline {baseline}",
    )

    log_event(
        "SPREAD_MONITOR",
        signal_id=signal_id,
        event_note=f"spread_diff={spread_diff:+.2f} pts (baseline={baseline})",
        spread_value=spread,
        payload={
            "spread_diff": spread_diff,
            "baseline_spread": baseline,
            "current_spread": spread,
            "threshold": audit_row.get("threshold"),
        },
    )

    checks = int(state.get("check_count", 0)) + 1
    if state.get("baseline_spread") is None or checks <= 3:
        state["baseline_spread"] = round(
            ((float(state.get("baseline_spread") or spread) * (checks - 1)) + spread) / checks,
            2,
        )
    state["last_spread"] = spread
    state["last_check_ts"] = datetime.now(timezone.utc).isoformat()
    state["check_count"] = checks
    _save_state(state)

    return {
        "signal_id": signal_id,
        "spread_pts": spread,
        "baseline_spread": baseline,
        "spread_diff": spread_diff,
        "spread_ok": audit_row.get("spread_ok", True),
    }


def snapshot() -> dict[str, Any]:
    """Current monitor state (for dashboard / ops)."""
    return _state()


def _background_loop(interval_sec: int) -> None:
    while not _MONITOR_STOP.wait(interval_sec):
        state = _state()
        state["background_tick"] = datetime.now(timezone.utc).isoformat()
        _save_state(state)


def start_background_monitor(*, interval_sec: int = 60) -> dict[str, Any]:
    """Start lightweight background heartbeat (state file only — no broker feed)."""
    global _MONITOR_THREAD
    if _MONITOR_THREAD and _MONITOR_THREAD.is_alive():
        return {"ok": True, "running": True, "message": "spread_monitor already running"}

    _MONITOR_STOP.clear()
    _MONITOR_THREAD = threading.Thread(
        target=_background_loop,
        args=(interval_sec,),
        name="spread_monitor",
        daemon=True,
    )
    _MONITOR_THREAD.start()
    state = _state()
    state["background_running"] = True
    state["background_interval_sec"] = interval_sec
    _save_state(state)
    return {"ok": True, "running": True, "interval_sec": interval_sec}


def stop_background_monitor() -> dict[str, Any]:
    """Stop background monitor thread."""
    global _MONITOR_THREAD
    _MONITOR_STOP.set()
    if _MONITOR_THREAD:
        _MONITOR_THREAD.join(timeout=2)
    _MONITOR_THREAD = None
    state = _state()
    state["background_running"] = False
    _save_state(state)
    return {"ok": True, "running": False}
