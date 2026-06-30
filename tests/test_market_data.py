"""Phase G — live market data tests (mocked HTTP)."""

from __future__ import annotations

import json
from unittest.mock import patch

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


def test_direction_from_closes_bullish():
    direction, stats = direction_from_closes([100.0, 100.5])
    assert direction == "bullish"
    assert stats["change_pct"] > 0


def test_fetch_live_macro_safe_mocked():
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
