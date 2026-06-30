"""Multi-entry split — total risk must remain unchanged."""

from __future__ import annotations

from typing import Any


def split_entries(
    *,
    total_lot: float,
    risk_budget_usd: float,
    legs: list[dict[str, Any]],
) -> dict[str, Any]:
    if total_lot <= 0:
        return {"ok": False, "error": "total_lot must be positive."}
    if not legs:
        return {"ok": False, "error": "At least one leg required."}

    leg_lots = [float(leg.get("lot", 0)) for leg in legs]
    lot_sum = round(sum(leg_lots), 4)
    if abs(lot_sum - total_lot) > 0.001:
        return {
            "ok": False,
            "error": f"Leg lots sum {lot_sum} != total_lot {total_lot}.",
        }

    for i, leg in enumerate(legs):
        if float(leg.get("lot", 0)) <= 0:
            return {"ok": False, "error": f"Leg {i + 1} lot must be positive."}
        if leg.get("entry") is None:
            return {"ok": False, "error": f"Leg {i + 1} missing entry price."}

    normalized = [
        {
            "leg": i + 1,
            "lot": float(leg["lot"]),
            "entry": float(leg["entry"]),
            "status": leg.get("status", "pending"),
        }
        for i, leg in enumerate(legs)
    ]
    return {
        "ok": True,
        "data": {
            "entries": normalized,
            "total_lot": total_lot,
            "risk_budget_usd": risk_budget_usd,
            "multi_entry_allowed": True,
            "note": "Total risk unchanged — split for execution control only.",
        },
    }
