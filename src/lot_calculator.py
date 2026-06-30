"""Lot Room — equity-based lot sizing with risk-first rules."""

from __future__ import annotations

from typing import Any

from src.common import data_path, load_json
from src.desk_config import load_client_rules, load_market_config

RECOVERY_KEYWORDS = ("recovery", "recover", "martingale", "double", "double_down")


def _load_groups() -> dict:
    return load_json(data_path("client_groups.json"), {"groups": {}})


def _value_per_point_per_lot() -> float:
    rules = load_client_rules().get("rules", {})
    cfg = load_market_config()
    per_001 = float(
        rules.get("pip_value_per_0_01_lot")
        or cfg.get("xauusd_value_per_point_per_0_01_lot", 0.1)
    )
    return per_001 * 100.0


def calculate_lot(
    *,
    account_equity: float,
    risk_tier: str,
    stop_loss_distance: float,
    max_risk_percent: float | None = None,
    recovery_request: bool = False,
    previous_loss: bool = False,
    risk_multiplier: float = 1.0,
    safety_blocked: bool = False,
) -> dict[str, Any]:
    """Calculate lot from equity, risk%, and SL distance."""
    tier = risk_tier.lower()
    groups = _load_groups().get("groups", {})

    if safety_blocked:
        return {
            "allowed": False,
            "suggested_risk_amount": 0.0,
            "suggested_lot": 0.0,
            "suggested_lot_category": None,
            "warning": "Safety lock active — new lot calculation blocked.",
        }

    if tier not in groups:
        return {
            "allowed": False,
            "suggested_risk_amount": 0.0,
            "suggested_lot": 0.0,
            "suggested_lot_category": None,
            "warning": f"Unknown risk tier: {risk_tier}",
        }

    if recovery_request or previous_loss:
        return {
            "allowed": False,
            "suggested_risk_amount": 0.0,
            "suggested_lot": 0.0,
            "suggested_lot_category": None,
            "warning": "Martingale / recovery lot increase is not allowed.",
        }

    if account_equity <= 0:
        return {
            "allowed": False,
            "suggested_risk_amount": 0.0,
            "suggested_lot": 0.0,
            "suggested_lot_category": None,
            "warning": "Account equity must be positive.",
        }

    if stop_loss_distance <= 0:
        return {
            "allowed": False,
            "suggested_risk_amount": 0.0,
            "suggested_lot": 0.0,
            "suggested_lot_category": None,
            "warning": "Stop loss distance must be positive.",
        }

    group = groups[tier]
    risk_pct = float(group.get("risk_pct", 1.0))
    cap_pct = float(group.get("max_risk_pct", risk_pct))
    max_lot = float(group.get("max_lot", 0.1))

    if max_risk_percent is not None:
        risk_pct = min(risk_pct, max_risk_percent, cap_pct)
    else:
        risk_pct = min(risk_pct, cap_pct)

    if tier == "conservative":
        risk_pct = min(risk_pct, float(groups["conservative"].get("risk_pct", 0.5)))

    risk_pct *= max(0.0, min(1.0, risk_multiplier))
    suggested_risk_amount = round(account_equity * (risk_pct / 100.0), 2)
    lot_category = group.get("lot_category", "small")

    value_per_point = _value_per_point_per_lot()
    raw_lot = suggested_risk_amount / (stop_loss_distance * value_per_point)
    suggested_lot = round(min(raw_lot, max_lot), 2)

    warning = ""
    if tier == "aggressive":
        warning = "Aggressive tier is capped by max_risk_pct; size responsibly."
    if risk_multiplier < 1.0:
        warning = (warning + " Reduced risk sizing applied.").strip()
    if raw_lot > max_lot:
        warning = (warning + f" Lot capped at tier max {max_lot}.").strip()

    return {
        "allowed": True,
        "suggested_risk_amount": suggested_risk_amount,
        "suggested_lot": suggested_lot,
        "suggested_lot_category": lot_category,
        "risk_tier": tier,
        "risk_percent_used": round(risk_pct, 3),
        "risk_multiplier": risk_multiplier,
        "stop_loss_distance": stop_loss_distance,
        "value_per_point_per_lot": value_per_point,
        "warning": warning,
    }


def is_recovery_request(text: str) -> bool:
    lower = text.lower()
    return any(k in lower for k in RECOVERY_KEYWORDS)
