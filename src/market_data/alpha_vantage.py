"""Live macro quotes — DXY proxy + US10Y via Alpha Vantage (stdlib only)."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.common import REPO_ROOT, data_path, load_json, save_json
from src.market_data.live_feed import direction_from_closes

_BASE_URL = "https://www.alphavantage.co/query"
_USER_AGENT = "HermesXAUUSD-Desk/1.0"
_ENV_PATHS = (
    REPO_ROOT / "market_data" / ".env",
    REPO_ROOT / "supabase" / ".env",
)


def _load_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    env: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        env[key.strip()] = value.strip()
    return env


def _api_key() -> str:
    key = os.environ.get("ALPHA_VANTAGE_API_KEY", "").strip()
    if key:
        return key
    for path in _ENV_PATHS:
        key = _load_env_file(path).get("ALPHA_VANTAGE_API_KEY", "").strip()
        if key:
            return key
    return ""


def _cache_ttl_seconds() -> int:
    raw = os.environ.get("ALPHA_VANTAGE_CACHE_SECONDS", "900").strip()
    try:
        return max(60, int(raw))
    except ValueError:
        return 900


def _cache_path() -> Path:
    return data_path("alpha_vantage_cache.json")


def _read_cache() -> dict[str, Any] | None:
    cached = load_json(_cache_path(), {})
    fetched_at = cached.get("fetched_at")
    payload = cached.get("macro")
    if not fetched_at or not payload:
        return None
    try:
        ts = datetime.fromisoformat(str(fetched_at).replace("Z", "+00:00"))
    except ValueError:
        return None
    age = (datetime.now(timezone.utc) - ts).total_seconds()
    if age > _cache_ttl_seconds():
        return None
    return payload


def _write_cache(macro: dict[str, Any]) -> None:
    save_json(
        _cache_path(),
        {
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "macro": macro,
        },
    )


def _av_query(params: dict[str, str]) -> dict[str, Any]:
    api_key = _api_key()
    if not api_key:
        raise ValueError("ALPHA_VANTAGE_API_KEY not configured")
    query = urllib.parse.urlencode({**params, "apikey": api_key})
    url = f"{_BASE_URL}?{query}"
    req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    with urllib.request.urlopen(req, timeout=25) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    if payload.get("Note") or payload.get("Information"):
        raise ValueError(str(payload.get("Note") or payload.get("Information"))[:200])
    if "Error Message" in payload:
        raise ValueError(str(payload["Error Message"])[:200])
    return payload


def _sorted_daily_closes(series: dict[str, dict[str, str]], close_key: str) -> list[float]:
    rows: list[tuple[str, float]] = []
    for day, values in series.items():
        raw = values.get(close_key)
        if raw is None:
            continue
        rows.append((day, float(raw)))
    rows.sort(key=lambda item: item[0])
    closes = [price for _, price in rows]
    if len(closes) < 2:
        raise ValueError("Insufficient Alpha Vantage daily closes")
    return closes


def _fetch_usd_eur_daily() -> dict[str, Any]:
    closes = _fetch_fx_daily("USD", "EUR")
    direction, stats = direction_from_closes(closes)
    return {
        "symbol": "USD/EUR",
        "label": "DXY",
        "proxy": "USD/EUR",
        "direction": direction,
        "source": "alpha_vantage",
        **stats,
    }


def _fetch_us10y_daily() -> dict[str, Any]:
    payload = _av_query(
        {
            "function": "TREASURY_YIELD",
            "interval": "daily",
            "maturity": "10year",
        }
    )
    rows = payload.get("data") or []
    values: list[tuple[str, float]] = []
    for row in rows:
        raw = row.get("value")
        if raw in (None, ".", ""):
            continue
        values.append((str(row.get("date", "")), float(raw)))
    values.sort(key=lambda item: item[0])
    closes = [value for _, value in values]
    if len(closes) < 2:
        raise ValueError("Insufficient Alpha Vantage treasury yields")
    direction, stats = direction_from_closes(closes)
    return {
        "symbol": "US10Y",
        "label": "US10Y",
        "direction": direction,
        "source": "alpha_vantage",
        **stats,
    }


def _fetch_fx_daily(from_symbol: str, to_symbol: str) -> list[float]:
    payload = _av_query(
        {"function": "FX_DAILY", "from_symbol": from_symbol, "to_symbol": to_symbol}
    )
    series = payload.get("Time Series FX (Daily)") or {}
    return _sorted_daily_closes(series, "4. close")


def _fetch_xauusd_price() -> float | None:
    """XAUUSD via FX_DAILY (forex); fallback CURRENCY_EXCHANGE_RATE spot."""
    try:
        closes = _fetch_fx_daily("XAU", "USD")
        return closes[-1]
    except (urllib.error.URLError, ValueError, KeyError, OSError, json.JSONDecodeError):
        pass
    payload = _av_query(
        {
            "function": "CURRENCY_EXCHANGE_RATE",
            "from_currency": "XAU",
            "to_currency": "USD",
        }
    )
    rate = (payload.get("Realtime Currency Exchange Rate") or {}).get("5. Exchange Rate")
    if rate is None:
        return None
    return float(rate)


def fetch_live_macro_alpha() -> dict[str, Any]:
    """Fetch DXY proxy + US10Y from Alpha Vantage. Raises on total failure."""
    cached = _read_cache()
    if cached:
        return cached

    dxy = _fetch_usd_eur_daily()
    us10y = _fetch_us10y_daily()
    xauusd_price: float | None = None
    try:
        xauusd_price = _fetch_xauusd_price()
    except (urllib.error.URLError, ValueError, KeyError, OSError, json.JSONDecodeError):
        pass

    macro = {
        "source": "live",
        "provider": "alpha_vantage",
        "dxy_direction": dxy["direction"],
        "us10y_direction": us10y["direction"],
        "dxy_context": dxy,
        "us10y_context": us10y,
        "xauusd_price": xauusd_price,
    }
    _write_cache(macro)
    return macro


def fetch_live_macro_alpha_safe() -> dict[str, Any]:
    """Return Alpha Vantage macro or mock fallback with error note."""
    try:
        return fetch_live_macro_alpha()
    except (urllib.error.URLError, ValueError, KeyError, OSError, json.JSONDecodeError) as exc:
        return {
            "source": "mock",
            "provider": "alpha_vantage",
            "error": str(exc)[:200],
            "dxy_direction": "neutral",
            "us10y_direction": "neutral",
            "dxy_context": {
                "direction": "neutral",
                "source": "mock",
                "error": str(exc)[:120],
            },
            "us10y_context": {
                "direction": "neutral",
                "source": "mock",
                "error": str(exc)[:120],
            },
            "xauusd_price": None,
        }
