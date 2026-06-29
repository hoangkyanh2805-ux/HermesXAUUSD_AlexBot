# Hermes XAUUSD IB Trading Desk — Knowledge Asset

> **Source:** [I Let Hermes Agent Build My AI Trading Desk… The Results Were Insane](https://www.youtube.com/watch?v=MbfuJZZ01IU)  
> **Type:** Video description + chapter notes + trading desk case study  
> **Project:** Hermes XAUUSD IB Trading Desk  
> **Distilled:** 2026-06-29 (v3 — IB rooms + signal use case)  
> **Skill:** `knowledge-asset-factory`

---

## 1. Source Summary

### What the video demonstrates

David (StrategyFactory) demos the **new Hermes Agent desktop** by building an **AI trading research desk** — not a Q&A chatbot. He installs Hermes, connects it to **Telegram** as a command console, attaches **Trader Dev MCP** for TradingView / Pine Script backtesting, organizes work into **agent rooms** (like a small quant firm), runs **scheduled research loops**, tracks everything on a **dashboard**, and compounds lessons in an **AI Brain**. The stated end goal is a **Jarvis-like trading operating system**.

### Mechanisms worth extracting

| Mechanism | What it does |
|-----------|--------------|
| Autonomous agent + long memory | Hermes persists context and improves over iterations — unlike one-shot chat |
| Telegram as ops layer | Primary interface for missions, status, and triggers |
| MCP tool boundary | Real work (backtest, strategy ops) goes through structured tools |
| Role-based rooms | Split agents by function — not one mega-agent |
| Cron / scheduled loops | Continuous research without manual prompting every time |
| Quality gate | Backtest + forward test before trusting output |
| Dashboard | Single pane for strategies, results, iterations, decisions |
| AI Brain | Learns pairings (e.g. which indicators fit which strategy types) |
| Desktop app | Debug gateway, model, bot, schedules; control token spend |
| Jarvis vision | Capstone — integrate strategy, bots, test, management in one place |

### What the video does NOT prove

- Stable live profitability
- Fully built Jarvis system (vision stated, not completed)
- Financial advice (video frames as education)

### Source inventory

| Input | Confidence |
|-------|------------|
| Video URL + description + chapters | High |
| Vietnamese timestamp notes (prior session) | High |
| XAUUSD IB project context (user) | High |
| Room names + signal use case (user) | High — project spec |
| MCP tool schemas, gate thresholds | Medium — project inference |

---

## 2. Original Video Flow

```text
Hermes Agent
    → Telegram
    → Trader Dev MCP
    → Strategy Rooms
    → Backtest
    → Dashboard
    → AI Brain
    → Jarvis trading vision
```

### Layer definitions (video)

| Layer | Role |
|-------|------|
| **Hermes Agent** | Central autonomous operator; memory, tools, scheduler |
| **Telegram** | Command + communication console |
| **Trader Dev MCP** | TradingView / Pine Script backtest and strategy tooling |
| **Strategy Rooms** | Specialized agent rooms (quant desk offices) |
| **Backtest** | Quality-control via historical validation |
| **Dashboard** | Tracking: backtests, ideas, agent decisions |
| **AI Brain** | Learning layer from prior results |
| **Jarvis vision** | Long-term OS vision for unified trading command center |

### Agent loop (from video)

```text
[cron schedule]
  → room receives mission (workbook prompt)
  → create / fork strategy
  → backtest via Trader Dev MCP
  → save results
  → AI Brain updates
  → dashboard reflects state
  → queue next improvement task
```

---

## 3. Adapted Hermes XAUUSD IB Flow

```text
Hermes XAUUSD Agent
    → Telegram DM / Signal Group
    → XAUUSD Trading MCP
    → Strategy Rooms
        ├── Market Room
        ├── Signal Room
        ├── Lot Room
        ├── Seeding Room
        └── Journal Room
    → Signal Replay / Forward Test
    → IB Signal Dashboard
    → XAUUSD AI Brain
    → Alex IB Jarvis Vision
```

### Core use case — new XAUUSD signal

When a new XAUUSD signal appears, Hermes should:

```text
1. Read market context          (Market Room)
2. Check the signal             (Signal Room)
3. Approve / wait / reject      (Signal Room + quality gate)
4. Calculate safe lot by group  (Lot Room)
5. Generate Telegram seeding    (Seeding Room)
6. Track live signal status     (Signal Room + Dashboard)
7. Journal the result           (Journal Room)
8. Update dashboard             (IB Signal Dashboard)
9. Feed result into AI Brain    (XAUUSD AI Brain)
```

### Room responsibilities

| Room | Mission | Output |
|------|---------|--------|
| **Market Room** | Read XAUUSD context: session, spread, volatility, news window | `market_context.json` |
| **Signal Room** | Validate signal structure, RR, session fit; approve/wait/reject | `signal_decision.json` |
| **Lot Room** | Safe lot by client group (risk %, max exposure) | `lot_plan.json` |
| **Seeding Room** | Natural Telegram copy around the signal (not spam) | `seeding_messages.md` |
| **Journal Room** | Log entry, management, exit, lesson | `journal_entry.jsonl` |
| **Replay / Forward Test** | Quality gate before promotion to live group | `replay_result.json` |

### Telegram channels

| Channel | Purpose |
|---------|---------|
| **DM** | Client support, private follow-up |
| **Signal Group** | Broadcast approved signals + seeding content |

---

## 4. Key Concepts from the Video

### Keep the 8-layer architecture

The video's power is **layer separation**, not any single tool. Each layer has one job.

### Hermes ≠ chatbot

Hermes is an **operator** with memory, schedule, and tools — not a strategy oracle.

### MCP = real work boundary

Agents call tools; they do not freestyle broker actions or invent backtest results.

### Rooms = role specialization

David splits by office (trend, optimizer, loader). You split by **IB workflow stage** (market → signal → lot → seeding → journal).

### Test before broadcast

Video: backtest + forward test. You: **signal replay + forward test** before Signal Group promotion.

### Dashboard = trust + ops

Clients and operator need visible track record. Dashboard is proof, not decoration.

### AI Brain = compounding edge

Learn what works with what — video uses indicator pairings; you use **setup ↔ session ↔ volatility ↔ client group** pairings.

### Jarvis last

Vision layer integrates everything. Build the pipe first; Jarvis reads from brain + dashboard later.

### Risk discipline (from video)

Testing, forward testing, risk control — never skip for IB reputation. No guaranteed profit claims.

---

## 5. Direct Mapping Table

| # | Video (Original) | Hermes XAUUSD IB | Change type |
|---|------------------|------------------|-------------|
| 1 | Hermes Agent | **Hermes XAUUSD Agent** | Rename + scope to gold IB SOP |
| 2 | Telegram | **Telegram DM + Signal Group** | Split client DM vs signal broadcast |
| 3 | Trader Dev MCP | **XAUUSD Trading MCP** | Replace TV/Pine backtest with IB signal tools |
| 4 | Strategy Rooms (quant offices) | **5 IB rooms** (Market, Signal, Lot, Seeding, Journal) | Adapt roles to IB signal workflow |
| 5 | Backtest | **Signal Replay / Forward Test** | IB publishes signals, not algos |
| 6 | Dashboard (Hermes Quant Lab) | **IB Signal Dashboard** | Signal track record + room status |
| 7 | AI Brain | **XAUUSD AI Brain** | Gold/session/client-group pairings |
| 8 | Jarvis trading vision | **Alex IB Jarvis Vision** | Personal IB command center OS |

### Video room pattern → IB room pattern

| Video pattern | IB equivalent |
|---------------|---------------|
| Trend-following office | **Market Room** + **Signal Room** |
| Optimizer office | **Signal Replay** tuning + **Lot Room** risk params |
| Strategy-loader office | Import / fork gold setups into **Signal Room** |
| Forward-test journal | **Journal Room** + forward test gate |
| Telegram topic per office | Telegram topic per room OR folder per room in repo |

---

## 6. What to Copy

| Copy from video | Apply to Hermes XAUUSD IB |
|-----------------|---------------------------|
| Hermes as central operator | One agent orchestrates rooms via MCP |
| Telegram command console | DM + Signal Group; missions via chat |
| MCP tool attachment | XAUUSD Trading MCP with explicit tools per room |
| Role-based rooms | 5 rooms — never one agent doing all steps blindly |
| Prompt workbook pattern | `workbook/` with room missions (create, replay, seed, journal) |
| Cron / scheduled loops | Review open signals, forward-test status (control via desktop) |
| Backtest → forward test gate | Replay → forward test → `live` promotion |
| Dashboard tracking | IB Signal Dashboard reads structured outputs |
| AI Brain learning loop | Append outcomes + pairings after every signal |
| Hermes Desktop for ops | Model, gateway, bot, cron management |
| Fork / improve workflow | Fork winning gold setup → tweak → replay |
| Disclaimer discipline | Education framing; no profit guarantees |
| Token / cron control | Delete runaway schedules from desktop |

---

## 7. What NOT to Copy

| Exclude | Reason |
|---------|--------|
| **Content Engine** | Not a content production system |
| **X Funnel Pack** | YouTube lead capture ≠ IB desk |
| **BioLink funnel** | Out of scope |
| **Full CRM** | Telegram + light client groups only |
| **Real trade execution** | Deferred — signal ops first, no broker API yet |
| **Client password handling** | Security boundary — never in agent scope |
| **Guaranteed profit claims** | IB reputation + compliance risk |
| **Overtrading optimization** | Optimize for quality and risk control, not signal volume |
| **StrategyFactory platform lock-in** | Extract workbook pattern only |
| **One agent does everything** | Against video's own architecture |
| **Blind live promotion** | Always pass replay + forward test gates |
| **"Insane results" marketing** | Video is architecture demo, not profit proof |
| **Random indicator soup** | Brain learns meaningful gold pairings only |

---

## 8. MVP Scope

### Principle

Smallest version that runs the **full signal pipeline once** end-to-end — with mock or manual data where integrations are not ready.

### In scope (MVP)

```text
Hermes XAUUSD Agent + Desktop
  → Telegram Signal Group (1 test group)
  → XAUUSD Trading MCP (core tools)
  → 5 Strategy Rooms (folder + STATUS each)
  → Signal Replay on 1 historical signal set
  → IB Signal Dashboard (read-only)
  → XAUUSD AI Brain (outcomes.jsonl + pairings.md)
```

**XAUUSD Trading MCP — MVP tools:**

| Tool | Room | Purpose |
|------|------|---------|
| `get_market_context` | Market | Session, spread, volatility stub |
| `validate_signal` | Signal | Approve / wait / reject |
| `calculate_lot_plan` | Lot | Safe lot by client group rules |
| `generate_seeding_copy` | Seeding | Natural Telegram messages |
| `replay_signals` | QC | Replay gate: win_rate, avg_r, pass |
| `post_signal_to_telegram` | Signal | Post approved signal to group |
| `append_journal` | Journal | Write journal entry |
| `update_brain` | Brain | Append outcome + pairing note |

**Promotion lifecycle:**

```text
draft → replay_passed → forward_test → live
```

**MVP workbook prompts (5):**

1. `mission-market-context.md`
2. `mission-validate-signal.md`
3. `mission-lot-and-seed.md`
4. `mission-publish-and-track.md`
5. `mission-journal-and-learn.md`

**MVP cron:** 1 job (30 min) — forward-test status check for active signals only.

### Out of scope (defer)

- Alex IB Jarvis Vision
- Real broker execution API
- Client password / credential handling
- Full TradingView / Pine automation
- Telegram DM auto-bot (human or manual DM first)
- CRM, funnels, content engine
- Multi-instrument desk
- Overtrading / high-frequency signal generation

### MVP done when

1. A sample XAUUSD signal runs through all 9 core-use-case steps.
2. `validate_signal` can return approve / wait / reject.
3. `replay_signals` blocks promotion when metrics fail.
4. Approved signal posts to Telegram in standard format.
5. Dashboard shows last signal + decision + journal entry.
6. Brain has ≥1 outcome row and ≥1 pairing note.
7. No execution API, no password handling, no profit claims in copy.

### Phase 2 (post-MVP)

- Forward test automation (7-day paper track)
- Second signal setup (fork workflow)
- DM assist for FAQ only
- Alex IB Jarvis Vision (read-only queries)
- Optional TradingView research lane (manual)

---

## 9. Suggested Folder Structure

```text
hermes-xauusd-ib-desk/
├── .cursor/
│   └── rules/
│       └── hermes-xauusd-desk.mdc       # Agent SOP + guardrails
├── agents/
│   └── hermes-xauusd-agent.md           # System prompt + room routing
├── workbook/
│   ├── mission-market-context.md
│   ├── mission-validate-signal.md
│   ├── mission-lot-and-seed.md
│   ├── mission-publish-and-track.md
│   └── mission-journal-and-learn.md
├── mcp/
│   └── xauusd-trading/
│       ├── src/
│       └── tools/
├── strategy-rooms/
│   ├── market-room/
│   │   ├── config.yaml
│   │   └── STATUS
│   ├── signal-room/
│   │   ├── config.yaml
│   │   ├── signals/
│   │   └── STATUS
│   ├── lot-room/
│   │   ├── client-groups.yaml
│   │   └── STATUS
│   ├── seeding-room/
│   │   ├── templates/
│   │   └── STATUS
│   ├── journal-room/
│   │   ├── entries.jsonl
│   │   └── STATUS
│   └── _template/
├── dashboard/
│   └── ib-signals/                      # IB Signal Dashboard
├── knowledge/
│   ├── raw/video-notes/
│   │   └── hermes-agent-trading-desk-youtube.md
│   ├── brain/
│   │   ├── pairings.md
│   │   ├── setups.md
│   │   └── outcomes.jsonl
│   └── distilled/
│       └── hermes-xauusd-ib-desk-knowledge-asset.md   # this file
├── telegram/
│   ├── signal-format.md
│   ├── seeding-guidelines.md
│   └── offices.md                       # topic ↔ room map
└── docs/
    ├── flow.md
    ├── guardrails.md                    # no execution, no passwords, no profit claims
    └── client-groups.example.yaml
```

---

## 10. Implementation Notes for Cursor

### Agent routing rule

One signal event flows **sequentially** through rooms. Do not parallelize approve + publish without lot plan.

```text
market_context → validate_signal → [gate] → lot_plan → seeding_copy → publish → track → journal → brain
```

### Cursor agent SOP (hard rules)

1. **Never** post to Signal Group unless `signal_decision == approve` AND `room.status == live`.
2. **Never** handle client passwords, broker credentials, or execution API in MVP.
3. **Never** generate guaranteed profit language in seeding copy.
4. **Always** run `replay_signals` before first promotion of a new setup.
5. **Always** append journal + brain after signal closes.
6. **Prefer MCP tools** over shell for all desk actions.
7. **One mission per room** per cron tick.
8. **Seeding** = natural context around signal, not hype spam.
9. **Lot Room** uses client group rules — cap risk per group, not one size fits all.
10. **No CRM, content engine, funnel, BioLink, X pack** in this repo.

### Structured outputs (data contract)

**`market_context.json`**
```json
{
  "symbol": "XAUUSD",
  "session": "london",
  "spread_pts": 28,
  "volatility": "normal",
  "news_risk": "low",
  "ts": "2026-06-29T08:00:00Z"
}
```

**`signal_decision.json`**
```json
{
  "signal_id": "sig-001",
  "decision": "approve",
  "reason": "RR 1:2.5, london session, replay pass",
  "entry": 2345.5,
  "sl": 2340.0,
  "tp": 2355.0
}
```

**`lot_plan.json`**
```json
{
  "signal_id": "sig-001",
  "groups": [
    { "name": "conservative", "risk_pct": 0.5, "lot": 0.01 },
    { "name": "standard", "risk_pct": 1.0, "lot": 0.02 }
  ]
}
```

**`outcomes.jsonl` (brain)**
```json
{"ts":"2026-06-29T14:00:00Z","signal_id":"sig-001","result":"win","r":2.1,"session":"london","setup":"breakout","lesson":"low spread morning worked"}
```

### Build order for Cursor sessions

| Order | Task |
|-------|------|
| 1 | `docs/guardrails.md` + `.cursor/rules/hermes-xauusd-desk.mdc` |
| 2 | `strategy-rooms/` scaffold (5 rooms + STATUS lifecycle) |
| 3 | `telegram/signal-format.md` + `seeding-guidelines.md` |
| 4 | XAUUSD Trading MCP — `get_market_context`, `validate_signal` first |
| 5 | `replay_signals` + promotion gate |
| 6 | `calculate_lot_plan`, `generate_seeding_copy` |
| 7 | `post_signal_to_telegram`, `append_journal`, `update_brain` |
| 8 | Workbook missions (5 prompts) |
| 9 | IB Signal Dashboard reader |
| 10 | 1 cron job + desktop verification checklist |

### Skill candidates (future)

| Skill | Purpose |
|-------|---------|
| `hermes-xauusd-desk-operator` | Full SOP + room routing |
| `ib-signal-quality-gate` | Replay / forward test thresholds |
| `ib-telegram-seeding` | Natural seeding copy guidelines |
| `xauusd-lot-by-group` | Client group risk rules |

---

## 11. Next Prompt to Run with `$project-kickstart-os`

Copy and run this prompt in a new Cursor chat to turn this knowledge asset into a build-ready project OS:

```markdown
$project-kickstart-os

PROJECT NAME:
Hermes XAUUSD IB Trading Desk

KNOWLEDGE ASSET (already distilled):
Read and use as primary source:
knowledge/distilled/hermes-xauusd-ib-desk-knowledge-asset.md

Also reference:
knowledge/raw/video-notes/hermes-agent-trading-desk-youtube.md

PROJECT TYPE:
AI agent operating system for a Forex IB (XAUUSD / Gold) — NOT a content engine, NOT a CRM, NOT trade execution.

OBJECTIVE:
Build an agent-operated IB signal desk where Hermes XAUUSD Agent orchestrates 5 strategy rooms (Market, Signal, Lot, Seeding, Journal) via XAUUSD Trading MCP, validates signals through replay/forward test, publishes to Telegram Signal Group, tracks on IB Signal Dashboard, and learns via XAUUSD AI Brain.

AUDIENCE:
- Me (IB operator / Alex)
- Global clients via Telegram DM and Signal Group

SUCCESS METRICS (MVP):
- One sample XAUUSD signal flows through all 9 core-use-case steps end-to-end
- Replay gate blocks bad setups before Telegram publish
- Dashboard shows signal decision + journal + stats
- Brain accumulates ≥1 outcome + pairing per closed signal
- Zero broker execution, zero password handling, zero profit guarantees in copy

NON-GOALS (HARD):
- Content Engine, X Funnel Pack, BioLink funnel
- Full CRM
- Real trade execution API
- Client password / credential handling
- Guaranteed profit claims
- Overtrading / signal spam optimization

ADAPTED FLOW:
Hermes XAUUSD Agent → Telegram DM/Signal Group → XAUUSD Trading MCP → Strategy Rooms (Market, Signal, Lot, Seeding, Journal) → Signal Replay/Forward Test → IB Signal Dashboard → XAUUSD AI Brain → Alex IB Jarvis Vision (defer)

CORE USE CASE:
New signal → market context → validate → approve/wait/reject → lot by client group → seeding copy → publish → track → journal → dashboard → brain

DELIVERABLES REQUESTED:
1. docs/project-brief.md
2. docs/requirements.md
3. docs/architecture.md
4. docs/mvp-build-map.md
5. docs/first-sprint.md
6. docs/sop-ops-runbook.md
7. Recommended .cursor/rules and agents/ prompts
8. Acceptance criteria per MVP phase

CONSTRAINTS:
- Keep video's 8-layer architecture; adapt names only where needed
- Jarvis vision is Phase 2+ — do not scope into MVP
- Prefer smallest buildable first version
- Every risky action needs human approval gate (especially Telegram publish)

Please read the knowledge asset first, then produce all deliverables. Do not start coding services until brief and MVP map are written.
```

---

## Acceptance Criteria (This Asset)

- [x] Source summary with confidence levels
- [x] Original + adapted flows documented
- [x] 5 IB strategy rooms mapped to video pattern
- [x] 9-step core use case defined
- [x] Copy / no-copy lists include all user exclusions
- [x] MVP scope with defer list
- [x] Folder structure + Cursor implementation notes
- [x] `$project-kickstart-os` prompt ready to copy

---

## One-Line Formula

> Hermes operates → Telegram commands → MCP does real work → 5 IB rooms process each signal → replay/forward test gates quality → dashboard proves track record → brain compounds lessons → Jarvis integrates last.
