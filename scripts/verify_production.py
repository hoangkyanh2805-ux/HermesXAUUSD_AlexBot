#!/usr/bin/env python3
"""Production readiness verification — Phase G + operator checks."""

from __future__ import annotations

import json
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.market_context import get_market_context
from src.pipeline_test_flow import run_sig_test_001
from src.supabase_sync import get_supabase_config, sync_all


def _step(name: str, ok: bool, detail: str = "") -> dict:
    return {"step": name, "ok": ok, "detail": detail}


def _run_tests() -> dict:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "tests" / "run_tests.py")],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    ok = proc.returncode == 0
    tail = proc.stdout.strip().splitlines()[-1] if proc.stdout else proc.stderr
    return _step("unit_tests", ok, tail)


def _live_market() -> dict:
    ctx = get_market_context(live=True)
    source = ctx.get("source", "mock")
    ok = source == "live" or ctx.get("live_fetch_error")
    return _step(
        "live_market_data",
        source == "live",
        f"source={source} dxy={ctx.get('dxy_direction')} us10y={ctx.get('us10y_direction')}",
    )


def _supabase_counts() -> dict:
    cfg = get_supabase_config()
    if not cfg["url"] or not cfg["service_key"]:
        return _step("supabase_counts", False, "Missing supabase/.env")

    counts: dict[str, int] = {}
    for table in ("signals", "activity_logs", "spread_audit"):
        url = f"{cfg['url']}/rest/v1/{table}?select=id&limit=1"
        req = urllib.request.Request(
            url,
            headers={
                "apikey": cfg["service_key"],
                "Authorization": f"Bearer {cfg['service_key']}",
                "Prefer": "count=exact",
            },
            method="GET",
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                raw = resp.headers.get("Content-Range", "")
                # format: 0-9/10
                total = int(raw.split("/")[-1]) if "/" in raw else 0
                counts[table] = total
        except urllib.error.HTTPError as e:
            return _step("supabase_counts", False, f"{table}: HTTP {e.code}")

    ok = counts.get("signals", 0) >= 1
    return _step("supabase_counts", ok, json.dumps(counts))


def _sync() -> dict:
    result = sync_all()
    ok = bool(result.get("ok"))
    return _step("supabase_sync", ok, json.dumps(result.get("counts", {})))


def _sig_test_live() -> dict:
    result = run_sig_test_001(dry_run=False, reset=True)
    ok = bool(result.get("ok"))
    detail = f"events={result.get('activity_events')} decision={result.get('gate_decision')}"
    return _step("sig_test_001_live", ok, detail)


def _metabase_checklist() -> dict:
    items = [
        "Open http://localhost:3000 — Metabase running",
        "Browse -> signals, activity_logs, volume_monthly",
        "SQL: select count(*) from signals;",
        "Create collection 'Hermes XAUUSD IB Desk'",
        "Paste SQL from metabase/cards.sql (20 cards)",
        "Add G10 footer: volume KPI display-only",
    ]
    return _step("metabase_dashboard", False, "MANUAL: " + " | ".join(items[:3]))


def main() -> int:
    steps = [
        _run_tests(),
        _live_market(),
        _sig_test_live(),
        _sync(),
        _supabase_counts(),
        _metabase_checklist(),
    ]
    report = {
        "ok": all(s["ok"] for s in steps if s["step"] != "metabase_dashboard"),
        "steps": steps,
        "note": "metabase_dashboard requires manual operator steps — see docs/metabase-phase5-dashboard.md",
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
