"""Market Room — XAUUSD market context."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

from src.common import data_path, save_json
from src.desk_config import load_market_config
from src.market_data.live_feed import fetch_live_macro_safe


def session_from_utc(ts: datetime) -> str:
    hour = ts.hour
    if 0 <= hour < 7:
        return "asia"
    if 7 <= hour < 13:
        return "london"
    if 13 <= hour < 21:
        return "ny"
    return "asia"


def _live_enabled() -> bool:
    flag = os.environ.get("MARKET_DATA_LIVE", "true").lower()
    return flag not in ("0", "false", "no", "off")


def get_market_context(
    *,
    spread_pts: float | None = None,
    news_risk: str = "low",
    volatility: str = "normal",
    xauusd_price: float | None = None,
    dxy_direction: str | None = None,
    us10y_direction: str | None = None,
    ts: datetime | None = None,
    live: bool | None = None,
) -> dict[str, Any]:
    ts = ts or datetime.now(timezone.utc)
    cfg = load_market_config()
    threshold = float(cfg["spread_threshold_pts"])
    spread = spread_pts if spread_pts is not None else 28.0

    use_live = _live_enabled() if live is None else live
    macro = fetch_live_macro_safe() if use_live else {
        "source": "mock",
        "dxy_direction": dxy_direction or "neutral",
        "us10y_direction": us10y_direction or "neutral",
        "dxy_context": {"direction": (dxy_direction or "neutral").lower(), "source": "mock"},
        "us10y_context": {"direction": (us10y_direction or "neutral").lower(), "source": "mock"},
        "xauusd_price": xauusd_price,
    }

    dxy_dir = (dxy_direction or macro.get("dxy_direction") or "neutral").lower()
    us10y_dir = (us10y_direction or macro.get("us10y_direction") or "neutral").lower()
    if dxy_direction:
        dxy_ctx = {"direction": dxy_dir, "source": macro.get("source", "mock")}
    else:
        dxy_ctx = macro.get("dxy_context") or {"direction": dxy_dir, "source": "mock"}
    if us10y_direction:
        us10y_ctx = {"direction": us10y_dir, "source": macro.get("source", "mock")}
    else:
        us10y_ctx = macro.get("us10y_context") or {"direction": us10y_dir, "source": "mock"}

    price = xauusd_price if xauusd_price is not None else macro.get("xauusd_price")

    ctx = {
        "symbol": "XAUUSD",
        "source": macro.get("source", "mock"),
        "provider": macro.get("provider", "mock"),
        "session": session_from_utc(ts),
        "spread_pts": spread,
        "spread_threshold": threshold,
        "spread_ok": spread <= threshold,
        "volatility": volatility,
        "news_risk": news_risk,
        "xauusd_price": price,
        "dxy_direction": dxy_dir,
        "us10y_direction": us10y_dir,
        "dxy_context": dxy_ctx,
        "us10y_context": us10y_ctx,
        "ts": ts.isoformat(),
    }
    if macro.get("error"):
        ctx["live_fetch_error"] = macro["error"]
    return ctx


def write_market_context(ctx: dict[str, Any]) -> None:
    save_json(data_path("market_context.json"), ctx)
