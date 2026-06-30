"""Signal Room — validate XAUUSD signal quality + correlation filter."""

from __future__ import annotations

from typing import Any

MIN_RR = 1.5
VALID_DECISIONS = ("APPROVE", "WAIT", "REJECT", "REDUCE_RISK")


def _entry_mid(entry_low: float | None, entry_high: float | None) -> float | None:
    if entry_low is None or entry_high is None:
        return None
    return (entry_low + entry_high) / 2


def _compute_rr(
    direction: str,
    entry: float,
    stop_loss: float,
    take_profits: list[float],
) -> float | None:
    if not take_profits:
        return None
    tp = take_profits[0]
    if direction.lower() == "buy":
        risk = entry - stop_loss
        reward = tp - entry
    else:
        risk = stop_loss - entry
        reward = entry - tp
    if risk <= 0 or reward <= 0:
        return None
    return round(reward / risk, 2)


def _bias_conflicts(direction: str, market_bias: str) -> bool:
    d = direction.lower()
    b = market_bias.lower()
    if b in ("neutral", "none", ""):
        return False
    if b == "bullish" and d == "sell":
        return True
    if b == "bearish" and d == "buy":
        return True
    return False


def _correlation_severity(
    direction: str,
    dxy_direction: str,
    us10y_direction: str,
) -> tuple[str, str, list[str]]:
    """Return tag, action, reasons for DXY/US10Y vs XAUUSD direction."""
    d = direction.lower()
    dxy = dxy_direction.lower()
    us10y = us10y_direction.lower()
    reasons: list[str] = []

    if dxy == "neutral" and us10y == "neutral":
        return "none", "APPROVE", reasons

    def _usd_pressure() -> str:
        if dxy == "bullish" or us10y == "bullish":
            if dxy == "bullish" and us10y == "bullish":
                return "high"
            if dxy == "bullish" or us10y == "bullish":
                return "medium"
        if dxy == "bearish" or us10y == "bearish":
            if dxy == "bearish" and us10y == "bearish":
                return "low_aligned"
            return "low_aligned"
        return "none"

    pressure = _usd_pressure()

    if d == "buy":
        if dxy == "bullish":
            reasons.append("DXY bullish conflicts with XAUUSD BUY")
        if us10y == "bullish":
            reasons.append("US10Y bullish conflicts with XAUUSD BUY")
        if pressure == "high":
            return "high", "WAIT", reasons
        if pressure == "medium" or reasons:
            return "medium", "REDUCE_RISK", reasons
        if pressure == "low_aligned":
            reasons.append("DXY/US10Y bearish — tailwind for gold BUY")
            return "aligned", "APPROVE", reasons
    else:
        if dxy == "bearish":
            reasons.append("DXY bearish conflicts with XAUUSD SELL")
        if us10y == "bearish":
            reasons.append("US10Y bearish conflicts with XAUUSD SELL")
        if pressure == "high" or (dxy == "bearish" and us10y == "bearish"):
            return "high", "WAIT", reasons
        if reasons:
            return "medium", "REDUCE_RISK", reasons
        if dxy == "bullish" or us10y == "bullish":
            reasons.append("DXY/US10Y bullish — tailwind for gold SELL")
            return "aligned", "APPROVE", reasons

    return "none", "APPROVE", reasons


def check_signal(
    *,
    pair: str,
    direction: str,
    entry_low: float | None,
    entry_high: float | None,
    stop_loss: float | None,
    take_profits: list[float] | None,
    session: str,
    news_risk: str,
    market_bias: str,
    dxy_direction: str = "neutral",
    us10y_direction: str = "neutral",
) -> dict[str, Any]:
    """Return APPROVE / WAIT / REJECT / REDUCE_RISK with reasons."""
    reasons: list[str] = []
    tps = take_profits or []

    if pair.upper() != "XAUUSD":
        reasons.append(f"Pair {pair} is not supported; desk is XAUUSD only.")

    if stop_loss is None:
        reasons.append("No stop loss defined.")
        return _result("REJECT", reasons, "Fix stop loss before resubmitting.")

    if not tps:
        reasons.append("No take profit defined.")
        return _result("REJECT", reasons, "Add at least one take profit level.")

    entry = _entry_mid(entry_low, entry_high)
    if entry is None:
        reasons.append("Entry range is incomplete.")
        return _result("REJECT", reasons, "Provide entry_low and entry_high.")

    rr = _compute_rr(direction, entry, stop_loss, tps)
    if rr is None:
        reasons.append("Invalid RR geometry (check direction vs SL/TP).")
        return _result("REJECT", reasons, "Correct entry, SL, and TP alignment.")

    if rr < MIN_RR:
        reasons.append(f"RR {rr} is below minimum {MIN_RR}.")
        return _result("REJECT", reasons, "Improve reward-to-risk before approval.")

    if news_risk.lower() in ("high", "elevated"):
        reasons.append(f"News risk is {news_risk}; wait for clearer conditions.")
        decision = "WAIT" if news_risk.lower() == "high" else "REDUCE_RISK"
        return _result(decision, reasons, "Re-check after news window passes.")

    if _bias_conflicts(direction, market_bias):
        reasons.append(
            f"Market bias ({market_bias}) conflicts with {direction} direction."
        )
        return _result("WAIT", reasons, "Wait for bias alignment or revise direction.")

    tag, corr_action, corr_reasons = _correlation_severity(
        direction, dxy_direction, us10y_direction
    )
    reasons.extend(corr_reasons)
    reasons.append(f"RR {rr} meets minimum.")
    reasons.append(f"Session {session} accepted.")
    reasons.append("Basic structure valid.")

    decision = corr_action if corr_action != "APPROVE" else "APPROVE"
    action = (
        "Proceed with reduced size."
        if decision == "REDUCE_RISK"
        else "Proceed to lot calculation and seeding."
        if decision == "APPROVE"
        else "Wait for macro alignment or clearer conditions."
    )
    return _result(
        decision,
        reasons,
        action,
        extra={
            "rr": rr,
            "entry": entry,
            "correlation_risk_tag": tag,
            "correlation_reasons": corr_reasons,
            "correlation_action": corr_action,
        },
    )


def check_signal_dict(signal: dict[str, Any], market_ctx: dict[str, Any] | None = None) -> dict[str, Any]:
    """Check a signal record from data/signals.json."""
    ctx = market_ctx or {}
    result = check_signal(
        pair=signal.get("pair", "XAUUSD"),
        direction=signal.get("direction", ""),
        entry_low=signal.get("entry_low"),
        entry_high=signal.get("entry_high"),
        stop_loss=signal.get("stop_loss"),
        take_profits=signal.get("take_profits"),
        session=signal.get("session", "unknown"),
        news_risk=signal.get("news_risk", ctx.get("news_risk", "low")),
        market_bias=signal.get("market_bias", "neutral"),
        dxy_direction=ctx.get("dxy_direction", signal.get("dxy_direction", "neutral")),
        us10y_direction=ctx.get("us10y_direction", signal.get("us10y_direction", "neutral")),
    )
    result["signal_id"] = signal.get("signal_id")
    return result


def _result(
    decision: str,
    reasons: list[str],
    suggested_action: str,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "decision": decision,
        "reasons": reasons,
        "suggested_action": suggested_action,
    }
    if extra:
        payload.update(extra)
    return payload
