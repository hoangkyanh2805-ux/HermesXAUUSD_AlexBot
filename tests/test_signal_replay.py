"""Tests for signal replay (Phase C)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.common import data_path, save_json
from src.signal_replay import get_setup_status, promote_setup, replay_signals


def _reset_setups():
    save_json(
        data_path("setups.json"),
        {
            "setups": {
                "london-breakout": {"status": "draft", "replay_required": True},
                "ny-reversal": {"status": "draft", "replay_required": True},
            }
        },
    )


def test_london_breakout_replay_passes():
    r = replay_signals("london-breakout")
    assert r["ok"]
    assert r["pass"] is True
    assert r["trades"] == 30
    assert r["win_rate"] >= 0.55
    assert r["avg_r"] >= 1.5


def test_ny_reversal_replay_fails():
    r = replay_signals("ny-reversal")
    assert r["ok"]
    assert r["pass"] is False


def test_promote_setup():
    _reset_setups()
    promote_setup("london-breakout", "replay_passed")
    assert get_setup_status("london-breakout") == "replay_passed"
