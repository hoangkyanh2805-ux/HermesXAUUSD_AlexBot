"""Tests for journal, dashboard, ai_brain, publish_gate, telegram_router."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.ai_brain import summarize
from src.common import data_path, save_json
from src.dashboard import export_state, get_summary
from src.journal import append_journal, get_entry, list_entries
from src.publish_gate import publish_signal
from src.telegram_router import route_command


def _reset_journal():
    save_json(data_path("journal.json"), {"entries": []})


def test_journal_append_and_duplicate():
    _reset_journal()
    r = append_journal(
        signal_id="t-j1",
        pair="XAUUSD",
        direction="buy",
        entry=2345.0,
        stop_loss=2340.0,
        take_profits=[2355.0],
        result="win",
        session="london",
        lot_category="small",
        pnl=100.0,
        lesson="test lesson",
    )
    assert r["ok"]
    assert get_entry("t-j1") is not None
    r2 = append_journal(
        signal_id="t-j1",
        pair="XAUUSD",
        direction="buy",
        entry=2345.0,
        stop_loss=2340.0,
        take_profits=[2355.0],
        result="win",
        session="london",
        lot_category="small",
        pnl=100.0,
    )
    assert not r2["ok"]


def test_brain_refuses_without_enough_data():
    _reset_journal()
    append_journal(
        signal_id="t-b1",
        pair="XAUUSD",
        direction="buy",
        entry=2345.0,
        stop_loss=2340.0,
        take_profits=[2355.0],
        result="win",
        session="london",
        lot_category="small",
        pnl=50.0,
        lesson="one entry",
    )
    data = summarize()
    assert data["insights"]["not_enough_data"] is True


def test_publish_requires_alex():
    r = publish_signal(signal_id="x", messages={"a": "b"}, alex_approved=False)
    assert not r["ok"]
    r2 = publish_signal(signal_id="x", messages={"a": "b"}, alex_approved=True)
    assert r2["ok"]


def test_dashboard_export_has_journal():
    export_state()
    s = get_summary()
    assert "journal_entries" in s
    assert "total_pnl" in s


def test_router_reject_blocks_lot():
    route_command("/check_signal sig-reject-demo")
    r = route_command("/calc_lot sig-reject-demo 10000 standard")
    assert not r["ok"]
    _reset_journal()
