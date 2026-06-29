# Project Brief — Hermes XAUUSD IB Trading Desk

## One-line Objective

Build an agent-operated IB signal desk where **Hermes XAUUSD Agent** processes each gold signal through five specialized rooms, validates via replay/forward test, publishes to Telegram, tracks on a dashboard, and learns through **XAUUSD AI Brain**.

## Problem

As a Forex IB focused on XAUUSD, Alex manually juggles market context, signal validation, lot sizing by client group, Telegram seeding, tracking, journaling, and learning from outcomes. This is slow, inconsistent, and hard to scale across global clients without sacrificing risk discipline or reputation.

## Target User / Buyer

| User | Need |
|------|------|
| **Alex (IB operator)** | Reliable signal pipeline with approval gates, audit trail, and compounding lessons |
| **Global clients (Telegram)** | Clear, trustworthy signals with appropriate lot guidance — no hype, no guarantees |

## Desired Outcome

A working **AI agent operating system** adapted from the [Hermes Agent trading desk video](https://www.youtube.com/watch?v=MbfuJZZ01IU) — keeping the 8-layer architecture, replacing quant backtest with IB signal replay, and organizing work into five IB strategy rooms.

## Success Metrics

| Type | Metric |
|------|--------|
| **North-star** | One sample XAUUSD signal completes all 9 core-use-case steps end-to-end |
| **Activation** | Replay gate blocks bad setups before Telegram publish |
| **Quality** | Dashboard shows signal decision + journal + rolling stats |
| **Learning** | Brain accumulates ≥1 outcome + pairing per closed signal |
| **Safety** | Zero broker execution, zero password handling, zero profit guarantees in copy |

## In Scope (MVP)

- Hermes XAUUSD Agent as central operator
- Telegram DM (manual) + Signal Group (publish target)
- XAUUSD Trading MCP (8 core tools)
- 5 Strategy Rooms: Market, Signal, Lot, Seeding, Journal
- Signal Replay / Forward Test quality gate
- IB Signal Dashboard (read-only)
- XAUUSD AI Brain (`outcomes.jsonl`, `pairings.md`)
- Workbook missions + 1 cron job
- Human approval gate for Telegram publish

## Out of Scope (Hard Non-Goals)

- Content Engine, X Funnel Pack, BioLink funnel
- Full CRM
- Real trade execution API
- Client password / credential handling
- Guaranteed profit claims in any copy
- Overtrading / signal spam optimization
- Alex IB Jarvis Vision (Phase 2+)
- TradingView / Pine automation (optional manual lane later)

## Constraints

| Area | Constraint |
|------|------------|
| **Architecture** | Keep video's 8-layer flow; adapt names only where IB requires |
| **Risk** | Every risky action needs human approval — especially Telegram publish |
| **Build** | Smallest buildable first version; mock data OK where integrations not ready |
| **Compliance tone** | Education framing; forward test + risk control always visible |
| **Team** | Solo operator (Alex) + Hermes Agent |
| **Infrastructure** | Hermes Agent + Desktop, Telegram, MCP server, local/JSON storage for MVP |

## Source Materials

| Source | Type | Why it matters |
|--------|------|----------------|
| `knowledge/distilled/hermes-xauusd-ib-desk-knowledge-asset.md` | Distilled framework | Primary project map, rooms, use case, MVP |
| `knowledge/raw/video-notes/hermes-agent-trading-desk-youtube.md` | Raw notes | Original Hermes desk architecture reference |
| [YouTube MbfuJZZ01IU](https://www.youtube.com/watch?v=MbfuJZZ01IU) | Video case study | 8-layer agent desk pattern |

## Assumptions

1. Hermes Agent + Desktop is installed and connectable to Telegram.
2. MVP can use mock market data and historical signal CSV/JSON for replay.
3. One test Signal Group is sufficient for MVP publish verification.
4. Client groups are defined in config (conservative / standard) — not a CRM.
5. Alex approves first live publishes manually until pipeline is trusted.

## Open Questions

| # | Question | Default for MVP |
|---|----------|-----------------|
| 1 | Replay gate thresholds (min win rate, avg R)? | 55% win rate, 1.5 avg R, max 15% drawdown — tune after first replay |
| 2 | Forward test duration before `live`? | 7 days paper track (Phase 2 automation) |
| 3 | Telegram topics per room or repo folders only? | Repo folders for MVP; topics optional |
| 4 | Dashboard tech (static HTML vs Vite)? | Static HTML reading JSON — fastest MVP |

## Related Docs

- [Requirements](./requirements.md)
- [Architecture](./architecture.md)
- [MVP Build Map](./mvp-build-map.md)
- [First Sprint](./first-sprint.md)
- [SOP / Ops Runbook](./sop-ops-runbook.md)
