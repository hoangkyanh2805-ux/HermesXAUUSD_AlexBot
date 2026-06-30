"""Local Telegram command router (simulation — no real API)."""

from __future__ import annotations

import shlex
from typing import Any

from src.ai_brain import print_brain, summarize
from src.activity_log import log_event, log_gate_decision
from src.common import data_path, load_json, save_json
from src.correlation import (
    build_correlation_data,
    snapshot_correlation_at_publish,
    snapshot_correlation_at_seed,
)
from src.dashboard import export_state, get_summary, print_dashboard
from src.desk_config import load_market_config
from src.journal import append_journal, get_entry
from src.lot_calculator import calculate_lot, is_recovery_request
from src.market_context import get_market_context, write_market_context
from src.multi_entry import split_entries
from src.publish_gate import publish_signal
from src.safety_locks import evaluate_safety_locks, evaluate_seed_lock, refresh_risk_state
from src.seeding_engine import generate_seeding_dict
from src.signal_gate import check_signal_dict
from src.signal_registry import create_signal
from src.spread_audit import record_spread
from src.spread_guard import guard_or_block
from src.spread_monitor import record_at_check, start_background_monitor
from src.supabase_writer import write_pipeline_step
from src.telegram_notify import send_correlation_alert, send_safety_lock_alert
from src.forward_test import check_forward_test_stale, start_forward_test
from src.signal_replay import get_setup_status, promote_setup, replay_signals
from src.volume_tracker import record_volume

_monitor_started = False
_gate_cache: dict[str, dict] = {}
_lot_cache: dict[str, dict] = {}
_seeding_cache: dict[str, dict] = {}


def _ensure_spread_monitor() -> None:
    global _monitor_started
    if not _monitor_started:
        start_background_monitor(interval_sec=60)
        _monitor_started = True


def clear_pipeline_caches() -> None:
    """Reset in-memory pipeline state (tests / verify runs)."""
    _gate_cache.clear()
    _lot_cache.clear()
    _seeding_cache.clear()


def _load_signal(signal_id: str) -> dict | None:
    data = load_json(data_path("signals.json"), {"signals": []})
    for s in data.get("signals", []):
        if s.get("signal_id") == signal_id:
            return s
    return None


def _stop_loss_distance(signal: dict) -> float:
    entry = (float(signal["entry_low"]) + float(signal["entry_high"])) / 2
    sl = float(signal["stop_loss"])
    return abs(entry - sl)


def _log_signal_audit(signal_id: str, result: dict) -> None:
    audit = load_json(data_path("signal_audit.json"), {"decisions": []})
    audit.setdefault("decisions", []).append(
        {
            "signal_id": signal_id,
            "decision": result.get("decision"),
            "correlation_risk_tag": result.get("correlation_risk_tag"),
            "reasons": result.get("reasons", []),
            "suggested_action": result.get("suggested_action"),
        }
    )
    save_json(data_path("signal_audit.json"), audit)
    log_gate_decision(signal_id, result, correlation_data=result.get("correlation_data"))


def _apply_safety_to_gate(result: dict, safety: dict) -> dict:
    if safety.get("block_new_trades"):
        result["decision"] = "REJECT"
        result["reasons"] = result.get("reasons", []) + safety.get("locks", [])
        result["suggested_action"] = "Safety lock active — resolve before new trades."
    elif safety.get("action_override") and result.get("decision") == "APPROVE":
        result["decision"] = safety["action_override"]
        result["reasons"] = result.get("reasons", []) + safety.get("locks", [])
    result["safety"] = safety
    return result


def parse_command(text: str) -> tuple[str, list[str]]:
    text = text.strip()
    if not text.startswith("/"):
        return "", []
    parts = shlex.split(text)
    cmd = parts[0].lower()
    return cmd, parts[1:]


def route_command(text: str) -> dict[str, Any]:
    cmd, args = parse_command(text)

    if cmd == "/replay":
        return _cmd_replay(args)
    if cmd == "/promote_setup":
        return _cmd_promote_setup(args)
    if cmd == "/forward_test":
        return _cmd_forward_test(args)
    if cmd == "/create_signal":
        return _cmd_create_signal(args)
    if cmd == "/safety_check":
        return _cmd_safety_check(args)
    if cmd == "/split_entries":
        return _cmd_split_entries(args)
    if cmd == "/check_signal":
        return _cmd_check_signal(args)
    if cmd == "/calc_lot":
        return _cmd_calc_lot(args)
    if cmd == "/seed_signal":
        return _cmd_seed_signal(args)
    if cmd == "/publish_signal":
        return _cmd_publish_signal(args)
    if cmd == "/update_signal":
        return _cmd_update_signal(args)
    if cmd == "/close_signal":
        return _cmd_close_signal(args)
    if cmd == "/dashboard":
        export_state()
        return {"ok": True, "data": get_summary()}
    if cmd == "/brain":
        return {"ok": True, "data": summarize()}
    return {"ok": False, "error": f"Unknown command: {cmd or text}"}


def _cmd_create_signal(args: list[str]) -> dict[str, Any]:
    if len(args) < 6:
        return {
            "ok": False,
            "error": (
                "Usage: /create_signal <id> <direction> <entry_low> <entry_high> "
                "<sl> <tp1> [tp2...] [setup_name]"
            ),
        }
    signal_id, direction = args[0], args[1]
    entry_low, entry_high, sl = float(args[2]), float(args[3]), float(args[4])
    setup = ""
    tps: list[float] = []
    for item in args[5:]:
        try:
            tps.append(float(item))
        except ValueError:
            setup = item
    if not tps:
        return {"ok": False, "error": "At least one take_profit required."}
    return create_signal(
        signal_id=signal_id,
        direction=direction,
        entry_low=entry_low,
        entry_high=entry_high,
        stop_loss=sl,
        take_profits=tps,
        setup_name=setup,
    )


def _cmd_safety_check(args: list[str]) -> dict[str, Any]:
    equity = float(args[0]) if args else None
    ctx = get_market_context()
    safety = evaluate_safety_locks(market_ctx=ctx, equity=equity)
    return {"ok": True, "data": safety}


def _cmd_split_entries(args: list[str]) -> dict[str, Any]:
    if len(args) < 2:
        return {"ok": False, "error": "Usage: /split_entries <signal_id> <leg_lot:entry>..."}
    signal_id = args[0]
    lot_info = _lot_cache.get(signal_id)
    if not lot_info or not lot_info.get("allowed"):
        return {"ok": False, "error": "Run /calc_lot first."}
    legs = []
    for spec in args[1:]:
        lot_s, entry_s = spec.split(":")
        legs.append({"lot": float(lot_s), "entry": float(entry_s)})
    return split_entries(
        total_lot=float(lot_info["suggested_lot"]),
        risk_budget_usd=float(lot_info["suggested_risk_amount"]),
        legs=legs,
    )


def _cmd_check_signal(args: list[str]) -> dict[str, Any]:
    if not args:
        return {"ok": False, "error": "Usage: /check_signal <signal_id>"}
    _ensure_spread_monitor()
    signal_id = args[0]
    signal = _load_signal(signal_id)
    if not signal:
        return {"ok": False, "error": f"Signal not found: {signal_id}"}

    ctx = get_market_context(
        news_risk=signal.get("news_risk", "low"),
        spread_pts=signal.get("spread_pts"),
        xauusd_price=signal.get("xauusd_price"),
    )
    write_market_context(ctx)

    spread_pts = float(ctx.get("spread_pts", 28.0))
    monitor = record_at_check(
        signal_id=signal_id,
        spread_pts=spread_pts,
        session=ctx.get("session", ""),
    )

    result = check_signal_dict(signal, market_ctx=ctx)
    safety = evaluate_safety_locks(
        market_ctx=ctx,
        news_risk=signal.get("news_risk", "low"),
    )
    result = _apply_safety_to_gate(result, safety)

    setup = signal.get("setup_name", "")
    if setup:
        status = get_setup_status(setup)
        result["setup_status"] = status
        if status in ("draft", "replay_passed"):
            replay = replay_signals(setup)
            result["replay"] = replay
            if status == "draft" and not replay.get("pass"):
                result["decision"] = "WAIT"
                result["reasons"] = result.get("reasons", []) + [
                    "Replay gate not passed — cannot promote to live."
                ]
                result["suggested_action"] = "Run /replay and fix setup before publish."

    correlation_data = build_correlation_data(
        signal_direction=signal.get("direction", ""),
        gate_result=result,
        market_ctx=ctx,
        market_conditions=result.get("market_conditions"),
    )
    result["correlation_data"] = correlation_data
    result["spread_monitor"] = monitor

    data = load_json(data_path("signals.json"), {"signals": []})
    for s in data.get("signals", []):
        if s.get("signal_id") == signal_id:
            s["correlation_risk_tag"] = result.get("correlation_risk_tag")
            s["correlation_data"] = correlation_data
            s["dxy_direction"] = ctx.get("dxy_direction")
            s["us10y_direction"] = ctx.get("us10y_direction")
    save_json(data_path("signals.json"), data)

    _gate_cache[signal_id] = result
    _log_signal_audit(signal_id, result)
    write_pipeline_step("checked", signal_id)
    return {"ok": True, "data": result}


def _cmd_replay(args: list[str]) -> dict[str, Any]:
    if not args:
        return {"ok": False, "error": "Usage: /replay <setup_name>"}
    setup_name = args[0]
    replay = replay_signals(setup_name)
    if not replay.get("ok"):
        return {"ok": False, "error": replay.get("error", "Replay failed")}
    if replay.get("pass"):
        promote_setup(setup_name, "replay_passed")
        replay["promoted_to"] = "replay_passed"
    return {"ok": True, "data": replay}


def _cmd_promote_setup(args: list[str]) -> dict[str, Any]:
    if len(args) < 2:
        return {"ok": False, "error": "Usage: /promote_setup <setup_name> <status>"}
    setup_name, status = args[0], args[1]
    if status == "live":
        replay = replay_signals(setup_name)
        if not replay.get("pass"):
            return {"ok": False, "error": "Replay must pass before live promotion."}
    result = promote_setup(setup_name, status)
    if not result.get("ok"):
        return result
    return {"ok": True, "data": result}


def _cmd_forward_test(args: list[str]) -> dict[str, Any]:
    if not args:
        return {"ok": True, "data": check_forward_test_stale()}
    if args[0] == "start" and len(args) >= 2:
        result = start_forward_test(args[1])
        if not result.get("ok"):
            return result
        return {"ok": True, "data": result}
    if args[0] == "check":
        return {"ok": True, "data": check_forward_test_stale()}
    return {"ok": False, "error": "Usage: /forward_test check | /forward_test start <setup>"}


def _cmd_calc_lot(args: list[str]) -> dict[str, Any]:
    if len(args) < 3:
        return {
            "ok": False,
            "error": "Usage: /calc_lot <signal_id> <equity> <tier> [recovery_flag]",
        }
    signal_id, equity_s, tier = args[0], args[1], args[2]
    recovery = len(args) > 3 and args[3].lower() in ("true", "1", "recovery", "yes")
    equity = float(equity_s)

    gate = _gate_cache.get(signal_id)
    if not gate:
        return {"ok": False, "error": "Run /check_signal first."}
    if gate.get("decision") == "REJECT":
        return {"ok": False, "error": "S4: Signal rejected — lot calculation blocked."}
    if gate.get("decision") == "WAIT":
        return {"ok": False, "error": "Signal on WAIT — lot calculation blocked."}

    signal = _load_signal(signal_id)
    if not signal:
        return {"ok": False, "error": f"Signal not found: {signal_id}"}

    if is_recovery_request(" ".join(args)):
        recovery = True

    ctx = load_json(data_path("market_context.json"), {})
    safety = evaluate_safety_locks(
        market_ctx=ctx,
        equity=equity,
        news_risk=signal.get("news_risk", "low"),
    )
    cfg = load_market_config()
    risk_mult = 1.0
    if gate.get("decision") == "REDUCE_RISK":
        risk_mult = float(cfg.get("correlation_reduce_risk_multiplier", 0.5))

    lot = calculate_lot(
        account_equity=equity,
        risk_tier=tier,
        stop_loss_distance=_stop_loss_distance(signal),
        recovery_request=recovery,
        risk_multiplier=risk_mult,
        safety_blocked=safety.get("block_new_trades", False),
    )
    _lot_cache[signal_id] = lot
    lot["account_equity"] = equity

    state = refresh_risk_state(equity=equity)
    if lot.get("allowed") and lot.get("suggested_lot"):
        risk_pct = float(lot.get("risk_percent_used", 0))
        state["floating_risk_pct"] = round(
            float(state.get("floating_risk_pct", 0)) + risk_pct, 2
        )
        save_json(data_path("risk_state.json"), state)

    log_event(
        "LOT_CALCULATED",
        signal_id=signal_id,
        event_note=f"lot={lot.get('suggested_lot')}",
        payload=lot,
    )
    write_pipeline_step("lot_calculated", signal_id)
    return {"ok": True, "data": lot}


def _cmd_seed_signal(args: list[str]) -> dict[str, Any]:
    if not args:
        return {"ok": False, "error": "Usage: /seed_signal <signal_id>"}
    signal_id = args[0]
    gate = _gate_cache.get(signal_id)
    if not gate or gate.get("decision") not in ("APPROVE", "REDUCE_RISK"):
        return {"ok": False, "error": "Signal must be APPROVE or REDUCE_RISK before seeding."}

    signal = _load_signal(signal_id)
    if not signal:
        return {"ok": False, "error": f"Signal not found: {signal_id}"}

    ctx = load_json(data_path("market_context.json"), {})
    spread_pts = float(ctx.get("spread_pts", 0))

    equity = float(_lot_cache.get(signal_id, {}).get("account_equity") or 0)
    if equity <= 0:
        equity = float(refresh_risk_state().get("last_equity") or 0)
    seed_lock = evaluate_seed_lock(equity=equity if equity > 0 else None)
    if seed_lock.get("blocked"):
        log_event(
            "SAFETY_LOCK_BLOCKED",
            signal_id=signal_id,
            event_note=seed_lock.get("detail", "seed blocked"),
            status_after="BLOCK_SEED",
            payload=seed_lock,
        )
        send_safety_lock_alert(
            seed_lock.get("detail", "Floating risk cap exceeded"),
            floating_risk_pct=float(seed_lock.get("floating_risk_pct", 0)),
            cap_pct=float(seed_lock.get("cap_pct", 3)),
        )
        write_pipeline_step("seed_blocked", signal_id)
        return {
            "ok": False,
            "error": f"Safety lock — seeding blocked: {seed_lock.get('detail')}",
            "data": seed_lock,
        }

    guard = guard_or_block(spread_pts, action="seed", signal_id=signal_id)
    if not guard.get("ok"):
        return {"ok": False, "error": f"Spread guard — seeding blocked ({guard.get('action')})."}

    correlation_data = snapshot_correlation_at_seed(signal, gate, live=True)
    if correlation_data.get("conflict"):
        send_correlation_alert(signal_id, correlation_data)

    ctx = load_json(data_path("market_context.json"), {})
    spread_pts = float(ctx.get("spread_pts", spread_pts))

    lot = _lot_cache.get(signal_id, {})
    lot_cat = lot.get("suggested_lot_category")
    messages = generate_seeding_dict(signal, lot_category=lot_cat)
    _seeding_cache[signal_id] = messages

    spread_pts = float(ctx.get("spread_pts", 0))
    record_spread(
        signal_id=signal_id,
        event="seed",
        spread_pts=spread_pts,
        session=ctx.get("session", ""),
    )
    data = load_json(data_path("signals.json"), {"signals": []})
    for s in data.get("signals", []):
        if s.get("signal_id") == signal_id:
            s["spread_at_seed"] = spread_pts
    save_json(data_path("signals.json"), data)

    log_event(
        "SIGNAL_SEEDED",
        signal_id=signal_id,
        spread_value=spread_pts,
        payload={"correlation_data": correlation_data},
    )
    write_pipeline_step("seeded", signal_id)
    return {"ok": True, "data": {**messages, "correlation_data": correlation_data}}


def _cmd_publish_signal(args: list[str]) -> dict[str, Any]:
    if len(args) < 2:
        return {
            "ok": False,
            "error": "Usage: /publish_signal <signal_id> <alex_yes|alex_no> [dry_run]",
        }
    signal_id, approval = args[0], args[1].lower()
    dry_run = len(args) > 2 and args[2].lower() in ("dry_run", "dry-run", "dry")
    alex_ok = approval in ("yes", "y", "true", "1", "approve")

    gate = _gate_cache.get(signal_id)
    if not gate or gate.get("decision") not in ("APPROVE", "REDUCE_RISK"):
        return {"ok": False, "error": "Signal must be APPROVE or REDUCE_RISK before publish."}

    ctx = load_json(data_path("market_context.json"), {})
    spread_pts = float(ctx.get("spread_pts", 0))
    guard = guard_or_block(
        spread_pts,
        action="publish",
        signal_id=signal_id,
        has_pending=True,
    )
    if not guard.get("ok"):
        return {"ok": False, "error": f"Spread guard — publish blocked ({guard.get('action')})."}

    signal = _load_signal(signal_id)
    setup = (signal or {}).get("setup_name", "")
    if setup:
        status = get_setup_status(setup)
        if status not in ("replay_passed", "forward_test", "live"):
            return {
                "ok": False,
                "error": f"Setup '{setup}' status is '{status}' — run /replay and /promote_setup first.",
            }

    messages = _seeding_cache.get(signal_id)
    if not messages:
        return {"ok": False, "error": "Run /seed_signal first."}

    result = publish_signal(
        signal_id=signal_id,
        messages=messages,
        alex_approved=alex_ok,
        dry_run=dry_run,
    )
    if not result.get("ok"):
        return result

    correlation_data: dict[str, Any] | None = None
    if not dry_run:
        spread_pts = float(ctx.get("spread_pts", 0))
        correlation_data = snapshot_correlation_at_publish(signal, gate, live=True)
        if correlation_data.get("conflict"):
            send_correlation_alert(signal_id, correlation_data)

        record_spread(signal_id=signal_id, event="entry", spread_pts=spread_pts, session=ctx.get("session", ""))

        data = load_json(data_path("signals.json"), {"signals": []})
        for s in data.get("signals", []):
            if s.get("signal_id") == signal_id:
                s["status"] = "live"
                s["spread_at_entry"] = spread_pts
        save_json(data_path("signals.json"), data)

        state = load_json(data_path("risk_state.json"), {})
        state["trades_today"] = int(state.get("trades_today", 0)) + 1
        save_json(data_path("risk_state.json"), state)

    log_event(
        "SIGNAL_PUBLISHED",
        signal_id=signal_id,
        event_note="dry_run" if dry_run else "published",
        spread_value=spread_pts,
        payload={"correlation_data": correlation_data} if correlation_data else None,
    )
    write_pipeline_step("published", signal_id, dry_run=dry_run)
    export_state()
    if correlation_data:
        result = {**result, "data": {**(result.get("data") or {}), "correlation_data": correlation_data}}
    return result


def _cmd_update_signal(args: list[str]) -> dict[str, Any]:
    if len(args) < 2:
        return {"ok": False, "error": "Usage: /update_signal <signal_id> <status>"}
    signal_id, status = args[0], args[1]
    signal = _load_signal(signal_id)
    if not signal:
        return {"ok": False, "error": f"Signal not found: {signal_id}"}

    data = load_json(data_path("signals.json"), {"signals": []})
    for s in data.get("signals", []):
        if s.get("signal_id") == signal_id:
            s["status"] = status
    save_json(data_path("signals.json"), data)
    export_state()
    return {"ok": True, "data": {"signal_id": signal_id, "status": status}}


def _cmd_close_signal(args: list[str]) -> dict[str, Any]:
    if len(args) < 4:
        return {
            "ok": False,
            "error": "Usage: /close_signal <id> <result> <pnl> <lesson...>",
        }
    signal_id, result, pnl_s = args[0], args[1], args[2]
    lesson = " ".join(args[3:]) if len(args) > 3 else ""
    mistake = "" if result.lower() == "win" else lesson

    if get_entry(signal_id):
        return {"ok": False, "error": f"Signal {signal_id} already in journal."}

    signal = _load_signal(signal_id)
    if not signal:
        return {"ok": False, "error": f"Signal not found: {signal_id}"}

    entry_mid = (float(signal["entry_low"]) + float(signal["entry_high"])) / 2
    lot = _lot_cache.get(signal_id, {})
    lot_cat = lot.get("suggested_lot_category", "unknown")
    lots = float(lot.get("suggested_lot", 0) or 0)

    ctx = load_json(data_path("market_context.json"), {})
    spread_close = float(ctx.get("spread_pts", 0))
    record_spread(
        signal_id=signal_id,
        event="close",
        spread_pts=spread_close,
        session=ctx.get("session", ""),
    )

    row = append_journal(
        signal_id=signal_id,
        pair=signal.get("pair", "XAUUSD"),
        direction=signal.get("direction", ""),
        entry=entry_mid,
        stop_loss=float(signal["stop_loss"]),
        take_profits=[float(x) for x in signal["take_profits"]],
        result=result,
        session=signal.get("session", ""),
        lot_category=lot_cat,
        pnl=float(pnl_s),
        mistake=mistake,
        lesson=lesson,
        lots=lots,
        correlation_risk_tag=signal.get("correlation_risk_tag"),
        spread_at_close=spread_close,
        risk_percent_used=lot.get("risk_percent_used"),
    )
    if not row.get("ok"):
        return {"ok": False, "error": row.get("error")}

    log_event("TRADE_CLOSED", signal_id=signal_id, payload={"result": result, "pnl": float(pnl_s)})
    log_event("JOURNAL_UPDATED", signal_id=signal_id, event_note=lesson[:120] if lesson else "")
    write_pipeline_step("closed", signal_id)

    if lots > 0:
        record_volume(lots=lots)

    data = load_json(data_path("signals.json"), {"signals": []})
    for s in data.get("signals", []):
        if s.get("signal_id") == signal_id:
            s["status"] = "closed"
            s["spread_at_close"] = spread_close
    save_json(data_path("signals.json"), data)

    state = refresh_risk_state()
    if lots > 0 and lot.get("risk_percent_used"):
        state["floating_risk_pct"] = max(
            0.0,
            float(state.get("floating_risk_pct", 0)) - float(lot["risk_percent_used"]),
        )
        save_json(data_path("risk_state.json"), state)

    export_state()
    brain = summarize()
    return {"ok": True, "data": {"journal": row["entry"], "brain": brain["insights"]}}


def _safe_print(text: str) -> None:
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode("ascii", errors="replace").decode("ascii"))


def print_command_result(result: dict[str, Any]) -> None:
    if not result.get("ok"):
        _safe_print(f"ERROR: {result.get('error')}")
        return
    data = result.get("data")
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, dict):
                _safe_print(f"\n[{k}]")
                for sk, sv in v.items():
                    _safe_print(f"  {sk}: {sv}")
            elif isinstance(v, list):
                _safe_print(f"{k}: {', '.join(str(x) for x in v)}")
            else:
                _safe_print(f"{k}: {v}")
    else:
        _safe_print(str(data))
