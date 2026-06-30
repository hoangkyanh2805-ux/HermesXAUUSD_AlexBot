"""End-to-end sig-test-001 pipeline flow."""

from __future__ import annotations

import os
from typing import Any

from src.activity_log import list_events
from src.common import data_path, load_json, save_json
from src.dashboard import export_state, get_summary
from src.market_context import get_market_context, write_market_context
from src.signal_registry import create_signal
from src.telegram_router import _cmd_calc_lot, _cmd_check_signal, _cmd_publish_signal, _cmd_seed_signal


SIG_TEST_001 = {
    "signal_id": "sig-test-001",
    "pair": "XAUUSD",
    "direction": "buy",
    "entry_low": 2320.0,
    "entry_high": 2322.0,
    "stop_loss": 2314.0,
    "take_profits": [2332.0, 2335.0, 2345.0],
    "session": "london",
    "news_risk": "medium",
    "market_bias": "bullish",
    "dxy_direction": "bearish",
    "us10y_direction": "bearish",
    "equity": 10000.0,
    "risk_tier": "standard",
}


def _reset_risk_state() -> None:
    save_json(
        data_path("risk_state.json"),
        {
            "last_equity": 0.0,
            "floating_risk_pct": 0.0,
            "daily_drawdown_pct": 0.0,
            "open_trades": 0,
            "trades_today": 0,
            "last_reset_date": "",
            "signals_blocked_spread": 0,
        },
    )


def _remove_signal(signal_id: str) -> None:
    data = load_json(data_path("signals.json"), {"signals": []})
    data["signals"] = [s for s in data.get("signals", []) if s.get("signal_id") != signal_id]
    save_json(data_path("signals.json"), data)

    audit = load_json(data_path("signal_audit.json"), {"decisions": []})
    audit["decisions"] = [
        d for d in audit.get("decisions", []) if d.get("signal_id") != signal_id
    ]
    save_json(data_path("signal_audit.json"), audit)

    events = load_json(data_path("activity_events.json"), {"events": []})
    events["events"] = [
        e for e in events.get("events", []) if e.get("signal_id") != signal_id
    ]
    save_json(data_path("activity_events.json"), events)


def run_sig_test_001(*, dry_run: bool = True, reset: bool = True) -> dict[str, Any]:
    """Run full sig-test-001 sequence."""
    if dry_run:
        os.environ["SUPABASE_PIPELINE_DRY_RUN"] = "true"
    else:
        os.environ.pop("SUPABASE_PIPELINE_DRY_RUN", None)

    spec = SIG_TEST_001
    sid = spec["signal_id"]
    steps: list[dict[str, Any]] = []

    if reset:
        _remove_signal(sid)
        _reset_risk_state()

    ctx = get_market_context(
        spread_pts=25.0,
        news_risk=spec["news_risk"],
        dxy_direction=spec["dxy_direction"],
        us10y_direction=spec["us10y_direction"],
        xauusd_price=2321.0,
    )
    write_market_context(ctx)

    created = create_signal(
        signal_id=sid,
        pair=spec["pair"],
        direction=spec["direction"],
        entry_low=spec["entry_low"],
        entry_high=spec["entry_high"],
        stop_loss=spec["stop_loss"],
        take_profits=spec["take_profits"],
        session=spec["session"],
        news_risk=spec["news_risk"],
        market_bias=spec["market_bias"],
        dxy_direction=spec["dxy_direction"],
        us10y_direction=spec["us10y_direction"],
    )
    steps.append({"step": "create_signal", "ok": created.get("ok")})
    if not created.get("ok"):
        return {"ok": False, "steps": steps, "error": created.get("error")}

    checked = _cmd_check_signal([sid])
    steps.append({
        "step": "check_signal",
        "ok": checked.get("ok"),
        "decision": (checked.get("data") or {}).get("decision"),
    })
    if not checked.get("ok"):
        return {"ok": False, "steps": steps, "error": checked.get("error")}

    lot = _cmd_calc_lot([sid, str(spec["equity"]), spec["risk_tier"]])
    steps.append({
        "step": "calc_lot",
        "ok": lot.get("ok"),
        "lot": (lot.get("data") or {}).get("suggested_lot"),
    })
    if not lot.get("ok"):
        return {"ok": False, "steps": steps, "error": lot.get("error")}

    seeded = _cmd_seed_signal([sid])
    steps.append({"step": "seed_signal", "ok": seeded.get("ok")})
    if not seeded.get("ok"):
        return {"ok": False, "steps": steps, "error": seeded.get("error")}

    pub_args = [sid, "yes"]
    if dry_run:
        pub_args.append("dry_run")
    published = _cmd_publish_signal(pub_args)
    steps.append({"step": "publish_signal", "ok": published.get("ok"), "dry_run": dry_run})
    if not published.get("ok"):
        return {"ok": False, "steps": steps, "error": published.get("error")}

    export_state()
    dashboard = get_summary()
    activity_count = len(list_events(sid))
    event_types = {e.get("event_type") for e in list_events(sid)}

    return {
        "ok": True,
        "signal_id": sid,
        "dry_run": dry_run,
        "steps": steps,
        "activity_events": activity_count,
        "event_types": sorted(event_types),
        "volume_metrics": dashboard.get("volume_metrics"),
        "gate_decision": (checked.get("data") or {}).get("decision"),
    }
