"""Reporting audit warnings — monitor only, never trigger trades."""

from __future__ import annotations

from typing import Any

from src.spread_audit import summarize_audit
from src.volume_tracker import get_summary


def evaluate_audit_warnings(
    *,
    volume: dict[str, Any] | None = None,
    risk_metrics: dict[str, Any] | None = None,
) -> list[dict[str, str]]:
    """Return dashboard warning flags for operator review."""
    volume = volume or get_summary()
    risk = risk_metrics or {}
    warnings: list[dict[str, str]] = []

    required = volume.get("required_daily_pace")
    actual = volume.get("actual_daily_pace")
    if required and actual and actual < required and volume.get("remaining_to_kpi", 0) > 0:
        warnings.append({
            "status": "BELOW_TARGET_PACE",
            "action": f"Catch-up pace: {required} lots/day (display only — no auto-trade).",
        })

    dd = float(risk.get("daily_drawdown_pct", 0))
    monthly = float(volume.get("monthly_lots", 0))
    if monthly > 0 and dd >= 2.0:
        warnings.append({
            "status": "UNHEALTHY_VOLUME",
            "action": "Volume rising with elevated drawdown — review overtrade risk.",
        })

    spread = summarize_audit()
    if spread.get("spread_warning_count", 0) >= 3:
        warnings.append({
            "status": "BROKER_EXECUTION_RISK",
            "action": "Frequent spread warnings — broker execution audit recommended.",
        })

    trades_today = int(risk.get("trades_today", 0))
    max_day = 5
    if trades_today >= max_day:
        warnings.append({
            "status": "OVERTRADE_RISK",
            "action": "Daily trade limit reached — block new trades until review.",
        })

    return warnings
