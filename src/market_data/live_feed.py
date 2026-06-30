"""Live macro quotes — DXY + US10Y via Yahoo Finance (stdlib only)."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

# Yahoo Finance symbols
DXY_SYMBOL = "DX-Y.NYB"
US10Y_SYMBOL = "^TNX"
XAUUSD_SYMBOL = "GC=F"

_USER_AGENT = "HermesXAUUSD-Desk/1.0"
_DIRECTION_THRESHOLD_PCT = 0.15


def _fetch_closes(symbol: str, *, range_days: str = "5d") -> list[float]:
    encoded = symbol.replace("^", "%5E")
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{encoded}"
        f"?interval=1d&range={range_days}"
    )
    req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    with urllib.request.urlopen(req, timeout=20) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    result = (payload.get("chart") or {}).get("result") or []
    if not result:
        raise ValueError(f"No chart data for {symbol}")
    closes = (result[0].get("indicators") or {}).get("quote", [{}])[0].get("close") or []
    values = [float(c) for c in closes if c is not None]
    if len(values) < 2:
        raise ValueError(f"Insufficient closes for {symbol}")
    return values


def direction_from_closes(
    closes: list[float],
    *,
    threshold_pct: float = _DIRECTION_THRESHOLD_PCT,
) -> tuple[str, dict[str, Any]]:
    prev, last = closes[-2], closes[-1]
    if prev == 0:
        return "neutral", {"price": last, "prev_price": prev, "change_pct": 0.0}
    change_pct = (last - prev) / prev * 100.0
    if change_pct > threshold_pct:
        direction = "bullish"
    elif change_pct < -threshold_pct:
        direction = "bearish"
    else:
        direction = "neutral"
    return direction, {
        "price": round(last, 4),
        "prev_price": round(prev, 4),
        "change_pct": round(change_pct, 3),
    }


def fetch_instrument(symbol: str, *, label: str) -> dict[str, Any]:
    closes = _fetch_closes(symbol)
    direction, stats = direction_from_closes(closes)
    return {
        "symbol": symbol,
        "label": label,
        "direction": direction,
        "source": "yahoo_finance",
        **stats,
    }


def fetch_live_macro() -> dict[str, Any]:
    """Fetch DXY + US10Y directions. Raises on total failure."""
    dxy = fetch_instrument(DXY_SYMBOL, label="DXY")
    us10y = fetch_instrument(US10Y_SYMBOL, label="US10Y")
    xauusd_price: float | None = None
    try:
        gold_closes = _fetch_closes(XAUUSD_SYMBOL)
        xauusd_price = gold_closes[-1]
    except (urllib.error.URLError, ValueError, KeyError, OSError):
        pass
    return {
        "source": "live",
        "provider": "yahoo_finance",
        "dxy_direction": dxy["direction"],
        "us10y_direction": us10y["direction"],
        "dxy_context": dxy,
        "us10y_context": us10y,
        "xauusd_price": xauusd_price,
    }


def fetch_live_macro_safe() -> dict[str, Any]:
    """Return live macro or mock fallback with error note."""
    try:
        return fetch_live_macro()
    except (urllib.error.URLError, ValueError, KeyError, OSError, json.JSONDecodeError) as exc:
        return {
            "source": "mock",
            "provider": "fallback",
            "error": str(exc)[:200],
            "dxy_direction": "neutral",
            "us10y_direction": "neutral",
            "dxy_context": {"direction": "neutral", "source": "mock", "error": str(exc)[:120]},
            "us10y_context": {"direction": "neutral", "source": "mock", "error": str(exc)[:120]},
            "xauusd_price": None,
        }
