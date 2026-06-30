"""Spread guard — seed / entry / pending spread rules."""

from __future__ import annotations

from typing import Any

from src.activity_log import log_event
from src.desk_config import load_market_config


def evaluate_spread(
    spread_pts: float,
    *,
    action: str = "seed",
    signal_id: str | None = None,
    has_pending: bool = False,
) -> dict[str, Any]:
    """
    Rules:
    - spread > threshold → High Spread Risk
    - pending + high spread → CANCEL_PENDING or PAUSE_PENDING
    - seed/entry blocked when spread too high
    """
    cfg = load_market_config()
    threshold = float(cfg.get("spread_threshold_pts", 30))
    warning_line = threshold * 0.8
    spread = float(spread_pts)

    result: dict[str, Any] = {
        "spread_pts": spread,
        "threshold": threshold,
        "spread_ok": spread <= threshold,
        "high_spread_risk": spread > threshold,
        "spread_status": "NORMAL",
        "action": "ALLOW",
    }

    if spread > threshold:
        result["spread_status"] = "HIGH_SPREAD_RISK"
        if has_pending or action == "pending":
            result["action"] = "CANCEL_PENDING"
        elif action in ("seed", "entry", "publish"):
            result["action"] = "BLOCK"
        if signal_id:
            log_event(
                "SPREAD_WARNING",
                signal_id=signal_id,
                event_note=f"High spread {spread} > {threshold}",
                spread_value=spread,
                status_after=result["action"],
            )
    elif spread > warning_line:
        result["spread_status"] = "WARNING"
        if has_pending:
            result["action"] = "PAUSE_PENDING"
            if signal_id:
                log_event(
                    "SPREAD_WARNING",
                    signal_id=signal_id,
                    event_note=f"Spread warning {spread} near threshold {threshold}",
                    spread_value=spread,
                    status_after="PAUSE_PENDING",
                )

    return result


def guard_or_block(
    spread_pts: float,
    *,
    action: str,
    signal_id: str,
    has_pending: bool = False,
) -> dict[str, Any]:
    """Return spread guard result; set ok=False when action is BLOCK."""
    guard = evaluate_spread(
        spread_pts,
        action=action,
        signal_id=signal_id,
        has_pending=has_pending,
    )
    guard["ok"] = guard["action"] != "BLOCK"
    if guard["action"] == "CANCEL_PENDING" and signal_id:
        log_event(
            "PENDING_CANCELLED",
            signal_id=signal_id,
            event_note="Spread too high — pending cancelled",
            spread_value=spread_pts,
        )
    return guard
