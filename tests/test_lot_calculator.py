"""Tests for lot_calculator."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.lot_calculator import calculate_lot, is_recovery_request


def test_conservative_lower_risk_than_aggressive():
    c = calculate_lot(
        account_equity=10000,
        risk_tier="conservative",
        stop_loss_distance=5.5,
    )
    a = calculate_lot(
        account_equity=10000,
        risk_tier="aggressive",
        stop_loss_distance=5.5,
    )
    assert c["allowed"]
    assert a["allowed"]
    assert c["suggested_risk_amount"] < a["suggested_risk_amount"]


def test_block_recovery():
    r = calculate_lot(
        account_equity=10000,
        risk_tier="standard",
        stop_loss_distance=5.0,
        recovery_request=True,
    )
    assert not r["allowed"]
    assert "martingale" in r["warning"].lower() or "recovery" in r["warning"].lower()


def test_recovery_keyword_detect():
    assert is_recovery_request("double after loss")
    assert not is_recovery_request("normal standard lot")
