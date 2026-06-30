"""Phase G — live market data tests (mocked HTTP)."""

from __future__ import annotations

import json
import os
from unittest.mock import patch

from src.market_data.alpha_vantage import fetch_live_macro_alpha_safe
from src.market_data.live_feed import direction_from_closes, fetch_live_macro_safe


def _yahoo_chart_payload(closes: list[float]) -> bytes:
    body = {
        "chart": {
            "result": [
                {
                    "indicators": {"quote": [{"close": closes}]},
                }
            ]
        }
    }
    return json.dumps(body).encode("utf-8")


def _av_fx_payload(closes: list[tuple[str, float]]) -> bytes:
    series = {
        day: {"4. close": str(price)}
        for day, price in closes
    }
    body = {"Time Series FX (Daily)": series}
    return json.dumps(body).encode("utf-8")


def _av_treasury_payload(values: list[tuple[str, float]]) -> bytes:
    body = {
        "data": [{"date": day, "value": str(value)} for day, value in values],
    }
    return json.dumps(body).encode("utf-8")


def test_direction_from_closes_bullish():
    direction, stats = direction_from_closes([100.0, 100.5])
    assert direction == "bullish"
    assert stats["change_pct"] > 0


def test_fetch_live_macro_safe_mocked_yahoo():
    os.environ["MARKET_DATA_PROVIDER"] = "yahoo"
    dxy = _yahoo_chart_payload([104.0, 104.5])
    tnx = _yahoo_chart_payload([4.1, 4.2])
    gold = _yahoo_chart_payload([2300.0, 2310.0])

    def fake_urlopen(req, timeout=20):
        url = req.full_url
        if "DX-Y" in url:
            data = dxy
        elif "%5ETNX" in url or "^TNX" in url:
            data = tnx
        else:
            data = gold

        class Resp:
            def read(self):
                return data

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        return Resp()

    with patch("urllib.request.urlopen", fake_urlopen):
        macro = fetch_live_macro_safe()
    assert macro["source"] == "live"
    assert macro["dxy_direction"] in ("bullish", "bearish", "neutral")
    assert macro["us10y_context"]["source"] == "yahoo_finance"


def test_fetch_alpha_vantage_safe_mocked():
    os.environ["ALPHA_VANTAGE_API_KEY"] = "test-key"
    fx = _av_fx_payload([("2026-06-27", 0.91), ("2026-06-28", 0.92)])
    treasury = _av_treasury_payload([("2026-06-27", 4.1), ("2026-06-28", 4.2)])
    xau = json.dumps(
        {
            "Realtime Currency Exchange Rate": {
                "5. Exchange Rate": "2310.5",
            }
        }
    ).encode("utf-8")

    def fake_urlopen(req, timeout=25):
        url = req.full_url
        if "FX_DAILY" in url:
            data = fx
        elif "TREASURY_YIELD" in url:
            data = treasury
        else:
            data = xau

        class Resp:
            def read(self):
                return data

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        return Resp()

    with patch("urllib.request.urlopen", fake_urlopen):
        macro = fetch_live_macro_alpha_safe()
    assert macro["source"] == "live"
    assert macro["provider"] == "alpha_vantage"
    assert macro["dxy_context"]["proxy"] == "USD/EUR"
    assert macro["us10y_context"]["source"] == "alpha_vantage"
    assert macro["xauusd_price"] == 2310.5
