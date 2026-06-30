"""Safety triggers — floating risk, spread, news, daily DD, trade count."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.common import data_path, load_json, save_json
from src.desk_config import load_market_config
from src.journal import list_entries


def _risk_state() -> dict[str, Any]:
    return load_json(
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


def _save_risk_state(state: dict[str, Any]) -> None:
    save_json(data_path("risk_state.json"), state)


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _count_open_trades() -> int:
    data = load_json(data_path("signals.json"), {"signals": []})
    return sum(1 for s in data.get("signals", []) if s.get("status") == "live")


def _daily_pnl() -> float:
    today = _today()
    return sum(
        float(e.get("pnl", 0))
        for e in list_entries()
        if e.get("date") == today
    )


def refresh_risk_state(*, equity: float | None = None) -> dict[str, Any]:
    state = _risk_state()
    if state.get("last_reset_date") != _today():
        state["trades_today"] = 0
        state["daily_drawdown_pct"] = 0.0
        state["last_reset_date"] = _today()
    if equity is not None and equity > 0:
        state["last_equity"] = equity
        pnl = _daily_pnl()
        if pnl < 0:
            state["daily_drawdown_pct"] = round(abs(pnl) / equity * 100, 2)
        else:
            state["daily_drawdown_pct"] = 0.0
    state["open_trades"] = _count_open_trades()
    _save_risk_state(state)
    return state


def evaluate_safety_locks(
    *,
    market_ctx: dict[str, Any],
    equity: float | None = None,
    news_risk: str = "low",
) -> dict[str, Any]:
    """Return lock flags and suggested gate action overrides."""
    cfg = load_market_config()
    state = refresh_risk_state(equity=equity)

    locks: list[str] = []
    action_override: str | None = None
    block_new_trades = False

    spread = float(market_ctx.get("spread_pts", 0))
    threshold = float(market_ctx.get("spread_threshold", cfg["spread_threshold_pts"]))
    if spread > threshold:
        locks.append(f"Spread lock: {spread} > {threshold} pts")
        action_override = "WAIT"

    if news_risk.lower() == "high":
        locks.append("News lock: high-impact news window")
        action_override = action_override or "WAIT"
    elif news_risk.lower() == "elevated" and action_override is None:
        locks.append("News elevated — consider REDUCE_RISK")
        action_override = "REDUCE_RISK"

    eq = float(state.get("last_equity") or equity or 0)
    if eq > 0:
        dd = float(state.get("daily_drawdown_pct", 0))
        if dd >= float(cfg["daily_drawdown_cap_pct"]):
            locks.append(f"Daily loss lock: drawdown {dd}% >= cap")
            block_new_trades = True

    floating = float(state.get("floating_risk_pct", 0))
    if floating >= float(cfg["floating_risk_cap_pct"]):
        locks.append(f"Floating risk lock: {floating}% >= cap")
        block_new_trades = True

    open_trades = int(state.get("open_trades", 0))
    max_day = int(cfg["max_trades_per_day"])
    trades_today = int(state.get("trades_today", 0))
    if trades_today >= max_day:
        locks.append(f"Trade count lock: {trades_today} trades today (max {max_day})")
        block_new_trades = True
    if open_trades >= max_day:
        locks.append(f"Open trade lock: {open_trades} open (max {max_day})")
        block_new_trades = True

    return {
        "locks": locks,
        "block_new_trades": block_new_trades,
        "action_override": action_override,
        "risk_state": state,
        "spread_ok": spread <= threshold,
    }
