# Permission Matrix — Hermes XAUUSD IB Trading Desk

> See [Agent OS Operating Model](./agent-os-operating-model.md) for full room contracts.

## Legend

- ✅ Autonomous (agent/module may execute)
- ⚠️ Autonomous with checks (rules must pass)
- 🔒 Human approval required (Alex)
- ❌ Forbidden

## By Action

| Action | Autonomous | Human | Forbidden | Evidence / Notes |
|--------|------------|-------|-----------|------------------|
| Read market context | ✅ | — | — | `market_context.py` |
| Write `market_context.json` | ✅ | — | — | Overwrite per tick OK |
| Validate signal structure | ⚠️ | — | — | `signal_gate.py` |
| Run replay gate | ⚠️ | — | — | Pass/fail JSON logged |
| Auto-approve signal | ⚠️ | — | — | Only if S1–S7 pass |
| Reject signal | ⚠️ | — | — | Halts pipeline |
| Calculate lot by group | ⚠️ | — | — | Caps from yaml |
| Block recovery lot increase | ⚠️ | — | — | Hard reject |
| Generate seeding copy | ⚠️ | — | — | Lint required |
| Publish to Signal Group | — | 🔒 | — | MVP: every publish |
| Update live signal status | ✅ | — | — | `/update_signal` |
| Append journal on close | ⚠️ | — | — | Requires exit data |
| Rebuild dashboard state | ✅ | — | — | Read-only external view |
| Append brain outcome | ⚠️ | — | — | Journal must exist |
| Update pairings.md | ⚠️ | — | — | From journal only |
| Read `/dashboard` `/brain` | ✅ | — | — | Read-only |
| Promote setup to `live` | — | 🔒 | — | After replay pass |
| Change client-groups.yaml | — | 🔒 | — | Risk params |
| Create cron job | — | 🔒 | — | Token control |
| Broker order execution | — | — | ❌ | Phase not in scope |
| Store client passwords | — | — | ❌ | Security |
| CRM / funnel / content | — | — | ❌ | G9 |

## By Room

| Room | May write | May not write | Approval for |
|------|-----------|---------------|--------------|
| Market | `market-room/` | Other rooms | — |
| Signal | `signal-room/` | `telegram` publish | Publish |
| Lot | `lot-room/` | Signal decision | Recovery lots |
| Seeding | `seeding-room/` | Telegram directly | Publish |
| Journal | `journal-room/entries.jsonl` | Brain without journal | — |
| Dashboard | `dashboard/state.json` | Brain, journal | — |
| AI Brain | `knowledge/brain/` | Journal (source) | — |

## Default Rule

> If action affects **client-visible output**, **risk parameters**, or **closed-signal truth** → human approval or journal-source guard required.
