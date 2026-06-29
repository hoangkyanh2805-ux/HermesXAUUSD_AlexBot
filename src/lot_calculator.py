"""Lot Room — safe lot category by client risk tier."""

from __future__ import annotations

from typing import Any

from src.common import data_path, load_json

RECOVERY_KEYWORDS = ("recovery", "recover", "martingale", "double", "double_down")


def _load_groups() -> dict:
    return load_json(data_path("client_groups.json"), {"groups": {}})


def calculate_lot(
    *,
    account_equity: float,
    risk_tier: str,
    stop_loss_distance: float,
    max_risk_percent: float | None = None,
    recovery_request: bool = False,
    previous_loss: bool = False,
) -> dict[str, Any]:
    """Calculate safe lot guidance by risk tier."""
    tier = risk_tier.lower()
    groups = _load_groups().get("groups", {})

    if tier not in groups:
        return {
            "allowed": False,
            "suggested_risk_amount": 0.0,
            "suggested_lot_category": None,
            "warning": f"Unknown risk tier: {risk_tier}",
        }

    if recovery_request or previous_loss:
        return {
            "allowed": False,
            "suggested_risk_amount": 0.0,
            "suggested_lot_category": None,
            "warning": "Martingale / recovery lot increase is not allowed.",
        }

    if account_equity <= 0:
        return {
            "allowed": False,
            "suggested_risk_amount": 0.0,
            "suggested_lot_category": None,
            "warning": "Account equity must be positive.",
        }

    if stop_loss_distance <= 0:
        return {
            "allowed": False,
            "suggested_risk_amount": 0.0,
            "suggested_lot_category": None,
            "warning": "Stop loss distance must be positive.",
        }

    group = groups[tier]
    risk_pct = float(group.get("risk_pct", 1.0))
    cap_pct = float(group.get("max_risk_pct", risk_pct))

    if max_risk_percent is not None:
        risk_pct = min(risk_pct, max_risk_percent, cap_pct)
    else:
        risk_pct = min(risk_pct, cap_pct)

    if tier == "conservative":
        risk_pct = min(risk_pct, float(groups["conservative"].get("risk_pct", 0.5)))

    suggested_risk_amount = round(account_equity * (risk_pct / 100.0), 2)
    lot_category = group.get("lot_category", "small")

    warning = ""
    if tier == "aggressive":
        warning = "Aggressive tier is capped by max_risk_pct; size responsibly."

    return {
        "allowed": True,
        "suggested_risk_amount": suggested_risk_amount,
        "suggested_lot_category": lot_category,
        "risk_tier": tier,
        "risk_percent_used": risk_pct,
        "warning": warning,
    }


def is_recovery_request(text: str) -> bool:
    lower = text.lower()
    return any(k in lower for k in RECOVERY_KEYWORDS)
