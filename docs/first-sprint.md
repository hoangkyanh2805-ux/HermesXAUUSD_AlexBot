# First Sprint — Hermes XAUUSD IB Trading Desk

## Sprint Goal

Complete **Phase 0 + Phase 1** from [MVP Build Map](./mvp-build-map.md): operating docs, folder scaffold, Telegram templates, and MCP tools for market context → validate → replay → lot → seeding — **without Telegram publish yet**.

## Sprint Duration

**2 weeks** (10 working days)

## Work Items

| # | Task | Owner | Output | Verification | Dependency |
|---|------|-------|--------|--------------|------------|
| 1 | Finalize docs package | Alex / Cursor | 6 docs in `docs/` | All cross-linked; guardrails G1–G9 present | — |
| 2 | Create cursor rules + agent prompt | Cursor | `.cursor/rules/`, `agents/` | Rules reference guardrails; room routing defined | #1 |
| 3 | Scaffold 5 strategy rooms | Cursor | `strategy-rooms/*/` + STATUS | Each room has config.yaml + STATUS | #1 |
| 4 | Init brain + sample signal | Cursor | `knowledge/brain/`, `sample-001.json` | Sample signal parses; brain files exist | #3 |
| 5 | Write telegram templates | Alex | `telegram/signal-format.md`, `seeding-guidelines.md` | No profit guarantees; standard signal layout | #1 |
| 6 | Write 5 workbook missions | Cursor | `workbook/mission-*.md` | One mission per pipeline stage | #1 |
| 7 | Bootstrap MCP server | Cursor | `mcp/xauusd-trading/` skeleton | Server starts; tool registry defined | #3 |
| 8 | Implement `get_market_context` | Cursor | tool + mock data | Returns valid JSON for london/ny sessions | #7 |
| 9 | Implement `validate_signal` | Cursor | tool | 3 test cases: approve, wait, reject | #7, #4 |
| 10 | Build replay dataset | Alex | 30 historical signals CSV/JSON | ≥20 rows with outcomes | — |
| 11 | Implement `replay_signals` | Cursor | tool + gate logic | pass/fail matches expected on 2 datasets | #10 |
| 12 | Implement `calculate_lot_plan` | Cursor | tool + `client-groups.example.yaml` | Conservative lot < standard lot; caps enforced | #7 |
| 13 | Implement `generate_seeding_copy` | Cursor | tool | Output passes seeding guidelines lint | #5, #7 |
| 14 | Run pipeline steps 1–5 manually | Alex | console log / saved JSON files | All 5 room outputs exist for sample-001 | #8–13 |
| 15 | Document gaps + Phase 2 plan | Alex | notes in `docs/first-sprint.md` | Known gaps listed; publish gate design confirmed | #14 |

## Daily Check

- What moved? (room outputs, MCP tools completed)
- What is blocked? (Hermes install, Telegram bot, replay data)
- What changed in assumptions? (gate thresholds, client groups)
- What needs approval? (any seeding copy, any publish — none in this sprint)

## Done Criteria

**Files/docs created:**
- [ ] Full docs package (6 files)
- [ ] Cursor rules + agent prompt
- [ ] 5 strategy rooms scaffolded
- [ ] 5 workbook missions
- [ ] Telegram templates
- [ ] MCP server with 5 tools (market, validate, replay, lot, seeding)
- [ ] Replay dataset (30 signals)
- [ ] `docs/client-groups.example.yaml`

**Core workflow demonstrated:**
- [ ] Sample signal `sig-001` produces: `market_context.json`, `signal_decision.json`, `replay_result.json`, `lot_plan.json`, `seeding_messages.md`
- [ ] Bad replay dataset returns `pass: false`

**Tests/checks passed:**
- [ ] Seeding copy has zero profit guarantee phrases
- [ ] Lot plan respects risk caps
- [ ] validate_signal rejects RR < 1:1.5

**Known gaps documented:**
- [ ] Telegram publish not implemented (Phase 2)
- [ ] Dashboard not implemented (Phase 2)
- [ ] Journal + brain writers not implemented (Phase 3)
- [ ] Human approval gate for publish — design confirmed, build next sprint

## Demo Script (End of Sprint 1)

```text
1. Open sample signal: strategy-rooms/signal-room/signals/sample-001.json
2. Run get_market_context → show market_context.json
3. Run validate_signal → show approve/wait/reject
4. Run replay_signals on london-breakout dataset → show pass/fail
5. On pass: run calculate_lot_plan → show conservative vs standard lots
6. Run generate_seeding_copy → review with Alex for tone
7. Show all JSON outputs in strategy-rooms/ — no Telegram post yet
8. Walk through Phase 2 plan: publish + dashboard + human gate
```

## Sprint 2 Preview (Not This Sprint)

- `post_signal_to_telegram` + human approval gate
- IB Signal Dashboard (static HTML)
- `append_journal` + `update_brain`
- End-to-end 9-step demo with test Signal Group
- 1 cron job for forward-test status
