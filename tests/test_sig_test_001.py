"""Phase F — sig-test-001 end-to-end flow."""

from __future__ import annotations

import os

from src.pipeline_test_flow import run_sig_test_001
from src.supabase_writer import build_step_payloads


def test_sig_test_001_dry_run_flow():
    os.environ["SUPABASE_PIPELINE_DRY_RUN"] = "true"
    result = run_sig_test_001(dry_run=True, reset=True)
    assert result["ok"] is True
    assert result["signal_id"] == "sig-test-001"
    assert result["gate_decision"] in ("APPROVE", "REDUCE_RISK")
    assert result["activity_events"] >= 5
    expected = {
        "SIGNAL_CREATED",
        "SIGNAL_CHECKED",
        "LOT_CALCULATED",
        "SIGNAL_SEEDED",
        "SIGNAL_PUBLISHED",
    }
    assert expected.issubset(set(result["event_types"]))


def test_build_step_payloads_has_context_fields():
    os.environ["SUPABASE_PIPELINE_DRY_RUN"] = "true"
    run_sig_test_001(dry_run=True, reset=True)
    payloads = build_step_payloads("sig-test-001", "published")
    assert "error" not in payloads
    row = payloads["signals"][0]
    assert row["signal_id"] == "sig-test-001"
    assert row.get("dxy_context", {}).get("source") in ("mock", "yahoo_finance", "live")
    assert row.get("us10y_context", {}).get("direction") in ("bullish", "bearish", "neutral")
    assert isinstance(row.get("spread_log"), list)
