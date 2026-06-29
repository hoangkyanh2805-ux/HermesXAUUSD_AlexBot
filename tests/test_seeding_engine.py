"""Tests for seeding_engine."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.seeding_engine import generate_seeding, lint_copy


def test_all_message_types_generated():
    msgs = generate_seeding(
        signal_id="sig-t",
        pair="XAUUSD",
        direction="buy",
        entry_low=2344.0,
        entry_high=2346.0,
        stop_loss=2340.0,
        take_profits=[2355.0],
        session="london",
        setup_name="london-breakout",
        rr=2.1,
    )
    expected = {
        "pre_signal_context",
        "signal_drop",
        "reason_message",
        "risk_reminder",
        "live_update",
        "tp_hit_update",
        "sl_hit_update",
        "result_summary",
    }
    assert expected == set(msgs.keys())


def test_lint_blocks_hype():
    bad = lint_copy("This is a guaranteed profit trade!")
    assert not bad["pass"]
    assert bad["violations"]


def test_lint_passes_calm_copy():
    good = lint_copy("Trade at your own risk. Past results do not guarantee future outcomes.")
    assert good["pass"]
