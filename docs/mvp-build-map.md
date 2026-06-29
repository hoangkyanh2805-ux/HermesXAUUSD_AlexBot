# MVP Build Map — Hermes XAUUSD IB Trading Desk

## Binding Constraint

No end-to-end signal pipeline exists yet. Value is blocked until one sample XAUUSD signal can flow through all 9 steps with replay gate, human-approved publish, dashboard visibility, and brain update.

## Delete / Defer

| Item | Decision | Reason |
|------|----------|--------|
| Alex IB Jarvis Vision | **Defer Phase 2+** | Capstone; needs brain + dashboard first |
| Broker execution API | **Delete from MVP** | Out of scope; reputation + security risk |
| Client password handling | **Delete permanently** | Security boundary |
| CRM | **Defer** | Telegram + client-groups.yaml sufficient |
| Content Engine / X Funnel / BioLink | **Delete** | Not IB desk |
| TradingView / Pine automation | **Defer** | Manual research lane optional |
| Telegram DM auto-bot | **Defer** | Human DM in MVP |
| Multi-room parallel cron | **Defer** | One room, one cron in MVP |
| Database | **Defer** | File-based storage for MVP |
| Profit guarantee copy | **Delete** | Guardrail G4 |

---

## Phase 0 — Ground Truth (Docs + Scaffold)

**Goal:** Operating context exists before any code. Project cannot drift.

**Deliverables:**
- [x] `docs/project-brief.md`
- [x] `docs/requirements.md`
- [x] `docs/architecture.md`
- [x] `docs/mvp-build-map.md` (this file)
- [x] `docs/first-sprint.md`
- [x] `docs/sop-ops-runbook.md`
- [x] `docs/guardrails.md`
- [x] `docs/flow.md`
- [x] `.cursor/rules/hermes-xauusd-desk.mdc`
- [x] `agents/hermes-xauusd-agent.md`
- [ ] `strategy-rooms/` scaffold (5 rooms + `_template/`)
- [ ] `knowledge/brain/` init files
- [ ] `telegram/signal-format.md` + `seeding-guidelines.md`

**Acceptance criteria:**
- [ ] All docs cross-link correctly
- [ ] Guardrails G1–G9 documented and reflected in cursor rules
- [ ] Folder scaffold matches architecture doc
- [ ] One sample signal JSON exists in `signal-room/signals/sample-001.json`

---

## Phase 1 — Core Loop (MCP + Rooms + Gate)

**Goal:** Signal flows through rooms 1–4 with replay gate blocking bad setups.

**Deliverables:**
- `mcp/xauusd-trading/` server with tools:
  - `get_market_context`
  - `validate_signal`
  - `replay_signals`
  - `calculate_lot_plan`
  - `generate_seeding_copy`
- `workbook/` — 5 mission prompts
- Replay gate with pass/fail JSON output
- Sample replay dataset (≥20 historical signals)

**Acceptance criteria:**
- [ ] `get_market_context` returns valid `market_context.json`
- [ ] `validate_signal` returns approve / wait / reject for 3 test cases
- [ ] `replay_signals` returns `pass: false` for bad dataset
- [ ] `replay_signals` returns `pass: true` for good dataset
- [ ] `calculate_lot_plan` respects client group risk caps
- [ ] `generate_seeding_copy` contains no profit guarantee phrases
- [ ] Pipeline runs steps 1–5 without Telegram publish

---

## Phase 2 — Publish + Track (Telegram + Dashboard)

**Goal:** Approved signal publishes to test group; dashboard shows state.

**Deliverables:**
- `post_signal_to_telegram` MCP tool
- `telegram/signal-format.md` implemented in tool output
- Human approval gate wrapper (operator confirms before post)
- `dashboard/ib-signals/` read-only page
- Cron job: forward-test status check (30 min)

**Acceptance criteria:**
- [ ] Publish blocked when `decision != approve` or `status != live`
- [ ] Human gate required before every MVP publish
- [ ] Test Signal Group receives formatted message
- [ ] Dashboard shows: last signal, decision, room STATUS, replay metrics
- [ ] Cron visible and disable-able in Hermes Desktop

---

## Phase 3 — Learn + Close Loop (Journal + Brain)

**Goal:** Closed signal updates journal, brain, and dashboard stats.

**Deliverables:**
- `append_journal` MCP tool
- `update_brain` MCP tool
- `knowledge/brain/outcomes.jsonl` + `pairings.md` writers
- End-to-end demo script

**Acceptance criteria:**
- [ ] Closing sample signal appends journal entry
- [ ] Brain receives outcome row + pairing note
- [ ] Dashboard reflects closed signal W/L
- [ ] **Full 9-step core use case completes once end-to-end**
- [ ] Demo script documented in `docs/first-sprint.md`

---

## Phase 4 — Packaging (Post-MVP — Not Sprint 1)

**Goal:** Harden for daily ops.

**Deliverables:**
- Forward test automation (7-day paper)
- Second signal setup (fork workflow)
- DM FAQ assist (read-only)
- Alex IB Jarvis Vision sketch (query brain + dashboard)

**Acceptance criteria:**
- [ ] 7-day forward test gate automates `forward_test → live` suggestion
- [ ] Fork workflow documented and tested once
- [ ] Jarvis prototype answers 3 desk status questions from brain data

---

## Critical Path

```text
1. Docs + guardrails + cursor rules          (Phase 0)
2. Room scaffold + sample signal           (Phase 0)
3. MCP: market + validate + replay         (Phase 1)
4. MCP: lot + seeding                        (Phase 1)
5. Telegram publish + human gate             (Phase 2)
6. Dashboard reader                          (Phase 2)
7. Journal + brain writers                   (Phase 3)
8. End-to-end demo                           (Phase 3)
```

## Risks

| Risk | Mitigation | Stop condition |
|------|------------|----------------|
| Hermes / Telegram setup friction | Follow video checklist; test bot in private chat first | Cannot send/receive after 2 debug sessions → pause build, fix infra |
| Replay data insufficient | Start with 30 synthetic historical signals | < 20 samples → do not promote any setup to live |
| Token burn from cron | One cron only; monitor in Desktop; document disable steps | > 2x expected daily tokens → disable cron, review missions |
| Seeding copy too promotional | `seeding-guidelines.md` + lint check in tool | Any profit guarantee phrase → block publish |
| Scope creep (CRM, execution) | Guardrails in cursor rules; defer list in every PR | New feature outside MVP map → reject or Phase 4 |
| Overtrading pressure | Optimize for quality metrics, not signal count | > 3 signals/day in MVP test → review gate thresholds |

## MVP Complete Definition

All Phase 0–3 acceptance criteria checked. Specifically:

1. One sample XAUUSD signal — 9 steps end-to-end
2. Replay gate blocked a bad setup (demonstrated)
3. Dashboard shows decision + journal + stats
4. Brain has ≥1 outcome + ≥1 pairing
5. Zero execution API, passwords, profit claims
