"""Phase D tests — risk-first volume desk."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.common import data_path, save_json
from src.lot_calculator import calculate_lot
from src.multi_entry import split_entries
from src.safety_locks import evaluate_safety_locks
from src.signal_gate import check_signal
from src.signal_registry import create_signal
from src.spread_audit import list_events, record_spread, summarize_audit
from src.volume_tracker import get_summary, record_volume


def test_correlation_reduce_risk_buy_dxy_bullish():
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
        dxy_direction="bullish",
        us10y_direction="neutral",
    )
    assert r["decision"] == "REDUCE_RISK"
    assert r["correlation_risk_tag"] in ("medium", "high")


def test_calc_lot_returns_numeric_lot():
    r = calculate_lot(
        account_equity=10000,
        risk_tier="standard",
        stop_loss_distance=9.0,
    )
    assert r["allowed"]
    assert r["suggested_lot"] > 0


def test_spread_lock_wait():
    safety = evaluate_safety_locks(
        market_ctx={"spread_pts": 31, "spread_threshold": 30, "spread_ok": False},
        equity=10000,
    )
    assert safety["action_override"] == "WAIT"
    assert any("Spread lock" in x for x in safety["locks"])


def test_multi_entry_sum_matches():
    r = split_entries(
        total_lot=0.30,
        risk_budget_usd=100.0,
        legs=[
            {"lot": 0.10, "entry": 4092.0},
            {"lot": 0.10, "entry": 4090.0},
            {"lot": 0.10, "entry": 4088.0},
        ],
    )
    assert r["ok"]
    assert r["data"]["total_lot"] == 0.30


def test_volume_tracker_increments():
    save_json(data_path("volume_tracker.json"), {
        "daily": {},
        "weekly": {},
        "monthly": {},
        "kpi_target_monthly_lots": 200,
        "total_all_time": 0,
    })
    s = record_volume(lots=0.5)
    assert s["daily_lots"] == 0.5
    assert s["kpi_display_only"] is True


def test_create_signal_registers():
    sid = "t-phase-d-create"
    data = __import__("json")
    store = data_path("signals.json")
    from src.common import load_json

    all_sigs = load_json(store, {"signals": []})
    all_sigs["signals"] = [s for s in all_sigs.get("signals", []) if s.get("signal_id") != sid]
    save_json(store, all_sigs)

    r = create_signal(
        signal_id=sid,
        direction="sell",
        entry_low=4088.0,
        entry_high=4092.0,
        stop_loss=4099.0,
        take_profits=[4076.0],
        setup_name="london-breakout",
    )
    assert r["ok"]
    assert r["data"]["signal_id"] == sid


def test_spread_audit_seed_and_close():
    audit_path = data_path("spread_audit.jsonl")
    if audit_path.exists():
        audit_path.write_text("", encoding="utf-8")
    record_spread(signal_id="t-spread", event="seed", spread_pts=28.0, session="london")
    record_spread(signal_id="t-spread", event="close", spread_pts=30.0, session="london")
    rows = list_events("t-spread")
    assert len(rows) == 2
    assert summarize_audit()["count"] >= 2
