"""Seeding Room — natural Telegram message generation."""

from __future__ import annotations

import re
from typing import Any

PROHIBITED = re.compile(
    r"\b(guaranteed|sure win|100%|don't miss|dont miss|last chance|all in|get rich|passive income)\b",
    re.IGNORECASE,
)


def lint_copy(text: str) -> dict[str, Any]:
    matches = PROHIBITED.findall(text)
    return {"pass": len(matches) == 0, "violations": matches}


def _entry_str(entry_low: float, entry_high: float) -> str:
    if entry_low == entry_high:
        return f"{entry_low:.2f}"
    return f"{entry_low:.2f} - {entry_high:.2f}"


def generate_seeding(
    *,
    signal_id: str,
    pair: str,
    direction: str,
    entry_low: float,
    entry_high: float,
    stop_loss: float,
    take_profits: list[float],
    session: str,
    setup_name: str,
    rr: float | None = None,
    news_risk: str = "low",
    lot_category: str | None = None,
) -> dict[str, str]:
    """Generate all seeding message types for a signal."""
    entry = _entry_str(entry_low, entry_high)
    tp = take_profits[0] if take_profits else 0.0
    dir_upper = direction.upper()
    rr_str = f"{rr:.1f}" if rr is not None else "n/a"

    news_note = (
        "High-impact news nearby — extra caution."
        if news_risk.lower() in ("high", "elevated")
        else "No major news conflict flagged for this window."
    )

    lot_note = (
        f"Reference tier: {lot_category} - size for your own account."
        if lot_category
        else "Size for your account; see pinned lot guide."
    )

    messages = {
        "pre_signal_context": (
            f"{session.title()} session — {pair} watching {setup_name.replace('-', ' ')}. "
            f"Volatility normal. {news_note}"
        ),
        "signal_drop": (
            f"[GOLD] {pair} | {setup_name.replace('-', ' ').title()}\n"
            f"DIR: {dir_upper} @ {entry}\n"
            f"SL: {stop_loss:.2f}\n"
            f"TP: {tp:.2f}\n"
            f"RR: 1:{rr_str}"
        ),
        "reason_message": (
            f"Setup: {setup_name.replace('-', ' ')} during {session} session. "
            f"Structure meets desk rules. {lot_note}"
        ),
        "risk_reminder": (
            "Trade at your own risk. Use a stop loss. Past results do not guarantee future outcomes. "
            "Questions - DM."
        ),
        "live_update": (
            f"Signal {signal_id} is live. {dir_upper} {pair} active. "
            "Manage per your plan; consider partials if momentum fades."
        ),
        "tp_hit_update": (
            f"TP reached on {signal_id}. Well done if you followed your plan. "
            "Journal your result and stay disciplined on the next setup."
        ),
        "sl_hit_update": (
            f"SL hit on {signal_id}. Losses are part of trading - do not increase size to recover. "
            "Review the journal note when posted."
        ),
        "result_summary": (
            f"Closed {signal_id} - see journal for full result. "
            "Desk tracks lessons to improve process, not to promise future wins."
        ),
    }

    for key, text in messages.items():
        lint = lint_copy(text)
        if not lint["pass"]:
            messages[key] = "[BLOCKED: hype language detected] " + text

    return messages


def generate_seeding_dict(signal: dict[str, Any], lot_category: str | None = None) -> dict[str, str]:
    entry_low = float(signal["entry_low"])
    entry_high = float(signal["entry_high"])
    entry_mid = (entry_low + entry_high) / 2
    sl = float(signal["stop_loss"])
    tps = [float(x) for x in signal["take_profits"]]
    direction = signal["direction"]
    if direction.lower() == "buy":
        rr = (tps[0] - entry_mid) / (entry_mid - sl) if entry_mid > sl else None
    else:
        rr = (entry_mid - tps[0]) / (sl - entry_mid) if sl > entry_mid else None

    return generate_seeding(
        signal_id=signal.get("signal_id", "unknown"),
        pair=signal.get("pair", "XAUUSD"),
        direction=direction,
        entry_low=entry_low,
        entry_high=entry_high,
        stop_loss=sl,
        take_profits=tps,
        session=signal.get("session", "unknown"),
        setup_name=signal.get("setup_name", "setup"),
        rr=round(rr, 2) if rr else None,
        news_risk=signal.get("news_risk", "low"),
        lot_category=lot_category,
    )
