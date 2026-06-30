"""Phase E — Supabase sync payload tests (no network)."""

from __future__ import annotations

from src.supabase_sync import build_sync_payloads, get_supabase_config, sync_all


def test_build_sync_payloads_signals_skip_no_sl():
    payloads = build_sync_payloads()
    ids = {s["signal_id"] for s in payloads["signals"]}
    assert "sig-reject-demo" not in ids
    assert "sig-sell-4088" in ids
    assert len(payloads["signals"]) >= 3


def test_build_sync_activity_keys_match_rows():
    payloads = build_sync_payloads()
    assert len(payloads["activity_logs"]) == len(payloads["activity_keys"])
    assert payloads["activity_logs"][0]["event_type"] == "SIGNAL_WAITING"


def test_sync_dry_run_ok():
    result = sync_all(dry_run=True)
    assert result["ok"] is True
    assert result["dry_run"] is True
    assert result["counts"]["signals"] >= 3


def test_sync_missing_credentials():
    result = sync_all(dry_run=False)
    if get_supabase_config()["url"] and get_supabase_config()["service_key"]:
        return
    assert result["ok"] is False
    assert "Missing SUPABASE_URL" in result.get("error", "")
