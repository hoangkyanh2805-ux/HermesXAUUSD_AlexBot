# Agent OS Design — Master Index

> **Project:** Hermes XAUUSD IB Trading Desk  
> **Skill:** `agent-os-designer`  
> **Status:** Design complete — implementation not started (`src/` pending)

## Quick Links

| # | Deliverable | Document |
|---|-------------|----------|
| 1 | Agent room architecture | [agent-os-operating-model.md](./agent-os-operating-model.md) §1 |
| 2 | Agent loop diagram | [agent-os-operating-model.md](./agent-os-operating-model.md) §2 |
| 3 | Permission matrix | [permission-matrix.md](./permission-matrix.md) |
| 4 | Stop condition table | [agent-os-operating-model.md](./agent-os-operating-model.md) §5 |
| 5 | Failure mode table | [agent-os-operating-model.md](./agent-os-operating-model.md) §6 |
| 6 | Room prompts (×7) | [../workbook/rooms/](../workbook/rooms/) |
| 7 | MVP implementation plan | [agent-os-mvp-implementation.md](./agent-os-mvp-implementation.md) |
| 8 | First coding tasks | [first-coding-tasks.md](./first-coding-tasks.md) |

## Adapted Flow

```text
Hermes XAUUSD Agent → Telegram → XAUUSD Trading MCP → 7 Rooms
→ Signal Replay/Forward Test → IB Signal Dashboard → XAUUSD AI Brain
→ Alex IB Jarvis Vision (defer)
```

## Module Map

| Room | Prompt | Python module |
|------|--------|---------------|
| Market | `workbook/rooms/market-room.md` | `src/market_context.py` |
| Signal | `workbook/rooms/signal-room.md` | `src/signal_gate.py` |
| Lot | `workbook/rooms/lot-room.md` | `src/lot_calculator.py` |
| Seeding | `workbook/rooms/seeding-room.md` | `src/seeding_engine.py` |
| Journal | `workbook/rooms/journal-room.md` | `src/journal.py` |
| Dashboard | `workbook/rooms/dashboard-room.md` | `src/dashboard.py` |
| AI Brain | `workbook/rooms/ai-brain-room.md` | `src/ai_brain.py` |
| Orchestrator | — | `src/telegram_router.py` |

## Telegram Commands

`/check_signal` · `/calc_lot` · `/seed_signal` · `/update_signal` · `/close_signal` · `/dashboard` · `/brain`

## Next Action

Implement Task 0–1 per [first-coding-tasks.md](./first-coding-tasks.md).
