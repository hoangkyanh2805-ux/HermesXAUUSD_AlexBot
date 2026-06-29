#!/usr/bin/env python3
"""
XAUUSD Trading MCP Server — Hermes Agent integration.

Install: pip install mcp
Run:     python mcp/xauusd-trading/server.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import TextContent, Tool
except ImportError:
    print("Install MCP SDK: pip install mcp", file=sys.stderr)
    raise SystemExit(1)

from src.forward_test import check_forward_test_stale, start_forward_test
from src.signal_replay import replay_signals
from src.telegram_router import route_command

server = Server("xauusd-trading")

TOOLS = [
    Tool(
        name="replay_signals",
        description="Signal replay gate (backtest equivalent). Args: setup_name e.g. london-breakout",
        inputSchema={
            "type": "object",
            "properties": {"setup_name": {"type": "string"}},
            "required": ["setup_name"],
        },
    ),
    Tool(
        name="check_signal",
        description="Market + Signal Room validate. Args: signal_id",
        inputSchema={
            "type": "object",
            "properties": {"signal_id": {"type": "string"}},
            "required": ["signal_id"],
        },
    ),
    Tool(
        name="calc_lot",
        description="Lot Room. Args: signal_id, equity, tier (conservative|standard|aggressive)",
        inputSchema={
            "type": "object",
            "properties": {
                "signal_id": {"type": "string"},
                "equity": {"type": "number"},
                "tier": {"type": "string"},
            },
            "required": ["signal_id", "equity", "tier"],
        },
    ),
    Tool(
        name="seed_signal",
        description="Seeding Room. Args: signal_id",
        inputSchema={
            "type": "object",
            "properties": {"signal_id": {"type": "string"}},
            "required": ["signal_id"],
        },
    ),
    Tool(
        name="publish_signal",
        description="Simulated publish — Alex approval required. Args: signal_id, alex_approved (bool)",
        inputSchema={
            "type": "object",
            "properties": {
                "signal_id": {"type": "string"},
                "alex_approved": {"type": "boolean"},
            },
            "required": ["signal_id", "alex_approved"],
        },
    ),
    Tool(
        name="close_signal",
        description="Journal + Brain. Args: signal_id, result, pnl, lesson",
        inputSchema={
            "type": "object",
            "properties": {
                "signal_id": {"type": "string"},
                "result": {"type": "string"},
                "pnl": {"type": "number"},
                "lesson": {"type": "string"},
            },
            "required": ["signal_id", "result", "pnl", "lesson"],
        },
    ),
    Tool(
        name="promote_setup",
        description="Promotion lifecycle. Args: setup_name, status (replay_passed|forward_test|live)",
        inputSchema={
            "type": "object",
            "properties": {
                "setup_name": {"type": "string"},
                "status": {"type": "string"},
            },
            "required": ["setup_name", "status"],
        },
    ),
    Tool(
        name="start_forward_test",
        description="Start forward test for setup after replay_passed. Args: setup_name",
        inputSchema={
            "type": "object",
            "properties": {"setup_name": {"type": "string"}},
            "required": ["setup_name"],
        },
    ),
    Tool(
        name="forward_test_check",
        description="Check forward test status (notify only, no auto-promote)",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="dashboard",
        description="IB Signal Dashboard summary",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="brain",
        description="XAUUSD AI Brain from journal only",
        inputSchema={"type": "object", "properties": {}},
    ),
]


@server.list_tools()
async def list_tools() -> list[Tool]:
    return TOOLS


def _run(cmd: str) -> str:
    return json.dumps(route_command(cmd), indent=2, ensure_ascii=False)


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    args = arguments or {}

    if name == "replay_signals":
        text = _run(f"/replay {args['setup_name']}")
    elif name == "check_signal":
        text = _run(f"/check_signal {args['signal_id']}")
    elif name == "calc_lot":
        text = _run(f"/calc_lot {args['signal_id']} {args['equity']} {args['tier']}")
    elif name == "seed_signal":
        text = _run(f"/seed_signal {args['signal_id']}")
    elif name == "publish_signal":
        flag = "yes" if args.get("alex_approved") else "no"
        text = _run(f"/publish_signal {args['signal_id']} {flag}")
    elif name == "close_signal":
        text = _run(
            f"/close_signal {args['signal_id']} {args['result']} {args['pnl']} {args.get('lesson', '')}"
        )
    elif name == "promote_setup":
        text = _run(f"/promote_setup {args['setup_name']} {args['status']}")
    elif name == "start_forward_test":
        result = start_forward_test(args["setup_name"])
        text = json.dumps(result, indent=2)
    elif name == "forward_test_check":
        text = json.dumps(check_forward_test_stale(), indent=2)
    elif name == "dashboard":
        text = _run("/dashboard")
    elif name == "brain":
        text = _run("/brain")
    else:
        text = json.dumps({"ok": False, "error": f"Unknown tool: {name}"})

    return [TextContent(type="text", text=text)]


async def main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
