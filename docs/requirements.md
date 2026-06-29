# Requirements — Hermes XAUUSD IB Trading Desk

> First-principles requirements derived from `knowledge/distilled/hermes-xauusd-ib-desk-knowledge-asset.md`.

## 1. Business Outcome

Enable Alex to operate a **professional XAUUSD IB signal desk** with:

- Faster, consistent signal processing
- Visible track record for clients
- Compounding operational intelligence (AI Brain)
- Strong risk and reputation guardrails

**Not** maximizing signal volume or automating sales funnels.

## 2. User Workflows

### 2.1 Operator (Alex) — Primary

```text
New signal idea
  → trigger Hermes pipeline (Telegram or Cursor)
  → review market context
  → review approve/wait/reject decision
  → approve lot plan + seeding copy
  → [HUMAN GATE] approve Telegram publish
  → monitor live signal on dashboard
  → close signal → journal auto-updates → brain learns
```

### 2.2 Client (Telegram Signal Group)

- Receives approved signal in standard format
- Receives natural seeding context (education, session note — not hype)
- Sees consistent lot guidance by group tier (in message or pinned doc)

### 2.3 Client (Telegram DM) — MVP

- Human-operated support only
- No auto-bot, no CRM pipeline in MVP

### 2.4 Core Use Case (9 Steps) — Must Support

| Step | Action | Room / Layer |
|------|--------|--------------|
| 1 | Read market context | Market Room |
| 2 | Check the signal | Signal Room |
| 3 | Approve / wait / reject | Signal Room + QC gate |
| 4 | Calculate safe lot by client group | Lot Room |
| 5 | Generate natural Telegram seeding | Seeding Room |
| 6 | Track live signal status | Signal Room + Dashboard |
| 7 | Journal the result | Journal Room |
| 8 | Update dashboard | IB Signal Dashboard |
| 9 | Feed result into AI Brain | XAUUSD AI Brain |

## 3. System Layers (8-Layer Architecture)

| Layer | Component | Requirement |
|-------|-----------|-------------|
| 1 | Hermes XAUUSD Agent | Orchestrates rooms; long memory; follows SOP |
| 2 | Telegram | DM + Signal Group; command console |
| 3 | XAUUSD Trading MCP | All desk actions via structured tools |
| 4 | Strategy Rooms | 5 rooms with isolated config + STATUS |
| 5 | Signal Replay / Forward Test | QC before promotion |
| 6 | IB Signal Dashboard | Read-only tracking UI |
| 7 | XAUUSD AI Brain | Persistent outcomes + pairings |
| 8 | Alex IB Jarvis Vision | **Deferred** — read-only queries in Phase 2 |

## 4. Strategy Room Requirements

### Market Room

- **Input:** Symbol XAUUSD, timestamp
- **Output:** `market_context.json` — session, spread, volatility, news_risk
- **Rules:** Flag high news risk → downstream should prefer `wait` or `reject`

### Signal Room

- **Input:** Signal draft (entry, SL, TP, setup name, rationale)
- **Output:** `signal_decision.json` — approve | wait | reject + reason
- **Rules:** Min RR 1:1.5; must align with session; new setups require replay pass

### Lot Room

- **Input:** Approved signal + `client-groups.yaml`
- **Output:** `lot_plan.json` — lot per group (conservative, standard)
- **Rules:** Cap risk % per group; never exceed max exposure config

### Seeding Room

- **Input:** Approved signal + market context
- **Output:** `seeding_messages.md` — natural Telegram copy
- **Rules:** No guaranteed profit language; no overtrading encouragement; education tone

### Journal Room

- **Input:** Closed signal (result, R-multiple, notes)
- **Output:** `journal_entry` appended to `entries.jsonl`
- **Rules:** Every closed signal must produce a journal entry

## 5. XAUUSD Trading MCP — Tool Requirements

| Tool | Required | Description |
|------|----------|-------------|
| `get_market_context` | MVP | Return session, spread, volatility, news_risk |
| `validate_signal` | MVP | Return approve / wait / reject |
| `replay_signals` | MVP | Run replay; return win_rate, avg_r, max_dd, pass |
| `calculate_lot_plan` | MVP | Lot by client group |
| `generate_seeding_copy` | MVP | Natural Telegram messages |
| `post_signal_to_telegram` | MVP | Publish to Signal Group (gated) |
| `append_journal` | MVP | Write journal entry |
| `update_brain` | MVP | Append outcome + pairing note |

**MCP contract:** All tools return structured JSON. No prose-only responses for dashboard/brain ingestion.

## 6. Data Model

### Promotion lifecycle

```text
draft → replay_passed → forward_test → live
```

### Core entities

| Entity | Storage | Key fields |
|--------|---------|------------|
| Signal | `strategy-rooms/signal-room/signals/` | id, entry, sl, tp, setup, status |
| Market context | `strategy-rooms/market-room/` | session, spread, volatility, news_risk, ts |
| Signal decision | `strategy-rooms/signal-room/` | decision, reason, signal_id |
| Lot plan | `strategy-rooms/lot-room/` | groups[], lot, risk_pct |
| Replay result | `strategy-rooms/signal-room/replay/` | win_rate, avg_r, max_dd, pass |
| Journal entry | `strategy-rooms/journal-room/entries.jsonl` | signal_id, result, r, lesson |
| Brain outcome | `knowledge/brain/outcomes.jsonl` | ts, signal_id, result, r, session, setup, lesson |
| Brain pairing | `knowledge/brain/pairings.md` | setup ↔ session ↔ condition ↔ result |

## 7. Integrations

| Integration | MVP | Phase 2 |
|-------------|-----|---------|
| Hermes Agent + Desktop | Required | — |
| Telegram Bot API | Required (test group) | Production group |
| XAUUSD Trading MCP | Required | Extended tools |
| Market data feed | Mock / manual | Live quote API |
| Broker execution | **Never in MVP** | Evaluate later with separate project |
| TradingView / Pine | Manual research only | Optional lane |

## 8. Guardrails (Hard Requirements)

| ID | Rule |
|----|------|
| G1 | No Telegram publish unless `decision == approve` AND setup `status == live` |
| G2 | No broker execution API in this project phase |
| G3 | No client passwords, broker credentials, or auth tokens in agent scope |
| G4 | No guaranteed profit language in seeding or signal copy |
| G5 | No overtrading optimization — quality over volume |
| G6 | Human approval required for first N publishes (MVP: every publish) |
| G7 | `replay_signals` required before first promotion of any new setup |
| G8 | Journal + brain update required after every closed signal |
| G9 | No CRM, content engine, funnel, BioLink, X pack in repo |

## 9. Non-Functional Requirements

| Area | Requirement |
|------|-------------|
| **Auditability** | Every decision logged as JSON with timestamp |
| **Recoverability** | Brain + journal append-only; no destructive overwrites |
| **Token control** | Document all cron jobs; ability to disable via Hermes Desktop |
| **Simplicity** | MVP runnable by one operator without DevOps team |
| **Portability** | File-based storage OK for MVP; DB optional Phase 2 |

## 10. Acceptance Criteria (Requirements Level)

- [ ] All 9 core-use-case steps have a defined room, tool, and output file
- [ ] All 8 MCP tools specified with JSON contracts
- [ ] All 9 guardrails (G1–G9) enforced in agent rules
- [ ] Promotion lifecycle documented and STATUS file per room
- [ ] Sample data paths exist for one end-to-end demo signal
