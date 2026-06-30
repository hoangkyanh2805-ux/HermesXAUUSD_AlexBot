"""Build payloads and sync local data/*.json to Supabase (PostgREST)."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.activity_log import rows_for_sync
from src.common import REPO_ROOT, data_path, load_json, save_json
from src.desk_config import load_market_config
from src.journal import list_entries
from src.spread_audit import list_events

SUPABASE_DIR = REPO_ROOT / "supabase"
ENV_PATH = SUPABASE_DIR / ".env"

_DECISION_TO_EVENT = {
    "APPROVE": "SIGNAL_APPROVED",
    "REJECT": "SIGNAL_REJECTED",
    "WAIT": "SIGNAL_WAITING",
    "REDUCE_RISK": "SIGNAL_WAITING",
}


def load_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    env: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip()
    return env


def get_supabase_config() -> dict[str, str]:
    file_env = load_env_file(ENV_PATH)
    url = os.environ.get("SUPABASE_URL") or file_env.get("SUPABASE_URL", "")
    key = (
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        or os.environ.get("SUPABASE_SERVICE_KEY")
        or file_env.get("SUPABASE_SERVICE_ROLE_KEY")
        or file_env.get("SUPABASE_SERVICE_KEY", "")
    )
    return {"url": url.rstrip("/"), "service_key": key}


def _signal_row(signal: dict[str, Any], audit_by_id: dict[str, dict]) -> dict[str, Any] | None:
    if signal.get("stop_loss") is None:
        return None
    aid = audit_by_id.get(signal.get("signal_id", ""), {})
    ctx = load_json(data_path("market_context.json"), {})
    reasons = aid.get("reasons") or []
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
        "dxy_direction": signal.get("dxy_direction"),
        "us10y_direction": signal.get("us10y_direction"),
        "dxy_context": ctx.get("dxy_context"),
        "us10y_context": ctx.get("us10y_context"),
        "correlation_risk_tag": signal.get("correlation_risk_tag"),
        "spread_log": [
            {"event": e.get("event"), "spread_pts": e.get("spread_pts"), "ts": e.get("ts")}
            for e in list_events()
            if e.get("signal_id") == signal.get("signal_id")
        ],
        "setup_name": signal.get("setup_name"),
        "status": signal.get("status", "draft"),
        "decision": aid.get("decision"),
        "reason": "; ".join(reasons[:5]) if reasons else None,
        "suggested_action": aid.get("suggested_action"),
    }


def _trade_row(entry: dict[str, Any]) -> dict[str, Any]:
    closed = f"{entry.get('date', '1970-01-01')}T12:00:00+00:00"
    return {
        "signal_id": entry["signal_id"],
        "closed_at": closed,
        "pair": entry.get("pair", "XAUUSD"),
        "direction": entry.get("direction"),
        "entry_price": entry.get("entry"),
        "stop_loss": entry.get("stop_loss"),
        "result": entry.get("result"),
        "lot_total": float(entry.get("lots") or 0),
        "client_group": entry.get("lot_category"),
        "risk_tier": entry.get("lot_category"),
        "risk_percent": entry.get("risk_percent_used"),
        "pnl": entry.get("pnl", 0),
        "session": entry.get("session"),
        "setup_type": entry.get("lesson", "")[:80] or None,
    }


def _aggregate_spread_rows(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cfg = load_market_config()
    threshold = float(cfg.get("spread_threshold_pts", 30))
    by_signal: dict[str, dict[str, Any]] = {}
    for ev in events:
        sid = ev.get("signal_id", "")
        if not sid:
            continue
        row = by_signal.setdefault(
            sid,
            {
                "signal_id": sid,
                "spread_threshold": threshold,
                "spread_status": "NORMAL",
            },
        )
        spread = float(ev.get("spread_pts", 0))
        event = ev.get("event", "")
        if event == "seed":
            row["spread_seed"] = spread
        elif event == "entry":
            row["spread_entry"] = spread
        elif event == "close":
            row["spread_close"] = spread
        if spread > threshold:
            row["spread_status"] = "HIGH_SPREAD_RISK"
        elif spread > threshold * 0.8 and row["spread_status"] == "NORMAL":
            row["spread_status"] = "WARNING"
    return list(by_signal.values())


def _activity_rows(audit: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    rows: list[dict[str, Any]] = []
    keys: list[str] = []
    seen = Counter()

    pipeline_rows = rows_for_sync()
    if pipeline_rows:
        for row in pipeline_rows:
            sid = row.get("signal_id", "")
            et = row.get("event_type", "")
            seen[(sid, et)] += 1
            sync_key = f"{sid}:{et}:{seen[(sid, et)]}"
            keys.append(sync_key)
            rows.append(row)
        return rows, keys

    for item in audit.get("decisions", []):
        decision = item.get("decision", "")
        event = _DECISION_TO_EVENT.get(decision)
        if not event:
            continue
        sid = item.get("signal_id", "")
        seen[(sid, decision)] += 1
        sync_key = f"{sid}:{decision}:{seen[(sid, decision)]}"
        keys.append(sync_key)
        rows.append(
            {
                "signal_id": sid,
                "event_type": event,
                "event_note": f"decision={decision} tag={item.get('correlation_risk_tag')}",
                "status_after": decision,
            }
        )
    return rows, keys


def _pending_activity(
    rows: list[dict[str, Any]], keys: list[str]
) -> tuple[list[dict[str, Any]], list[str]]:
    state = load_json(data_path("sync_state.json"), {})
    synced = set(state.get("activity_synced_keys", []))
    fresh_rows: list[dict[str, Any]] = []
    fresh_keys: list[str] = []
    for row, key in zip(rows, keys):
        if key in synced:
            continue
        fresh_rows.append(row)
        fresh_keys.append(key)
    return fresh_rows, fresh_keys


def _risk_row(state: dict[str, Any]) -> dict[str, Any]:
    floating = float(state.get("floating_risk_pct", 0))
    daily_dd = float(state.get("daily_drawdown_pct", 0))
    cfg = load_market_config()
    status = "OK"
    action = "snapshot"
    if floating >= float(cfg.get("floating_risk_cap_pct", 3)):
        status = "FLOATING_RISK_LOCK"
        action = "block_new_trades"
    elif daily_dd >= float(cfg.get("daily_drawdown_cap_pct", 3)):
        status = "DAILY_LOSS_LOCK"
        action = "block_new_trades"
    return {
        "equity": state.get("last_equity"),
        "floating_risk_percent": floating,
        "daily_drawdown_percent": daily_dd,
        "max_allowed_risk_percent": cfg.get("floating_risk_cap_pct"),
        "risk_status": status,
        "action_taken": action,
    }


def build_sync_payloads() -> dict[str, list[dict[str, Any]]]:
    """Read local JSON and return table payloads (no network)."""
    signals_data = load_json(data_path("signals.json"), {"signals": []})
    audit = load_json(data_path("signal_audit.json"), {"decisions": []})
    audit_by_id = {a["signal_id"]: a for a in audit.get("decisions", []) if a.get("signal_id")}

    signal_rows = []
    for s in signals_data.get("signals", []):
        row = _signal_row(s, audit_by_id)
        if row:
            signal_rows.append(row)

    trade_rows = [_trade_row(e) for e in list_entries()]
    spread_rows = _aggregate_spread_rows(list_events())
    activity_rows, activity_keys = _activity_rows(audit)
    risk_state = load_json(data_path("risk_state.json"), {})
    risk_rows = [_risk_row(risk_state)] if risk_state else []

    return {
        "signals": signal_rows,
        "trades": trade_rows,
        "spread_audit": spread_rows,
        "activity_logs": activity_rows,
        "activity_keys": activity_keys,
        "risk_audit": risk_rows,
    }


def _postgrest_upsert(
    *,
    base_url: str,
    service_key: str,
    table: str,
    rows: list[dict[str, Any]],
    on_conflict: str | None = None,
    insert_only: bool = False,
) -> dict[str, Any]:
    if not rows:
        return {"table": table, "upserted": 0, "skipped": True}

    url = f"{base_url}/rest/v1/{table}"
    if on_conflict:
        url += f"?on_conflict={on_conflict}"

    prefer = "return=minimal"
    if not insert_only:
        prefer = f"resolution=merge-duplicates,{prefer}"

    body = json.dumps(rows, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "apikey": service_key,
            "Authorization": f"Bearer {service_key}",
            "Content-Type": "application/json",
            "Prefer": prefer,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return {"table": table, "upserted": len(rows), "status": resp.status}
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")
        return {"table": table, "upserted": 0, "error": f"HTTP {e.code}: {detail[:500]}"}


def sync_all(*, dry_run: bool = False) -> dict[str, Any]:
    """Sync all local desk data to Supabase."""
    cfg = get_supabase_config()
    payloads = build_sync_payloads()
    summary = {
        "dry_run": dry_run,
        "ts": datetime.now(timezone.utc).isoformat(),
        "counts": {
            k: len(v)
            for k, v in payloads.items()
            if k != "activity_keys" and isinstance(v, list)
        },
        "results": [],
    }

    if dry_run:
        summary["ok"] = True
        summary["message"] = "Dry run — payloads built, no network calls."
        return summary

    if not cfg["url"] or not cfg["service_key"]:
        summary["ok"] = False
        summary["error"] = (
            "Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY. "
            "Copy supabase/env.example -> supabase/.env"
        )
        return summary

    activity_rows, new_activity_keys = _pending_activity(
        payloads.get("activity_logs", []),
        payloads.get("activity_keys", []),
    )

    order: list[tuple[str, str | None, bool]] = [
        ("signals", "signal_id", False),
        ("trades", "signal_id", False),
        ("spread_audit", "signal_id", False),
        ("activity_logs", None, True),
        ("risk_audit", None, True),
    ]
    errors: list[str] = []
    for table, conflict, insert_only in order:
        rows = activity_rows if table == "activity_logs" else payloads.get(table, [])
        result = _postgrest_upsert(
            base_url=cfg["url"],
            service_key=cfg["service_key"],
            table=table,
            rows=rows,
            on_conflict=conflict,
            insert_only=insert_only,
        )
        summary["results"].append(result)
        if result.get("error"):
            errors.append(f"{table}: {result['error']}")

    summary["ok"] = not errors
    if errors:
        summary["error"] = "; ".join(errors)
    else:
        state = load_json(data_path("sync_state.json"), {})
        synced = set(state.get("activity_synced_keys", []))
        synced.update(new_activity_keys)
        state["activity_synced_keys"] = sorted(synced)
        state["last_sync"] = summary["ts"]
        state["counts"] = summary["counts"]
        save_json(data_path("sync_state.json"), state)
    return summary


def maybe_sync_after_pipeline() -> None:
    """Optional auto-sync when SYNC_TO_SUPABASE=true."""
    file_env = load_env_file(ENV_PATH)
    flag = (
        os.environ.get("SYNC_TO_SUPABASE", "")
        or file_env.get("SYNC_TO_SUPABASE", "")
    ).lower()
    if flag not in ("1", "true", "yes"):
        return
    try:
        sync_all()
    except Exception:
        pass
