"""Register new signals in data/signals.json."""

from __future__ import annotations

from typing import Any

from src.common import data_path, load_json, save_json
from src.dashboard import export_state


def create_signal(
    *,
    signal_id: str,
    pair: str = "XAUUSD",
    direction: str,
    entry_low: float,
    entry_high: float,
    stop_loss: float,
    take_profits: list[float],
    session: str = "london",
    news_risk: str = "low",
    market_bias: str = "neutral",
    setup_name: str = "",
    dxy_direction: str = "neutral",
    us10y_direction: str = "neutral",
) -> dict[str, Any]:
    if not signal_id:
        return {"ok": False, "error": "signal_id required."}
    if pair.upper() != "XAUUSD":
        return {"ok": False, "error": "Desk supports XAUUSD only."}
    if stop_loss is None:
        return {"ok": False, "error": "stop_loss required."}
    if not take_profits:
        return {"ok": False, "error": "At least one take_profit required."}

    data = load_json(data_path("signals.json"), {"signals": []})
    for s in data.get("signals", []):
        if s.get("signal_id") == signal_id:
            return {"ok": False, "error": f"Signal already exists: {signal_id}"}

    row = {
        "signal_id": signal_id,
        "pair": pair.upper(),
        "direction": direction.lower(),
        "entry_low": float(entry_low),
        "entry_high": float(entry_high),
        "stop_loss": float(stop_loss),
        "take_profits": [float(x) for x in take_profits],
        "session": session.lower(),
        "news_risk": news_risk.lower(),
        "market_bias": market_bias.lower(),
        "setup_name": setup_name,
        "dxy_direction": dxy_direction.lower(),
        "us10y_direction": us10y_direction.lower(),
        "status": "draft",
        "lot_category": None,
        "correlation_risk_tag": None,
    }
    data.setdefault("signals", []).append(row)
    save_json(data_path("signals.json"), data)
    export_state()
    return {"ok": True, "data": row}
