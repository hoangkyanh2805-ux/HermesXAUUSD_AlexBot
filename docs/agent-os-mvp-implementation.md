# MVP Implementation Plan — Agent OS (Cursor)

> Implements [Agent OS Operating Model](./agent-os-operating-model.md) Phase 1–3.  
> **No broker execution. No passwords. No publish without Alex approval.**

## Target Structure

```text
hermes-xauusd-ib-desk/
├── src/
│   ├── market_context.py      # Market Room
│   ├── signal_gate.py         # Signal Room
│   ├── lot_calculator.py      # Lot Room
│   ├── seeding_engine.py      # Seeding Room
│   ├── journal.py             # Journal Room
│   ├── dashboard.py           # Dashboard Room
│   ├── ai_brain.py            # AI Brain Room
│   ├── telegram_router.py     # Command router
│   └── __init__.py
├── tests/
│   ├── test_signal_gate.py
│   ├── test_lot_calculator.py
│   ├── test_seeding_engine.py
│   ├── test_journal.py
│   ├── test_dashboard.py
│   ├── test_ai_brain.py
│   └── test_telegram_router.py
├── workbook/rooms/            # Room prompts (7 files)
├── mcp/xauusd-trading/        # MCP wrapper over src/ (Phase 2)
└── strategy-rooms/            # Room data (exists)
```

## Phase A — Core Modules (Week 1)

| Order | Module | Room | Depends on |
|-------|--------|------|------------|
| A1 | `market_context.py` | Market | — |
| A2 | `signal_gate.py` | Signal | A1 |
| A3 | `lot_calculator.py` | Lot | A2 approve |
| A4 | `seeding_engine.py` | Seeding | A2, A3 |
| A5 | `journal.py` | Journal | — |
| A6 | `dashboard.py` | Dashboard | all readers |
| A7 | `ai_brain.py` | Brain | A5 |
| A8 | `telegram_router.py` | Orchestrator | A1–A7 |

**Exit criteria:** CLI can run full loop on `sample-001.json` without Telegram API.

## Phase B — Telegram + Dashboard UI (Week 2)

| Order | Task | Output |
|-------|------|--------|
| B1 | Wire `telegram_router` to bot webhook/polling stub | Commands respond |
| B2 | Human approval gate before publish | Block without Alex flag |
| B3 | Static dashboard HTML reading `dashboard/state.json` | `/dashboard` view |
| B4 | MCP wrapper exposing src functions | Hermes integration |

**Exit criteria:** E2E demo with test group + human-approved publish.

## Phase C — Hardening (Week 3)

- Replay dataset (30 signals)
- Integration tests for stop conditions S1–S14
- Cron forward-test stale check (notify only)
- Docs update in `docs/mvp-build-map.md`

## Module Interface Contract

Each module exposes pure functions returning `dict` with `{ "ok": bool, "data": ..., "error": ... }`.

```python
# Example
from src.signal_gate import check_signal
result = check_signal(signal_id="sig-001", market_context=ctx)
# result["data"]["decision"] in ("approve", "wait", "reject")
```

## Telegram Router Command Map

| Command | Handler chain |
|---------|---------------|
| `/check_signal` | market_context → signal_gate |
| `/calc_lot` | lot_calculator (gate: approved) |
| `/seed_signal` | seeding_engine (gate: approved + lot) |
| `/update_signal` | signal_gate.track + dashboard.update |
| `/close_signal` | journal.append → dashboard.update → ai_brain.learn |
| `/dashboard` | dashboard.summary |
| `/brain` | ai_brain.summary |

## Acceptance Criteria (Agent OS MVP)

- [ ] All 7 Telegram commands route correctly
- [ ] S1–S4 stop conditions covered by tests
- [ ] Brain refuses learn without journal (S12)
- [ ] Dashboard shows: status, lot, PnL, journal, lessons
- [ ] No execution, passwords, CRM, funnel code paths
- [ ] One E2E signal: check → lot → seed → (approve) → track → close → brain

## Defer

- Alex IB Jarvis Vision
- Real market data API
- Automated Telegram publish
- Broker execution
