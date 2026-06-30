"""Activity event trail — local JSON + Supabase sync source."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.common import data_path, load_json, save_json

EVENT_TYPES = (
    "SIGNAL_CREATED",
    "SIGNAL_CHECKED",
    "SIGNAL_APPROVED",
    "SIGNAL_WAITING",
    "SIGNAL_REJECTED",
    "CORRELATION_RISK",
    "LOT_CALCULATED",
    "SIGNAL_SEEDED",
    "SIGNAL_PUBLISHED",
    "SPREAD_WARNING",
    "SPREAD_MONITOR",
    "SAFETY_LOCK_BLOCKED",
    "PENDING_CANCELLED",
    "TRADE_CLOSED",
    "JOURNAL_UPDATED",
)

_DECISION_TO_EVENT = {
    "APPROVE": "SIGNAL_APPROVED",
    "REJECT": "SIGNAL_REJECTED",
    "WAIT": "SIGNAL_WAITING",
    "REDUCE_RISK": "SIGNAL_WAITING",
}


def _store() -> dict[str, Any]:
    return load_json(data_path("activity_events.json"), {"events": []})


def _save(data: dict[str, Any]) -> None:
    save_json(data_path("activity_events.json"), data)


def log_event(
    event_type: str,
    *,
    signal_id: str | None = None,
    event_note: str = "",
    status_before: str | None = None,
    status_after: str | None = None,
    spread_value: float | None = None,
    price: float | None = None,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if event_type not in EVENT_TYPES:
        raise ValueError(f"Unknown event_type: {event_type}")
    row = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "signal_id": signal_id,
        "event_type": event_type,
        "event_note": event_note,
        "status_before": status_before,
        "status_after": status_after,
        "spread_value": spread_value,
        "price": price,
        "payload": payload or {},
    }
    data = _store()
    data.setdefault("events", []).append(row)
    _save(data)
    return row


def log_gate_decision(
    signal_id: str,
    gate_result: dict[str, Any],
    *,
    correlation_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    decision = gate_result.get("decision", "")
    log_event(
        "SIGNAL_CHECKED",
        signal_id=signal_id,
        event_note="; ".join(gate_result.get("reasons", [])[:3]),
        status_after=decision,
        payload={
            "correlation_risk_tag": gate_result.get("correlation_risk_tag"),
            "suggested_action": gate_result.get("suggested_action"),
            "correlation_data": correlation_data,
        },
    )
    if correlation_data and correlation_data.get("conflict"):
        from src.correlation import correlation_warning_note

        log_event(
            "CORRELATION_RISK",
            signal_id=signal_id,
            event_note=correlation_warning_note(correlation_data),
            status_after=decision,
            payload=correlation_data,
        )
    event = _DECISION_TO_EVENT.get(decision)
    if event:
        return log_event(
            event,
            signal_id=signal_id,
            event_note=f"decision={decision}",
            status_after=decision,
            payload={"correlation_risk_tag": gate_result.get("correlation_risk_tag")},
        )
    return {}


def list_events(signal_id: str | None = None) -> list[dict[str, Any]]:
    rows = _store().get("events", [])
    if signal_id is None:
        return list(rows)
    return [r for r in rows if r.get("signal_id") == signal_id]


def rows_for_sync() -> list[dict[str, Any]]:
    """Map local events to activity_logs table rows."""
    out: list[dict[str, Any]] = []
    for ev in list_events():
        row: dict[str, Any] = {
            "signal_id": ev.get("signal_id"),
            "event_type": ev.get("event_type"),
            "event_note": ev.get("event_note"),
            "status_before": ev.get("status_before"),
            "status_after": ev.get("status_after"),
        }
        if ev.get("spread_value") is not None:
            row["spread_value"] = ev["spread_value"]
        if ev.get("price") is not None:
            row["price"] = ev["price"]
        payload = ev.get("payload")
        if payload:
            row["payload"] = payload
        out.append(row)
    return out
