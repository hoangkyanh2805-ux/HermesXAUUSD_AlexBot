"""Correlation risk payload for signals + activity logs."""

from __future__ import annotations

from typing import Any


def build_correlation_data(
    *,
    signal_direction: str,
    gate_result: dict[str, Any],
    market_ctx: dict[str, Any],
    market_conditions: dict[str, Any] | None = None,
) -> dict[str, Any]:
    tag = gate_result.get("correlation_risk_tag") or "none"
    reasons = gate_result.get("correlation_reasons") or []
    dxy = market_ctx.get("dxy_direction", "neutral")
    us10y = market_ctx.get("us10y_direction", "neutral")
    d = signal_direction.lower()
    mc = market_conditions or {}

    conflict = tag in ("high", "medium") or bool(mc.get("warnings"))
    if not conflict and reasons:
        conflict = any("conflicts" in r.lower() or "risk high" in r.lower() for r in reasons)

    return {
        "tag": tag,
        "signal_direction": d,
        "dxy_direction": dxy,
        "us10y_direction": us10y,
        "conflict": conflict,
        "decision": gate_result.get("decision"),
        "reasons": reasons,
        "warnings": mc.get("warnings", []),
        "condition_score": mc.get("score"),
        "risk_level": mc.get("risk_level"),
        "source": market_ctx.get("source", "mock"),
        "fetched_at": market_ctx.get("ts"),
        "dxy_context": market_ctx.get("dxy_context"),
        "us10y_context": market_ctx.get("us10y_context"),
    }


def correlation_warning_note(correlation_data: dict[str, Any]) -> str:
    if not correlation_data.get("conflict"):
        return ""
    d = correlation_data.get("signal_direction", "").upper()
    return (
        f"Correlation Risk: DXY/US10Y may conflict with XAUUSD {d} "
        f"(tag={correlation_data.get('tag')})"
    )
