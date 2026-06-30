"""Tests for spread_monitor and seed safety lock."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.common import data_path, load_json, save_json
from src.safety_locks import evaluate_seed_lock
from src.spread_monitor import record_at_check, snapshot
from src.telegram_router import clear_pipeline_caches, route_command


def test_spread_monitor_logs_diff():
  save_json(data_path("spread_monitor_state.json"), {"baseline_spread": 25.0, "check_count": 5})
  row = record_at_check(signal_id="sig-mon-1", spread_pts=30.0, session="london")
  assert row["spread_diff"] == 5.0
  assert snapshot()["last_spread"] == 30.0


def test_seed_blocked_when_floating_risk_at_cap():
  save_json(
      data_path("risk_state.json"),
      {
          "last_equity": 10000.0,
          "floating_risk_pct": 3.0,
          "daily_drawdown_pct": 0.0,
          "open_trades": 1,
          "trades_today": 1,
          "last_reset_date": "2026-06-30",
          "signals_blocked_spread": 0,
      },
  )
  lock = evaluate_seed_lock(equity=10000.0)
  assert lock["blocked"] is True
  assert lock["cap_pct"] == 3.0


def test_seed_signal_blocked_by_safety_lock():
  clear_pipeline_caches()
  save_json(
      data_path("risk_state.json"),
      {
          "last_equity": 10000.0,
          "floating_risk_pct": 3.5,
          "daily_drawdown_pct": 0.0,
          "open_trades": 2,
          "trades_today": 2,
          "last_reset_date": "2026-06-30",
          "signals_blocked_spread": 0,
      },
  )
  save_json(
      data_path("signals.json"),
      {
          "signals": [
              {
                  "signal_id": "sig-lock-test",
                  "pair": "XAUUSD",
                  "direction": "buy",
                  "entry_low": 2320.0,
                  "entry_high": 2322.0,
                  "stop_loss": 2314.0,
                  "take_profits": [2332.0],
                  "session": "london",
                  "news_risk": "low",
                  "market_bias": "bullish",
                  "status": "draft",
              }
          ]
      },
  )
  from src.telegram_router import _gate_cache

  _gate_cache["sig-lock-test"] = {"decision": "APPROVE"}
  from src.telegram_router import _lot_cache

  _lot_cache["sig-lock-test"] = {"suggested_lot_category": "small", "account_equity": 10000.0}
  save_json(data_path("market_context.json"), {"spread_pts": 25.0, "session": "london"})
  result = route_command("/seed_signal sig-lock-test")
  assert result["ok"] is False
  assert "Safety lock" in result["error"]


def test_seed_correlation_snapshot_persisted():
  import os

  clear_pipeline_caches()
  os.environ["MARKET_DATA_LIVE"] = "false"
  save_json(
      data_path("risk_state.json"),
      {
          "last_equity": 5000.0,
          "floating_risk_pct": 0.0,
          "daily_drawdown_pct": 0.0,
          "open_trades": 0,
          "trades_today": 0,
          "last_reset_date": "2026-06-30",
          "signals_blocked_spread": 0,
      },
  )
  save_json(
      data_path("signals.json"),
      {
          "signals": [
              {
                  "signal_id": "sig-seed-snap",
                  "pair": "XAUUSD",
                  "direction": "sell",
                  "entry_low": 4015.0,
                  "entry_high": 4019.0,
                  "stop_loss": 4028.0,
                  "take_profits": [4000.0],
                  "session": "london",
                  "news_risk": "low",
                  "market_bias": "bearish",
                  "status": "draft",
              }
          ]
      },
  )
  from src.telegram_router import _gate_cache, _lot_cache

  _gate_cache["sig-seed-snap"] = {
      "decision": "REDUCE_RISK",
      "correlation_risk_tag": "medium",
      "correlation_reasons": ["test"],
  }
  _lot_cache["sig-seed-snap"] = {
      "suggested_lot_category": "small",
      "suggested_lot": 0.1,
      "account_equity": 5000.0,
  }
  save_json(data_path("market_context.json"), {"spread_pts": 25.0, "session": "london"})
  result = route_command("/seed_signal sig-seed-snap")
  assert result["ok"] is True
  cd = result["data"]["correlation_data"]
  assert cd.get("snapshot_phase") == "seed"
  assert cd.get("snapshotted_at")
  stored = load_json(data_path("signals.json"), {})
  row = next(s for s in stored["signals"] if s["signal_id"] == "sig-seed-snap")
  assert row["correlation_data"]["snapshot_phase"] == "seed"


def test_publish_correlation_snapshot_persisted():
  import os

  clear_pipeline_caches()
  os.environ["MARKET_DATA_LIVE"] = "false"
  save_json(
      data_path("risk_state.json"),
      {
          "last_equity": 5000.0,
          "floating_risk_pct": 0.0,
          "daily_drawdown_pct": 0.0,
          "open_trades": 0,
          "trades_today": 0,
          "last_reset_date": "2026-06-30",
          "signals_blocked_spread": 0,
      },
  )
  save_json(
      data_path("signals.json"),
      {
          "signals": [
              {
                  "signal_id": "sig-pub-snap",
                  "pair": "XAUUSD",
                  "direction": "buy",
                  "entry_low": 2320.0,
                  "entry_high": 2322.0,
                  "stop_loss": 2314.0,
                  "take_profits": [2332.0],
                  "session": "london",
                  "news_risk": "low",
                  "market_bias": "bullish",
                  "status": "draft",
              }
          ]
      },
  )
  from src.telegram_router import _gate_cache, _lot_cache, _seeding_cache

  _gate_cache["sig-pub-snap"] = {"decision": "APPROVE"}
  _lot_cache["sig-pub-snap"] = {
      "suggested_lot_category": "small",
      "suggested_lot": 0.1,
      "account_equity": 5000.0,
  }
  _seeding_cache["sig-pub-snap"] = {"main": "test message"}
  save_json(data_path("market_context.json"), {"spread_pts": 25.0, "session": "london"})
  seed = route_command("/seed_signal sig-pub-snap")
  assert seed["ok"] is True
  result = route_command("/publish_signal sig-pub-snap yes")
  assert result["ok"] is True
  cd = result["data"]["correlation_data"]
  assert cd.get("snapshot_phase") == "publish"
  assert cd.get("entry_phase") == "publish"
  stored = load_json(data_path("signals.json"), {})
  row = next(s for s in stored["signals"] if s["signal_id"] == "sig-pub-snap")
  assert row["correlation_data"]["snapshot_phase"] == "publish"
  assert row.get("correlation_snapshotted_at_publish")
