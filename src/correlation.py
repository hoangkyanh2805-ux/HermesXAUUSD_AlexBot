"""Correlation risk payload for signals + activity logs."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.activity_log import log_event
from src.common import data_path, load_json, save_json
from src.market_conditions import validate_market_conditions
from src.market_context import get_market_context, write_market_context


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
    phase = correlation_data.get("snapshot_phase", "check")
    return (
        f"Correlation Risk ({phase}): DXY/US10Y may conflict with XAUUSD {d} "
        f"(tag={correlation_data.get('tag')})"
    )


def snapshot_correlation_at_phase(
    signal: dict[str, Any],
    gate: dict[str, Any],
    *,
    phase: str,
    live: bool = True,
) -> dict[str, Any]:
    """Refresh live DXY/US10Y and persist correlation_data at seed or publish."""
    ctx = get_market_context(
        live=live,
        news_risk=signal.get("news_risk", "low"),
        spread_pts=signal.get("spread_pts"),
        xauusd_price=signal.get("xauusd_price"),
    )
    write_market_context(ctx)

    mc = validate_market_conditions(
        direction=signal.get("direction", ""),
        dxy_direction=ctx.get("dxy_direction", "neutral"),
        us10y_direction=ctx.get("us10y_direction", "neutral"),
    )
    gate_fresh = {
        **gate,
        "correlation_risk_tag": mc.get("correlation_risk_tag", gate.get("correlation_risk_tag")),
        "correlation_reasons": list(mc.get("warnings", [])) + list(mc.get("notes", [])),
    }
    correlation_data = build_correlation_data(
        signal_direction=signal.get("direction", ""),
        gate_result=gate_fresh,
        market_ctx=ctx,
        market_conditions=mc,
    )
    correlation_data["snapshot_phase"] = phase
    correlation_data["entry_phase"] = phase
    correlation_data["snapshotted_at"] = datetime.now(timezone.utc).isoformat()
    correlation_data["provider"] = ctx.get("provider", ctx.get("source", "mock"))

    signal_id = signal.get("signal_id", "")
    phase_key = f"correlation_snapshotted_at_{phase}"
    data = load_json(data_path("signals.json"), {"signals": []})
    for row in data.get("signals", []):
        if row.get("signal_id") == signal_id:
            row["correlation_data"] = correlation_data
            row["correlation_risk_tag"] = correlation_data.get("tag")
            row["dxy_direction"] = ctx.get("dxy_direction")
            row["us10y_direction"] = ctx.get("us10y_direction")
            row[phase_key] = correlation_data["snapshotted_at"]
    save_json(data_path("signals.json"), data)

    if correlation_data.get("conflict"):
        log_event(
            "CORRELATION_RISK",
            signal_id=signal_id,
            event_note=correlation_warning_note(correlation_data),
            status_after=gate.get("decision"),
            payload=correlation_data,
        )

    return correlation_data


def snapshot_correlation_at_seed(
    signal: dict[str, Any],
    gate: dict[str, Any],
    *,
    live: bool = True,
) -> dict[str, Any]:
    return snapshot_correlation_at_phase(signal, gate, phase="seed", live=live)


def snapshot_correlation_at_publish(
    signal: dict[str, Any],
    gate: dict[str, Any],
    *,
    live: bool = True,
) -> dict[str, Any]:
    """Entry snapshot — refresh macro at publish (vào lệnh)."""
    return snapshot_correlation_at_phase(signal, gate, phase="publish", live=live)
