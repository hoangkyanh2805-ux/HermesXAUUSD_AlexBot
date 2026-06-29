#!/usr/bin/env python3
"""Local CLI demo — Hermes XAUUSD IB Trading Desk MVP (Phase C)."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.ai_brain import print_brain
from src.common import data_path, save_json
from src.dashboard import export_state, print_dashboard
from src.telegram_router import print_command_result, route_command


def _reset_demo_data() -> None:
    save_json(data_path("journal.json"), {"entries": []})
    save_json(data_path("publish_log.json"), {"publishes": []})
    save_json(
        data_path("setups.json"),
        {
            "setups": {
                "london-breakout": {
                    "status": "draft",
                    "replay_required": True,
                    "description": "London session breakout",
                },
                "ny-reversal": {
                    "status": "draft",
                    "replay_required": True,
                    "description": "NY reversal (fails replay)",
                },
            }
        },
    )
    save_json(
        data_path("signals.json"),
        {
            "signals": [
                {
                    "signal_id": "sig-001",
                    "pair": "XAUUSD",
                    "direction": "buy",
                    "entry_low": 2344.0,
                    "entry_high": 2346.0,
                    "stop_loss": 2340.0,
                    "take_profits": [2355.0],
                    "session": "london",
                    "news_risk": "low",
                    "market_bias": "bullish",
                    "setup_name": "london-breakout",
                    "status": "open",
                    "lot_category": None,
                },
                {
                    "signal_id": "sig-reject-demo",
                    "pair": "XAUUSD",
                    "direction": "sell",
                    "entry_low": 2350.0,
                    "entry_high": 2352.0,
                    "stop_loss": None,
                    "take_profits": [2340.0],
                    "session": "london",
                    "news_risk": "low",
                    "market_bias": "bearish",
                    "setup_name": "invalid-no-sl",
                    "status": "draft",
                    "lot_category": None,
                },
            ]
        },
    )


def run_demo() -> None:
    _reset_demo_data()
    print("\n" + "=" * 60)
    print("  HERMES XAUUSD IB DESK - Phase C (Replay + Pipeline)")
    print("=" * 60)

    steps = [
        ("1. Replay london-breakout (30 signals)", "/replay london-breakout"),
        ("2. Replay fail demo ny-reversal", "/replay ny-reversal"),
        ("3. Forward test start", "/forward_test start london-breakout"),
        ("4. Promote setup -> live (demo skip 7d)", "/promote_setup london-breakout live"),
        ("5. Check signal", "/check_signal sig-001"),
        ("6. Calculate lot", "/calc_lot sig-001 10000 standard"),
        ("7. Generate seeding", "/seed_signal sig-001"),
        ("8. Publish (Alex approves)", "/publish_signal sig-001 yes"),
        ("9. Close signal -> journal", "/close_signal sig-001 win 210 London breakout worked"),
        ("10. Forward test check", "/forward_test check"),
        ("11. Dashboard", "/dashboard"),
        ("12. AI Brain", "/brain"),
    ]

    for label, cmd in steps:
        print(f"\n--- {label} ---")
        print(f">>> {cmd}")
        print_command_result(route_command(cmd))

    print("\n--- Dashboard ---")
    print_dashboard()
    print("\n--- AI Brain ---")
    print_brain()

    export_state()
    print("\nPhase C demo complete.")
    print("Hermes MCP: docs/hermes-mcp-setup.md")
    print("Dashboard HTML: dashboard/ib-signals/index.html\n")


if __name__ == "__main__":
    run_demo()
