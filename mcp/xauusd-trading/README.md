# XAUUSD Trading MCP

Wraps `src/` for **Hermes Agent**. See **[docs/hermes-mcp-setup.md](../docs/hermes-mcp-setup.md)** (tiếng Việt).

## Quick start

```bash
pip install mcp
python tests/run_tests.py
python src/main.py
python mcp/xauusd-trading/server.py   # stdio — Ctrl+C to stop
```

## Hermes Desktop

| Field | Value |
|-------|-------|
| Command | `python` |
| Args | `mcp/xauusd-trading/server.py` |
| CWD | repo root |

Example config: `hermes-mcp.example.json`

## Tools (11)

`replay_signals` · `check_signal` · `calc_lot` · `seed_signal` · `publish_signal` · `close_signal` · `promote_setup` · `start_forward_test` · `forward_test_check` · `dashboard` · `brain`

## Replay data

- `data/replay/london-breakout.json` — 30 signals, passes gate
- `data/replay/ny-reversal.json` — fails gate (demo)
