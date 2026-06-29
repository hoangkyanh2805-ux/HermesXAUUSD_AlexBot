# Architecture — Hermes XAUUSD IB Trading Desk

## Overview

Agent-operated IB signal desk following the **8-layer Hermes desk pattern**, adapted for XAUUSD gold signals. Hermes orchestrates; MCP executes; rooms isolate concerns; dashboard displays; brain persists lessons.

```text
┌─────────────────────────────────────────────────────────────────┐
│                    Hermes XAUUSD Agent                          │
│              (orchestrator + long memory + SOP)                 │
└───────────────────────────┬─────────────────────────────────────┘
                            │
         ┌──────────────────┼──────────────────┐
         ▼                  ▼                  ▼
┌─────────────────┐ ┌───────────────┐ ┌─────────────────┐
│    Telegram     │ │ Hermes Desktop│ │ XAUUSD Trading  │
│  DM + Signal    │ │  ops / debug  │ │      MCP        │
│     Group       │ │  model/cron   │ │   (8 tools)     │
└────────┬────────┘ └───────────────┘ └────────┬────────┘
         │                                      │
         │         ┌────────────────────────────┤
         │         ▼                            │
         │  ┌──────────────────────────────────────────────────┐
         │  │              Strategy Rooms                       │
         │  │  Market → Signal → Lot → Seeding → Journal       │
         │  └──────────────────────┬───────────────────────────┘
         │                         │
         │         ┌───────────────┼───────────────┐
         │         ▼               ▼               ▼
         │  ┌────────────┐ ┌─────────────┐ ┌─────────────┐
         │  │  Replay /  │ │ IB Signal   │ │  XAUUSD     │
         │  │  Forward   │ │ Dashboard   │ │  AI Brain   │
         │  │   Test     │ │ (read-only) │ │ (persist)   │
         │  └────────────┘ └─────────────┘ └─────────────┘
         │                                      │
         └──────────────────────────────────────┘
                            │
                   [Phase 2+: Alex IB Jarvis Vision]
```

## Signal Pipeline (Sequential)

```text
                    ┌─────────────────┐
  signal draft ───► │   Market Room   │──► market_context.json
                    └────────┬────────┘
                             ▼
                    ┌─────────────────┐
                    │   Signal Room   │──► validate_signal()
                    └────────┬────────┘     signal_decision.json
                             │
                    ┌────────▼────────┐
                    │  Replay Gate    │──► replay_signals() → pass/fail
                    └────────┬────────┘
                             │ approve + live
                    ┌────────▼────────┐
                    │    Lot Room     │──► lot_plan.json
                    └────────┬────────┘
                             ▼
                    ┌─────────────────┐
                    │  Seeding Room   │──► seeding_messages.md
                    └────────┬────────┘
                             ▼
              ┌──────────────────────────┐
              │  [HUMAN APPROVAL GATE]   │
              └────────────┬─────────────┘
                           ▼
                    ┌─────────────────┐
                    │ post_signal_to  │──► Telegram Signal Group
                    │   _telegram     │
                    └────────┬────────┘
                             ▼
                    ┌─────────────────┐
                    │    Dashboard    │──► track live status
                    └────────┬────────┘
                             │ signal closed
                    ┌────────▼────────┐
                    │  Journal Room   │──► append_journal()
                    └────────┬────────┘
                             ▼
                    ┌─────────────────┐
                    │   AI Brain      │──► update_brain()
                    └─────────────────┘
```

## Component Specifications

### Hermes XAUUSD Agent

- **Role:** Central operator; routes missions to rooms via MCP
- **Interfaces:** Telegram chat, Cursor (dev), Hermes Desktop (ops)
- **Memory:** Hermes long context + `knowledge/brain/` persistence
- **Policy:** Defined in `agents/hermes-xauusd-agent.md` + `.cursor/rules/`

### Telegram Layer

| Channel | Direction | Content |
|---------|-----------|---------|
| Operator → Hermes | Inbound | Missions, approvals, status queries |
| Hermes → Signal Group | Outbound | Approved signals + seeding (gated) |
| DM | Manual | Client support — not automated in MVP |

### XAUUSD Trading MCP

```
mcp/xauusd-trading/
├── src/           # MCP server entry
└── tools/
    ├── market.ts      # get_market_context
    ├── signal.ts      # validate_signal, replay_signals
    ├── lot.ts         # calculate_lot_plan
    ├── seeding.ts     # generate_seeding_copy
    ├── telegram.ts    # post_signal_to_telegram
    ├── journal.ts     # append_journal
    └── brain.ts       # update_brain
```

**Design principle:** Agent never bypasses MCP for desk actions.

### Strategy Rooms

| Room | Path | STATUS lifecycle |
|------|------|------------------|
| Market | `strategy-rooms/market-room/` | active |
| Signal | `strategy-rooms/signal-room/` | draft → replay_passed → forward_test → live |
| Lot | `strategy-rooms/lot-room/` | active |
| Seeding | `strategy-rooms/seeding-room/` | active |
| Journal | `strategy-rooms/journal-room/` | active |

Each room: `config.yaml` + `STATUS` file + room-specific outputs.

### Quality Control — Replay / Forward Test

- **Replay:** Historical signals vs price data → metrics + pass/fail
- **Forward test:** Paper track before `live` promotion (manual MVP; automated Phase 2)
- **Gate location:** Between Signal Room validation and publish

**Default gate thresholds (tunable):**

| Metric | Pass |
|--------|------|
| Win rate | ≥ 55% |
| Avg R | ≥ 1.5 |
| Max drawdown | ≤ 15% |
| Min sample | ≥ 20 trades in replay set |

### IB Signal Dashboard

- **Type:** Read-only static page (MVP)
- **Data sources:**
  - `strategy-rooms/signal-room/signals/`
  - `strategy-rooms/signal-room/replay/latest.json`
  - `strategy-rooms/journal-room/entries.jsonl`
  - `knowledge/brain/outcomes.jsonl`
- **Panels:** Active signal, decision log, W/L stats (rolling 30), room STATUS

### XAUUSD AI Brain

```
knowledge/brain/
├── outcomes.jsonl    # append-only signal results
├── pairings.md       # setup ↔ session ↔ condition learnings
└── setups.md         # gold setup catalog
```

**Learning model:** After each closed signal, append outcome + update pairing if pattern confirmed or refuted.

## Approval Gates

| Gate | Trigger | Approver | Blocks |
|------|---------|----------|--------|
| Replay gate | New setup promotion | Automatic (metrics) | Publish |
| Signal decision | validate_signal | Agent + rules | Lot / publish |
| Telegram publish | post_signal_to_telegram | **Human (MVP)** | Client visibility |
| Forward test | draft → live | Operator review | Live status |

## Deferred — Alex IB Jarvis Vision (Phase 2+)

Conversational command center reading brain + dashboard. Not in MVP architecture. No new write paths — query only.

## Repository Layout

See `knowledge/distilled/hermes-xauusd-ib-desk-knowledge-asset.md` §9 for full tree.

## Technology Choices (MVP)

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Agent runtime | Hermes Agent + Desktop | Matches source video pattern |
| Tool protocol | MCP | Structured, auditable agent actions |
| Storage | JSON / JSONL / YAML files | Simplest solo-operator MVP |
| Dashboard | Static HTML + fetch JSON | No backend required |
| Cron | Hermes scheduler | Forward-test status check |

## Security Boundaries

```text
IN SCOPE:  signal ops, lot calculation, Telegram publish, journaling
OUT SCOPE: broker credentials, client passwords, order execution
```

Agent rules and MCP must reject requests outside scope.

## Related Docs

- [Project Brief](./project-brief.md)
- [Requirements](./requirements.md)
- [MVP Build Map](./mvp-build-map.md)
- [Guardrails](./guardrails.md)
