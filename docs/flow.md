# Flow — Hermes XAUUSD IB Trading Desk

Quick reference. Full detail: [Architecture](./architecture.md) | [Knowledge Asset](../knowledge/distilled/hermes-xauusd-ib-desk-knowledge-asset.md)

## 8-Layer Stack

```text
Hermes XAUUSD Agent
  → Telegram DM / Signal Group
  → XAUUSD Trading MCP
  → Strategy Rooms (Market | Signal | Lot | Seeding | Journal)
  → Signal Replay / Forward Test
  → IB Signal Dashboard
  → XAUUSD AI Brain
  → Alex IB Jarvis Vision (Phase 2+)
```

## 9-Step Core Use Case

```text
New signal
  1. Read market context       [Market Room]
  2. Check signal              [Signal Room]
  3. Approve / wait / reject   [Signal Room + Replay Gate]
  4. Calculate lot by group    [Lot Room]
  5. Generate seeding copy     [Seeding Room]
  6. Track live status         [Dashboard]
  7. Journal result            [Journal Room]
  8. Update dashboard          [Dashboard]
  9. Feed AI Brain             [Brain]
```

## Promotion Lifecycle

```text
draft → replay_passed → forward_test → live
```

## Room → MCP Tool Map

| Room | Primary tools |
|------|---------------|
| Market | `get_market_context` |
| Signal | `validate_signal`, `replay_signals`, `post_signal_to_telegram` |
| Lot | `calculate_lot_plan` |
| Seeding | `generate_seeding_copy` |
| Journal | `append_journal` |
| Brain | `update_brain` |
