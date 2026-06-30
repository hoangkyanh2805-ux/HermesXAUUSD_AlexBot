"""Market Room — XAUUSD market context."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.common import data_path, save_json
from src.desk_config import load_market_config


def session_from_utc(ts: datetime) -> str:
    hour = ts.hour
    if 0 <= hour < 7:
        return "asia"
    if 7 <= hour < 13:
        return "london"
    if 13 <= hour < 21:
        return "ny"
    return "asia"


def get_market_context(
    *,
    spread_pts: float | None = None,
    news_risk: str = "low",
    volatility: str = "normal",
    xauusd_price: float | None = None,
    dxy_direction: str = "neutral",
    us10y_direction: str = "neutral",
    ts: datetime | None = None,
) -> dict[str, Any]:
    ts = ts or datetime.now(timezone.utc)
    cfg = load_market_config()
    threshold = float(cfg["spread_threshold_pts"])
    spread = spread_pts if spread_pts is not None else 28.0

    ctx = {
        "symbol": "XAUUSD",
        "source": "mock",
        "session": session_from_utc(ts),
        "spread_pts": spread,
        "spread_threshold": threshold,
        "spread_ok": spread <= threshold,
        "volatility": volatility,
        "news_risk": news_risk,
        "xauusd_price": xauusd_price,
        "dxy_direction": dxy_direction.lower(),
        "us10y_direction": us10y_direction.lower(),
        "dxy_context": {"direction": dxy_direction.lower(), "source": "mock"},
        "us10y_context": {"direction": us10y_direction.lower(), "source": "mock"},
        "ts": ts.isoformat(),
    }
    return ctx


def write_market_context(ctx: dict[str, Any]) -> None:
    save_json(data_path("market_context.json"), ctx)
