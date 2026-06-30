# README — Hermes XAUUSD IB Trading Desk

Agent-operated IB signal desk for XAUUSD / Gold.

## Start Here

1. [Project Brief](docs/project-brief.md)
2. [Architecture](docs/architecture.md)
3. [MVP Build Map](docs/mvp-build-map.md)
4. [First Sprint](docs/first-sprint.md)
5. [Guardrails](docs/guardrails.md)

## Knowledge

- [Knowledge Asset](knowledge/distilled/hermes-xauusd-ib-desk-knowledge-asset.md)
- [Flow](docs/flow.md)

## Agent

- [Hermes XAUUSD Agent](agents/hermes-xauusd-agent.md)
- Cursor rules: `.cursor/rules/hermes-xauusd-desk.mdc`

## Agent OS

- [Agent OS Operating Model](docs/agent-os-operating-model.md)
- [Permission Matrix](docs/permission-matrix.md)
- [First Coding Tasks](docs/first-coding-tasks.md)
- Room prompts: `workbook/rooms/`

## Status

**Phase D complete** — Risk-First Volume Desk (correlation filter, safety locks, lot formula, spread audit, volume KPI).  
**Phase E complete** — Sync `data/*.json` → Supabase + [Metabase setup](docs/supabase-metabase-setup.md).

```bash
python src/main.py              # Phase C demo (replay -> publish -> journal)
python tests/run_tests.py       # 31 tests
python scripts/sync_to_supabase.py --dry-run
pip install mcp
```
**Hermes:** [docs/hermes-mcp-setup.md](docs/hermes-mcp-setup.md)  
**Telegram bot (BotFather):** [docs/telegram-bot-setup.md](docs/telegram-bot-setup.md)

**Dashboard:** `dashboard/ib-signals/index.html`
