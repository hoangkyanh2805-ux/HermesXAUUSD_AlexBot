"""Per-step Supabase writer — upsert signal rows and insert activity events."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any

from src.activity_log import list_events as list_activity_events
from src.common import data_path, load_json
from src.desk_config import load_market_config
from src.spread_audit import list_events as list_spread_events
from src.supabase_sync import _aggregate_spread_rows, _postgrest_upsert, get_supabase_config


def _load_signal(signal_id: str) -> dict[str, Any] | None:
    data = load_json(data_path("signals.json"), {"signals": []})
    for s in data.get("signals", []):
        if s.get("signal_id") == signal_id:
            return s
    return None


def _latest_gate(signal_id: str) -> dict[str, Any]:
    audit = load_json(data_path("signal_audit.json"), {"decisions": []})
    for item in reversed(audit.get("decisions", [])):
        if item.get("signal_id") == signal_id:
            return item
    return {}


def _signal_row(signal: dict[str, Any]) -> dict[str, Any]:
    gate = _latest_gate(signal.get("signal_id", ""))
    ctx = load_json(data_path("market_context.json"), {})
    spread_events = [
        e for e in list_spread_events(signal.get("signal_id"))
    ]
    spread_log = [
        {
            "event": e.get("event"),
            "spread_pts": e.get("spread_pts"),
            "ts": e.get("ts"),
        }
        for e in spread_events
    ]
    reasons = gate.get("reasons") or []
    return {
        "signal_id": signal["signal_id"],
        "pair": signal.get("pair", "XAUUSD"),
        "direction": signal.get("direction", "buy"),
        "entry_low": signal.get("entry_low"),
        "entry_high": signal.get("entry_high"),
        "stop_loss": signal.get("stop_loss"),
        "take_profits": signal.get("take_profits", []),
        "session": signal.get("session"),
        "market_bias": signal.get("market_bias"),
        "news_risk": signal.get("news_risk"),
        "dxy_direction": signal.get("dxy_direction") or ctx.get("dxy_direction"),
        "us10y_direction": signal.get("us10y_direction") or ctx.get("us10y_direction"),
        "dxy_context": ctx.get("dxy_context") or {"direction": ctx.get("dxy_direction"), "source": ctx.get("source", "mock")},
        "us10y_context": ctx.get("us10y_context") or {"direction": ctx.get("us10y_direction"), "source": ctx.get("source", "mock")},
        "correlation_risk_tag": signal.get("correlation_risk_tag"),
        "spread_log": spread_log,
        "setup_name": signal.get("setup_name"),
        "status": signal.get("status", "draft"),
        "decision": gate.get("decision"),
        "reason": "; ".join(reasons[:5]) if reasons else None,
        "suggested_action": gate.get("suggested_action"),
    }


def _activity_rows_for_signal(signal_id: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for ev in list_activity_events(signal_id):
        row: dict[str, Any] = {
            "signal_id": ev.get("signal_id"),
            "event_type": ev.get("event_type"),
            "event_note": ev.get("event_note"),
            "status_before": ev.get("status_before"),
            "status_after": ev.get("status_after"),
        }
        if ev.get("spread_value") is not None:
            row["spread_value"] = ev["spread_value"]
        if ev.get("payload"):
            row["payload"] = ev["payload"]
        rows.append(row)
    return rows


def _spread_row(signal_id: str) -> dict[str, Any] | None:
    events = [e for e in list_spread_events() if e.get("signal_id") == signal_id]
    if not events:
        return None
    rows = _aggregate_spread_rows(events)
    return rows[0] if rows else None


def build_step_payloads(signal_id: str, step: str) -> dict[str, Any]:
    signal = _load_signal(signal_id)
    if not signal:
        return {"error": f"Signal not found: {signal_id}"}

    payloads: dict[str, Any] = {
        "step": step,
        "signal_id": signal_id,
        "ts": datetime.now(timezone.utc).isoformat(),
        "signals": [_signal_row(signal)],
    }

    activity = _activity_rows_for_signal(signal_id)
    if activity:
        payloads["activity_logs"] = activity[-3:]

    spread = _spread_row(signal_id)
    if spread:
        payloads["spread_audit"] = [spread]

    return payloads


def write_pipeline_step(
    step: str,
    signal_id: str,
    *,
    dry_run: bool | None = None,
) -> dict[str, Any]:
    """
    Sync one pipeline step to Supabase.
    dry_run=True prints payloads; False requires credentials.
    """
    if dry_run is None:
        dry_run = os.environ.get("SUPABASE_PIPELINE_DRY_RUN", "").lower() in (
            "1",
            "true",
            "yes",
        )

    payloads = build_step_payloads(signal_id, step)
    if payloads.get("error"):
        return {"ok": False, "error": payloads["error"]}

    summary: dict[str, Any] = {
        "ok": True,
        "step": step,
        "signal_id": signal_id,
        "dry_run": dry_run,
        "payloads": payloads,
    }

    if dry_run:
        summary["message"] = "Dry run — payloads built, no network calls."
        print(json.dumps(payloads, indent=2, ensure_ascii=False))
        return summary

    cfg = get_supabase_config()
    if not cfg["url"] or not cfg["service_key"]:
        summary["skipped"] = True
        summary["message"] = "No Supabase credentials — step sync skipped."
        return summary

    results: list[dict[str, Any]] = []
    errors: list[str] = []

    for table, conflict, insert_only in (
        ("signals", "signal_id", False),
        ("spread_audit", "signal_id", False),
        ("activity_logs", None, True),
    ):
        rows = payloads.get(table, [])
        if not rows:
            continue
        result = _postgrest_upsert(
            base_url=cfg["url"],
            service_key=cfg["service_key"],
            table=table,
            rows=rows,
            on_conflict=conflict,
            insert_only=insert_only,
        )
        results.append(result)
        if result.get("error"):
            errors.append(f"{table}: {result['error']}")

    summary["results"] = results
    if errors:
        summary["ok"] = False
        summary["error"] = "; ".join(errors)
    return summary
