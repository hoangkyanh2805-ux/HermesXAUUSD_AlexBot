"""Market Room — XAUUSD market context."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.common import data_path, save_json

SPREAD_THRESHOLD = 35.0


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
    ts: datetime | None = None,
) -> dict[str, Any]:
    ts = ts or datetime.now(timezone.utc)
    spread = spread_pts if spread_pts is not None else 28.0

    ctx = {
        "symbol": "XAUUSD",
        "session": session_from_utc(ts),
        "spread_pts": spread,
        "spread_ok": spread <= SPREAD_THRESHOLD,
        "volatility": volatility,
        "news_risk": news_risk,
        "ts": ts.isoformat(),
    }
    return ctx


def write_market_context(ctx: dict[str, Any]) -> None:
    save_json(data_path("market_context.json"), ctx)
