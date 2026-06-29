"""Tests for signal_gate."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.signal_gate import check_signal


def test_reject_no_sl():
    r = check_signal(
        pair="XAUUSD",
        direction="buy",
        entry_low=2345.0,
        entry_high=2346.0,
        stop_loss=None,
        take_profits=[2355.0],
        session="london",
        news_risk="low",
        market_bias="bullish",
    )
    assert r["decision"] == "REJECT"
    assert any("stop loss" in x.lower() for x in r["reasons"])


def test_reject_no_tp():
    r = check_signal(
        pair="XAUUSD",
        direction="buy",
        entry_low=2345.0,
        entry_high=2346.0,
        stop_loss=2340.0,
        take_profits=[],
        session="london",
        news_risk="low",
        market_bias="bullish",
    )
    assert r["decision"] == "REJECT"


def test_reject_poor_rr():
    r = check_signal(
        pair="XAUUSD",
        direction="buy",
        entry_low=2345.0,
        entry_high=2346.0,
        stop_loss=2340.0,
        take_profits=[2347.0],
        session="london",
        news_risk="low",
        market_bias="bullish",
    )
    assert r["decision"] == "REJECT"


def test_wait_high_news():
    r = check_signal(
        pair="XAUUSD",
        direction="buy",
        entry_low=2345.0,
        entry_high=2346.0,
        stop_loss=2340.0,
        take_profits=[2355.0],
        session="london",
        news_risk="high",
        market_bias="bullish",
    )
    assert r["decision"] == "WAIT"


def test_wait_bias_conflict():
    r = check_signal(
        pair="XAUUSD",
        direction="buy",
        entry_low=2345.0,
        entry_high=2346.0,
        stop_loss=2340.0,
        take_profits=[2355.0],
        session="london",
        news_risk="low",
        market_bias="bearish",
    )
    assert r["decision"] == "WAIT"


def test_approve_valid():
    r = check_signal(
        pair="XAUUSD",
        direction="buy",
        entry_low=2344.0,
        entry_high=2346.0,
        stop_loss=2340.0,
        take_profits=[2355.0],
        session="london",
        news_risk="low",
        market_bias="bullish",
    )
    assert r["decision"] == "APPROVE"
    assert r.get("rr", 0) >= 1.5
