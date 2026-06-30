"""Tests for market_conditions.validate_market_conditions."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.market_conditions import validate_market_conditions


def test_sell_dxy_up_high_score():
    mc = validate_market_conditions(direction="sell", dxy_direction="bullish", us10y_direction="neutral")
    assert mc["score"] >= 75
    assert mc["aligned"] is True
    assert not any("Risk High" in w for w in mc["warnings"])


def test_sell_dxy_down_risk_high():
    mc = validate_market_conditions(direction="sell", dxy_direction="bearish", us10y_direction="neutral")
    assert mc["score"] < 45
    assert any("Risk High" in w for w in mc["warnings"])
    assert mc["risk_level"] == "high"


def test_buy_dxy_down_high_score():
    mc = validate_market_conditions(direction="buy", dxy_direction="bearish", us10y_direction="neutral")
    assert mc["score"] >= 75
    assert mc["aligned"] is True


def test_buy_dxy_up_risk_high():
    mc = validate_market_conditions(direction="buy", dxy_direction="bullish", us10y_direction="neutral")
    assert mc["score"] < 45
    assert any("Risk High" in w for w in mc["warnings"])
