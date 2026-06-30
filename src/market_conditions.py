"""Market condition validation — DXY/US10Y vs XAUUSD direction scoring."""

from __future__ import annotations

from typing import Any


def validate_market_conditions(
    *,
    direction: str,
    dxy_direction: str,
    us10y_direction: str = "neutral",
) -> dict[str, Any]:
    """
    Score macro alignment for XAUUSD entries.

    Rules (brief):
    - Gold SELL + DXY up   → high score (aligned)
    - Gold SELL + DXY down → Risk High warning
    - Gold BUY  + DXY down → high score (aligned)
    - Gold BUY  + DXY up   → Risk High warning
    """
    d = direction.lower()
    dxy = dxy_direction.lower()
    us10y = us10y_direction.lower()
    warnings: list[str] = []
    notes: list[str] = []

    if dxy == "neutral" and us10y == "neutral":
        return {
            "score": 65,
            "risk_level": "low",
            "correlation_risk_tag": "none",
            "warnings": [],
            "notes": ["Macro neutral — no DXY/US10Y conflict"],
            "aligned": True,
            "decision_hint": "APPROVE",
            "direction": d,
            "dxy_direction": dxy,
            "us10y_direction": us10y,
        }

    score = 50

    if d == "sell":
        if dxy == "bullish":
            score = 88
            notes.append("DXY rising — high alignment score for XAUUSD SELL")
        elif dxy == "bearish":
            score = 22
            warnings.append("Risk High: DXY falling conflicts with Gold SELL")
        else:
            score = 55
            notes.append("DXY neutral — moderate SELL conditions")
    elif d == "buy":
        if dxy == "bearish":
            score = 88
            notes.append("DXY falling — high alignment score for XAUUSD BUY")
        elif dxy == "bullish":
            score = 22
            warnings.append("Risk High: DXY rising conflicts with Gold BUY")
        else:
            score = 55
            notes.append("DXY neutral — moderate BUY conditions")
    else:
        warnings.append(f"Unknown direction: {direction}")

    if us10y == "bullish" and d == "buy":
        score = max(20, score - 15)
        warnings.append("US10Y rising — headwind for Gold BUY")
    elif us10y == "bearish" and d == "sell":
        score = max(20, score - 15)
        warnings.append("US10Y falling — headwind for Gold SELL")
    elif us10y == "bearish" and d == "buy":
        score = min(95, score + 5)
        notes.append("US10Y falling — tailwind for Gold BUY")
    elif us10y == "bullish" and d == "sell":
        score = min(95, score + 5)
        notes.append("US10Y rising — tailwind for Gold SELL")

    if score >= 75:
        risk_level = "low"
        tag = "aligned"
    elif score >= 45:
        risk_level = "medium"
        tag = "medium"
    else:
        risk_level = "high"
        tag = "high"

    decision = "APPROVE"
    if warnings and score < 45:
        decision = "WAIT"
    elif warnings or score < 75:
        decision = "REDUCE_RISK"

    return {
        "score": score,
        "risk_level": risk_level,
        "correlation_risk_tag": tag,
        "warnings": warnings,
        "notes": notes,
        "aligned": score >= 75 and not warnings,
        "decision_hint": decision,
        "direction": d,
        "dxy_direction": dxy,
        "us10y_direction": us10y,
    }
