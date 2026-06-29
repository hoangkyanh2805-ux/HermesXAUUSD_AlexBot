# Hermes XAUUSD IB Trading Desk — Video Flow Knowledge Asset

> **Source:** David — *I Let Hermes Agent Build My AI Trading Desk… The Results Were Insane* (Hermes desktop update demo)  
> **Transcript:** Vietnamese timestamp notes + English video description (user-provided)  
> **Project:** Hermes XAUUSD IB Trading Desk  
> **Distilled:** 2026-06-29 (v2 — full transcript)  
> **Confidence:** High for architecture and workflow; Medium for live-profit claims (video explicitly disclaims)

---

## 1. Core Idea of the Video

David demos the **new Hermes Agent desktop** by building an **AI trading floor** — not a Q&A chatbot, but a **self-improving research desk** that can:

- Backtest strategies
- Learn from past failures
- Optimize parameters over iterations
- Eventually suggest live trades

**Hermes vs Claude/ChatGPT (David's claim):** Hermes runs as an **autonomous agent inside your system**, retains **long-term context**, connects to **tools + messaging + scheduler**, and **improves strategies over time** — not one-shot chat.

**Desktop update value:** Non-terminal users can manage model, API gateway, Telegram, and cron schedules through a GUI — while still operating the desk primarily via Telegram chat.

**Honest scope of the video:** Architecture and workflow demo. David does **not** prove stable live profitability. The real value is **how to organize agents into an automated trading research desk**.

**Mechanism to preserve:**

```text
Autonomous Agent + Long Memory
    → Telegram command console
    → MCP tool layer (backtest / strategy ops)
    → Role-based rooms (not one mega-agent)
    → Scheduled agent loop (cron)
    → Dashboard + AI Brain (learn pairings)
    → Jarvis vision (everything in one place)
```

**What the video is NOT:** Proof of edge, financial advice, or a content/funnel system. StrategyFactory workbook links are setup aids — not the core mechanism.

---

## 2. Original Workflow (From Video)

### High-Level Flow

```text
Hermes Agent (+ Desktop)
    → Telegram (command console + topic-based trading firm)
    → Trader Dev MCP (Pine Script / TradingView backtest)
    → Strategy Rooms (Telegram topics = quant offices)
    → Backtest (+ fork / optimize / iterate)
    → Hermes Quant Lab Dashboard
    → AI Brain (indicator ↔ strategy pairing memory)
    → Jarvis trading vision
```

### Stage-by-Stage (Timestamp Map)

| Time | Stage | What David Actually Does |
|------|-------|--------------------------|
| 00:00–01:27 | **Core thesis** | AI trading floor; backtest + learn + optimize + suggest live; long-term memory |
| 01:49–03:16 | **Hermes Agent** | Autonomous agent on server/PC; tools + messaging + scheduler; desktop GUI for ops |
| 03:16–06:42 | **Install + Telegram** | One-line installer → quick setup → pick model → BotFather bot → token + user ID → chat via Telegram |
| 07:05–08:35 | **Trader Dev MCP** | Install MCP server; agent backtests via Pine Script / TradingView; create, edit, test, export strategies |
| 08:35–10:46 | **AI trading firm** | Telegram group with **topics as offices**: trend-following, optimizer, strategy-loader — **role split, not one agent** |
| 11:29–13:52 | **Prompt workbook + loop** | Copy prompts from workbook → create rooms → assign missions → **cron every 15 min** → self-improvement system → results to DB |
| 14:16–15:41 | **Dashboard + AI Brain** | **Hermes Quant Lab**: strategies, backtests, iterations, forward-test journal. Brain learns **which indicators pair with which strategy types** |
| 15:41–16:07 | **Fork / download** | Fork or download strategy source → tweak logic → optimize params → improve equity curve ("strategy factory") |
| 16:07–17:41 | **Desktop ops** | Debug via desktop: API server, gateway, bot status, swap model, edit/delete cron (token cost control) |
| 18:03–19:06 | **Jarvis vision** | One system for strategy, bots, backtest, forward test, trade management — **vision stated, not fully built** |

### Agent Loop (From Video)

```text
[cron every 15 min]
    → agent in room receives mission (workbook prompt)
    → create or fork strategy
    → backtest via Trader Dev MCP
    → save results to database
    → AI Brain updates pairings / lessons
    → dashboard reflects iteration
    → self-improvement system queues next task
```

---

## 3. Adapted Workflow — Hermes XAUUSD IB

```text
Hermes XAUUSD Agent (+ Desktop)
    → Telegram DM / Signal Group (topics = IB offices)
    → XAUUSD Trading MCP
    → Strategy Rooms (gold setups by role)
    → Signal Replay / Forward Test
    → IB Signal Dashboard
    → XAUUSD AI Brain
    → Alex IB Jarvis Vision
```

### Mapping Table

| Video (David) | Hermes XAUUSD IB | Adaptation Notes |
|---------------|------------------|------------------|
| Hermes Agent + Desktop | **Hermes XAUUSD Agent + Desktop** | Same stack; desk SOP scoped to XAUUSD / gold IB |
| Telegram command console | **Telegram DM + Signal Group** | DM = client support; Group = signal broadcast + optional **topics as offices** |
| Trader Dev MCP (Pine / TV) | **XAUUSD Trading MCP** | Replace generic TV backtest with **signal replay + forward test**; optional TV/Pine for your own gold strategy research |
| Telegram topics = quant offices | **Strategy Rooms / Group topics** | e.g. `london-breakout`, `session-filter`, `signal-optimizer` — **role split preserved** |
| Backtest loop | **Signal Replay / Forward Test** | IB publishes signals, not algos — validate track record before group post |
| Hermes Quant Lab | **IB Signal Dashboard** | Strategies → **signal setups**; backtests → **replay results**; journal → **forward-test log** |
| AI Brain (indicator pairing) | **XAUUSD AI Brain** | Learn **setup ↔ session ↔ volatility ↔ news** pairings for gold (not random indicators) |
| Fork / download strategy | **Fork signal setup** | Clone a working gold setup → tweak entry rules → replay → promote |
| 15-min cron research | **Scheduled replay / review** | Cron reviews open signals, session windows, forward-test status — control token spend via desktop |
| Jarvis vision | **Alex IB Jarvis Vision** | One place: signals, clients, replay, forward test, desk ops — build last |
| StrategyFactory workbook | **Alex IB Prompt Workbook** | Your own prompts for room creation, missions, cron — **no funnel / no content engine** |

### IB Office Structure (Adapted from Video's Trading Firm)

| Topic / Room | Role | XAUUSD IB Mission |
|--------------|------|-------------------|
| `setup-research` | Strategy loader | Import or define gold setups; fork winners |
| `signal-optimizer` | Optimizer office | Tune SL/TP, session filters, RR on replay data |
| `session-desk` | Trend / session office | London / NY gold session signal logic |
| `forward-test` | QA office | Paper signals before Signal Group promotion |
| `operator-dm` | (DM, not topic) | Client questions — human or light agent assist |

---

## 4. Key Concepts to Reuse

### A. Systems Over Hype
Edge = right tools + proper testing + structured loops — not "ask AI to trade."

### B. Long-Term Memory Agent
Hermes remembers prior runs, failed setups, and improvements. Your brain layer must **persist** — not rely on chat context alone.

### C. Telegram as Command Console
Primary operator interface is chat (missions, status, triggers). Desktop is for **debug and ops**, not daily trading commands.

### D. MCP = Capability Boundary
Trader Dev gives backtest. Your XAUUSD MCP gives replay, promote, post. Agent never bypasses tools.

### E. Role-Based Rooms (Critical)
**Do not use one agent for everything.** Split by office: research, optimize, session desk, forward test — mirrors David's Telegram topics.

### F. Prompt Workbook + Cron Loop
Reusable prompts create rooms, assign missions, schedule work. **15-min cron** drives continuous research — with desktop control to delete runaway jobs.

### G. AI Brain = Pairing Memory
Video: MACD fits strategy A, volume fits strategy B. **IB adaptation:** London breakout fits low-spread mornings; news-fade fits high-impact USD weeks — document pairings, not random combos.

### H. Fork → Improve → Promote
Strategy factory pattern: start from proven setup, iterate, gate before live.

### I. Dashboard = Single Source of Truth
Quant Lab stores strategies, backtests, iterations, forward journal. Your dashboard = signal track record + room status + promotion state.

### J. Jarvis Is the Capstone
Vision integrates everything; video only sketches it. Build pipe first.

---

## 5. What to Copy from the Video

| Copy | How for Hermes XAUUSD IB |
|------|--------------------------|
| Hermes install + Telegram bot setup | One-line install; BotFather; token; user ID; Telegram as console |
| Hermes Desktop for ops | Manage model, gateway, bot, cron — token cost control |
| MCP server attachment | XAUUSD Trading MCP alongside Hermes |
| Telegram group with **topics as offices** | Signal group or private ops group with topic per room role |
| Prompt workbook pattern | `workbook/` folder: room-create, mission, cron-setup prompts |
| 15-min cron agent loop | Scheduled replay review / forward-test check (start with 1 room) |
| Self-improvement queue | After each replay, append brain + queue next optimization task |
| Results to database / JSONL | Structured storage for dashboard + brain |
| Hermes Quant Lab → your dashboard | Panels: setups, replay stats, forward journal, iteration log |
| AI Brain pairing logic | `knowledge/brain/pairings.md` — setup ↔ session ↔ condition |
| Fork / improve workflow | `strategy-rooms/<id>/` with `forked_from` metadata |
| Role separation | One mission per room per cron tick — no monolithic agent |
| Desktop debug workflow | Chat on Telegram; debug schedules and MCP on desktop |
| Disclaimer discipline | Education / forward test / risk gates — never skip for IB reputation |

---

## 6. What NOT to Copy

| Exclude | Reason |
|---------|--------|
| **Content Engine** | Video sells via YouTube; your desk is signal ops, not content production |
| **X Funnel Pack** | Comment "AI AGENT" lead capture — not IB workflow |
| **BioLink funnel** | StrategyFactory resource pages — defer entirely |
| **CRM expansion** | No client pipeline automation in MVP |
| **StrategyFactory as product** | Extract workbook **pattern** only; not their platform dependency |
| **Blind live trade suggestions** | Video suggests path to live; you require replay + forward-test gates |
| **Proof of profit implied by title** | "Results Were Insane" is marketing; video admits no full live proof |
| **One agent does all** | Explicitly against video's own architecture |
| **Uncontrolled cron** | David warns: delete bad crons to save tokens — enforce in your ops |
| **Random indicator soup** | Brain should learn **meaningful** gold pairings, not indicator spam |
| **Multi-asset quant lab** | Stay XAUUSD-focused for IB clarity |

---

## 7. MVP Scope

### Phase 1 — MVP (Match Video Architecture, IB Scope)

```text
Hermes XAUUSD Agent + Desktop
    → Telegram Signal Group (1 topic = 1 room)
    → XAUUSD Trading MCP (5 tools)
    → 1 Strategy Room: london-gold
    → Signal Replay on 30 historical signals
    → IB Signal Dashboard (read-only)
    → XAUUSD AI Brain (outcomes.jsonl + pairings.md)
```

**MVP tools (XAUUSD Trading MCP):**
- `get_xauusd_quote`
- `list_strategy_rooms`
- `replay_signals` — `{ win_rate, avg_r, max_dd, pass }`
- `promote_room` — `draft → replay_passed → forward_test → live`
- `post_signal_to_telegram` — standard IB signal format

**MVP workbook prompts (3):**
1. `create-room.md` — spawn strategy room + config
2. `mission-replay.md` — run replay, save results
3. `mission-forward.md` — start forward-test journal entry

**MVP cron:** 1 job (e.g. every 30 min) — replay check or forward-test status only for `london-gold`. Use desktop to monitor token use.

**MVP Dashboard panels:**
- Room status + promotion state
- Last 30 signals (W/L, avg R)
- Forward-test journal (last 7 days)
- Replay iteration log

### Phase 2 — After MVP

- Second room (`signal-optimizer` role)
- Telegram DM assist (FAQ only, not sales bot)
- Fork setup workflow
- Alex IB Jarvis Vision (read-only queries over brain + dashboard)

### Out of Scope

- Alex IB Jarvis Vision (Phase 1)
- Full TradingView / Pine automation (optional research lane later)
- Live broker execution API
- CRM, funnels, content, BioLink, X pack
- Multi-instrument desk

### MVP Done When

1. Hermes chats via Telegram; desktop shows healthy bot + 1 cron.
2. Workbook prompt creates `london-gold` room.
3. MCP `replay_signals` runs and returns pass/fail.
4. Promotion gate blocks Telegram group post until `live`.
5. Dashboard displays replay + last signals.
6. Brain appends outcome + one pairing note (e.g. "London breakout + low spread → pass").

---

## 8. Terms / Glossary

| Term | Definition |
|------|------------|
| **Hermes Agent** | Autonomous AI agent (server/PC) with tools, messaging, scheduler, long memory |
| **Hermes Desktop** | GUI to manage model, gateway, Telegram, cron — ops/debug layer |
| **Hermes XAUUSD Agent** | Your Hermes instance scoped to gold IB desk SOP |
| **Telegram command console** | Chat interface to send missions and receive agent output |
| **BotFather** | Telegram bot creation; provides API token |
| **Trader Dev MCP** | David's MCP for Pine Script / TradingView backtest (video reference) |
| **XAUUSD Trading MCP** | Your MCP: replay, promote, post, quote — gold IB tools |
| **Strategy Room / Quant Office** | Isolated unit of work; Telegram topic or folder; one role |
| **Prompt Workbook** | Reusable prompts for room setup, missions, cron — not chat improvisation |
| **Agent Loop** | Cron → mission → tool call → save → brain update → next task |
| **Self-Improvement System** | Queue of follow-up tasks after each iteration |
| **Signal Replay** | Historical signal validation (IB equivalent of backtest) |
| **Forward Test** | Live-sim signals before Signal Group promotion |
| **Hermes Quant Lab** | David's dashboard name — strategies, backtests, iterations, journal |
| **IB Signal Dashboard** | Your equivalent: signal track record + room health |
| **AI Brain** | Memory of what works with what — indicator pairings (video) → setup/session pairings (IB) |
| **Strategy Factory** | Fork → tweak → replay → improve equity / win rate |
| **Promotion Gate** | Metrics + forward-test days before `live` status |
| **Alex IB Jarvis Vision** | End-state: one conversational command center over full desk |
| **Gateway** | Hermes data/API gateway managed in desktop app |

---

## 9. Implementation Notes for Cursor

### Recommended Repo Layout

```text
hermes-xauusd-ib-desk/
├── .cursor/rules/hermes-xauusd-desk.mdc
├── agents/hermes-xauusd-agent.md
├── workbook/                          # ← from video's prompt workbook
│   ├── create-room.md
│   ├── mission-replay.md
│   └── mission-forward.md
├── mcp/xauusd-trading/
├── strategy-rooms/
│   ├── london-gold/                   # session-desk office
│   └── _template/
├── dashboard/ib-signals/              # Hermes Quant Lab equivalent
├── knowledge/
│   ├── brain/
│   │   ├── pairings.md                # setup ↔ session ↔ condition
│   │   ├── setups.md
│   │   └── outcomes.jsonl
│   ├── raw/video-notes/
│   │   └── david-hermes-trading-desk.md
│   └── distilled/                     # this file
├── telegram/
│   ├── offices.md                     # topic ↔ role map
│   └── signal-format.md
└── docs/flow.md
```

### Hermes Setup Checklist (From Video)

1. Run Hermes one-line installer (terminal).
2. Quick setup → choose AI provider + model.
3. Create Telegram bot (BotFather) → token + your user ID.
4. Verify chat works in Telegram.
5. Install XAUUSD Trading MCP (your equivalent of Trader Dev).
6. Create Telegram group → enable **topics** → one topic per office.
7. Paste workbook prompts to create first room.
8. Add cron (start 30 min; tune after token review).
9. Open Hermes Desktop → verify gateway, bot, schedule.
10. Open IB Signal Dashboard → confirm replay data flows.

### Cursor Agent SOP (Essentials)

1. **One room, one role, one mission** per cron tick.
2. **Never post to Signal Group** unless `room.status == live`.
3. **Always persist** replay results + outcomes to brain.
4. **Use workbook prompts** — do not improvise room structure each time.
5. **MCP only** for trading actions.
6. **Control cron** — document each job; delete if token burn is unjustified.
7. **No CRM, content, funnel, BioLink, X pack** in this repo.

### AI Brain — Pairing Schema (IB Adaptation)

Video learns: `MACD + trend strategy = good`.

You learn:

```markdown
## Pairing: london-breakout
- session: London open (07:00–11:00 UTC)
- condition: spread < 30 pts, no high-impact USD in ±30 min
- result: 62% win, 1.8 avg R (replay n=45)
- avoid: NY close chop
```

### Cron Template (Adapted from 15-min loop)

```yaml
# hermes schedule — review only, 1 room MVP
name: london-gold-replay-review
interval: 30m
mission: workbook/mission-replay.md
room: london-gold
on_pass: queue workbook/mission-forward.md
on_fail: append brain/pairings.md with failure note
```

### Phase Order for Cursor Sessions

1. `workbook/` prompts (3 files)  
2. `strategy-rooms/london-gold/` + STATUS lifecycle  
3. XAUUSD Trading MCP — `replay_signals` first  
4. Telegram signal format + `post_signal_to_telegram`  
5. IB Signal Dashboard reader  
6. Brain `outcomes.jsonl` + `pairings.md` writers  
7. Telegram group topics map (`telegram/offices.md`)  
8. Second room + optimizer role  
9. Alex IB Jarvis Vision sketch  

---

## 10. Final Knowledge Asset Summary

**Asset name:** Hermes XAUUSD IB Desk Flow (David Video Distillation v2)  
**Type:** Framework + Project Map + MVP Checklist + Setup Playbook  
**Reuse trigger:** Hermes install, room design, MCP wiring, cron loops, IB adaptation of quant desk pattern  

**One-line formula:**

> Autonomous Hermes with long memory → Telegram offices by role → MCP tools → scheduled replay/forward loop → dashboard as proof → brain learns pairings → Jarvis last.

**Source facts vs inference:**

| Claim | Status |
|-------|--------|
| Hermes has desktop, Telegram, MCP, cron | **Source fact** |
| Topics = quant offices, 15-min cron, workbook prompts | **Source fact** |
| AI Brain learns indicator-strategy pairings | **Source fact** |
| Video proves stable live profit | **False — video disclaims** |
| XAUUSD MCP tool names and gate thresholds | **Project inference** |

**Acceptance criteria:**
- [ ] Hermes + Telegram + Desktop operational
- [ ] ≥1 Telegram topic mapped to 1 strategy room
- [ ] Workbook prompts create room + run replay mission
- [ ] 1 cron job with desktop visibility
- [ ] IB Signal Dashboard shows replay + signals
- [ ] Brain has outcomes + ≥1 pairing entry
- [ ] No content engine / funnel / CRM in repo scope

---

## Source Inventory

| Source | Type | Confidence |
|--------|------|------------|
| Vietnamese timestamp transcript (00:00–19:06) | Primary | High |
| English video description + chapters | Primary | High |
| User project context (XAUUSD IB, adapted flow) | Primary | High |
| XAUUSD MCP schemas, gate thresholds | Inference | Medium |

## Skill Candidates (Future)

| Skill | Purpose |
|-------|---------|
| `hermes-desk-operator` | SOP for 8-stage flow + cron discipline |
| `ib-telegram-offices` | Map Telegram topics to strategy room roles |
| `xauusd-signal-replay` | Replay gate thresholds + promotion rules |
| `ib-prompt-workbook` | Room/mission/cron prompt templates |
