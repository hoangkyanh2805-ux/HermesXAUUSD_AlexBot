# Risk-First Volume Desk Upgrade — Knowledge Asset

> **Source type:** Business / system upgrade brief  
> **Source title:** Risk-First Volume Desk Upgrade for Hermes XAUUSD IB System  
> **Project:** Hermes XAUUSD IB Trading Desk  
> **Distilled:** 2026-06-29 (v1)  
> **Skill:** `knowledge-asset-factory`  
> **Parent asset:** [hermes-xauusd-ib-desk-knowledge-asset.md](./hermes-xauusd-ib-desk-knowledge-asset.md)  
> **Tiếng Việt:** [hermes-xauusd-risk-first-volume-desk-upgrade.vi.md](./hermes-xauusd-risk-first-volume-desk-upgrade.vi.md)

---

## 1. Source Summary

### What the upgrade brief proposes

Evolve the existing Hermes XAUUSD IB Desk from a **basic signal workflow** into a **Risk-First Volume Desk** — a professional IB operating system that protects client equity first, tracks business volume second, and never treats commission volume as a trading objective.

### Source context

| Item | Detail |
|------|--------|
| **Operator role** | Forex IB focused on XAUUSD / Gold |
| **Channels** | Telegram DM + Signal Group |
| **Reference architecture** | Hermes Agent trading desk video flow, adapted to IB signal ops |
| **Business KPI** | ~200 lots/month — **monitor only**, never a trade trigger |
| **Core metaphor** | Equity = fuel tank; risk = fuel gauge; DXY/US10Y = weather; multi-entry = trip stages; volume = distance traveled |

### Source inventory

| Input | Type | Confidence |
|-------|------|------------|
| User upgrade brief (this document) | Primary spec | High |
| Existing repo MVP (Phase C) | Verified codebase | High |
| Hermes video flow mapping | Prior knowledge asset | High |
| DXY/US10Y correlation thresholds | Brief examples only | Medium — needs calibration |
| Spread threshold (30 pts) | Brief example | Medium — repo currently uses 35 pts |
| 200 lots/month KPI | Business target | High — operator stated |

### What the brief does NOT ask for

- Real broker execution API
- Client password handling
- Full CRM, Content Engine, X Funnel, BioLink
- Profit guarantees or commission-first overtrading
- Replacing the Hermes 8-layer desk architecture

---

## 2. Core Idea

**Upgrade the desk from “signal publisher” to “risk-first IB operator.”**

The system should help Alex:

1. Validate XAUUSD signals with market + correlation context
2. Size positions from equity and risk — not from volume targets
3. Block or pause trades when floating risk, spread, news, or daily loss limits are breached
4. Support multi-entry **only** when total risk is unchanged
5. Audit spread at seed, entry, and close
6. Track cumulative volume (day/week/month) toward 200 lots/month **as a dashboard metric**
7. Feed spread, correlation, session, and risk behavior into AI Brain for sustainable operations

```text
Signal quality + equity protection  →  primary optimization target
Sustainable volume + IB commission  →  secondary business outcome (tracked, not forced)
```

---

## 3. Reporting & Audit Requirements (Supabase + Metabase)

### Purpose

Add a full **Reporting & Audit layer** so the IB operator can visually monitor:

1. Cumulative trading volume
2. Progress toward **200 lots/month**
3. Risk exposure
4. Spread/slippage quality
5. Signal quality
6. Whether volume is **safe** or from **overtrading**

**Target stack:** **Supabase** (system of record) + **Metabase** (visual dashboards)

### Critical rule (extends G10)

Volume target is a **reporting KPI only** — never force trades to reach 200 lots/month.

**200 lots/month must never override:**

| Guard | Current module |
|-------|----------------|
| Signal Gate | `src/signal_gate.py` |
| Risk Manager | `src/lot_calculator.py` + `src/safety_locks.py` |
| Spread Guard | `src/spread_audit.py` + spread lock |
| News Guard | `signal_gate` + `safety_locks` |
| Daily Loss Lock | `src/safety_locks.py` |
| Floating Risk Lock | `src/safety_locks.py` |

```text
Dashboard volume KPI  →  MONITOR ONLY
Trading pipeline      →  RISK-FIRST ALWAYS
```

---

### 3.1 Volume Progress Dashboard

| Metric | Description |
|--------|-------------|
| Today | `daily_lots` |
| This week | `weekly_lots` |
| This month | `monthly_lots` |
| MTD progress | `monthly / 200` |
| Remaining lots | `200 - monthly` |
| Required daily pace | `remaining / trading_days_remaining` |
| Actual daily pace | `monthly / trading_days_passed` |
| Projected month-end | `actual_pace × trading_days_in_month` |

**Example:**

```text
Monthly target:           200 lots
Current month volume:     68.5 lots
Progress:                 34.25%
Remaining:                131.5 lots
Trading days passed:      8
Trading days remaining:   14
Required daily pace:      9.39 lots/day
Current daily pace:       8.56 lots/day
Projected month-end:      188.3 lots
```

**Phase 1 (current):** `src/volume_tracker.py` + HTML dashboard  
**Phase 3–5:** `volume_monthly` SQL view + Metabase gauge

---

### 3.2 Volume Breakdown

Slice volume by: day, week, month, signal ID, client group, risk tier, session (Asia/London/NY), direction, setup type, broker group (if available).

**Metabase charts:** daily bar, weekly trend, monthly gauge, volume by tier/session/signal type.

---

### 3.3 Risk vs Volume Dashboard (Critical)

**Key audit question:** Is volume increasing while equity and drawdown remain controlled?

Metrics: total lots/trades, avg lot, W/L/BE, max floating risk, daily/monthly DD, risk per trade, blocked/reduced trades by guard type.

**Warning:** volume ↑ + drawdown ↑ fast → `UNHEALTHY_VOLUME`

---

### 3.4 Spread & Execution Audit

Record spread at seed, entry, close, max (if available).  
Rule: spread > threshold (e.g. 30 pts) → `HIGH_SPREAD_RISK`; wide spread on pending → `PAUSE_PENDING` / `CANCEL_PENDING`.

---

### 3.5 Signal Quality Dashboard

Approved / waiting / rejected counts, W/L/BE, TP1/TP2/SL hit rates, avg RR, best/worst session & setup, high correlation risk outcomes.

---

### 3.6 IB Business Audit

Daily/weekly/monthly lots, KPI progress, estimated commission (**display only**), active clients/groups, avg lots per client. Commission must not approve trades.

---

### 3.7 Supabase Tables

Full SQL: [`supabase/schema.sql`](../../supabase/schema.sql)

| Table / View | Role |
|--------------|------|
| `signals` | Signal master |
| `trades` | Open/close + lots + PnL |
| `activity_logs` | Event trail |
| `volume_daily` / `weekly` / `monthly` | Aggregates + KPI projection |
| `risk_audit` | Risk snapshots |
| `spread_audit` | Spread quality |

---

### 3.8 Metabase Cards (20)

Monthly gauge, daily bar, weekly trend, vs 200 target, remaining lots, required pace, projected month-end, volume by session/group/tier, risk vs volume, drawdown vs volume, spread warnings, avg spread by session, signal decision summary, W/L/BE, TP hit rates, correlation outcomes, blocked trades by reason, commission estimate.

---

### 3.9 Audit Warning Statuses

| Status | Condition |
|--------|-----------|
| `BELOW_TARGET_PACE` | Below required monthly pace — show catch-up pace only |
| `UNHEALTHY_VOLUME` | Volume up, drawdown up aggressively |
| `BROKER_EXECUTION_RISK` | Frequent spread threshold breaches |
| `OVERTRADE_RISK` | Exceeds daily trade limit |

---

### 3.10 Implementation Phases

| Phase | Deliverable |
|-------|-------------|
| **1** ✅ | Local JSON + HTML dashboard (Phase D) |
| **2** | Supabase tables + pipeline sync |
| **3** | SQL views |
| **4** | Metabase connection |
| **5** | 20 dashboard cards |

No broker execution. No auto-trade from volume target.

---

## 4. Risk-First Volume Philosophy

### Priority stack (never invert)

```text
1. Equity protection
2. Risk control
3. Signal quality
4. Client retention
5. Sustainable volume
6. IB commission
```

### Volume is a business metric, not a decision rule

| Volume IS | Volume IS NOT |
|-----------|---------------|
| Tracked on dashboard | A reason to open more trades |
| Reviewed weekly/monthly | A trigger to increase lot size |
| Compared to 200 lots/month KPI | An override for risk rules |
| Audited for sustainability | A substitute for replay/forward test |

### Positioning guardrail

Do **not** design a system that overtrades for commission. The desk earns trust first; volume follows from retained clients and consistent signal quality.

### Metaphor (preserve in copy and SOP)

| Concept | Metaphor |
|---------|----------|
| Equity | Fuel tank |
| Risk management | Fuel gauge |
| DXY / US10Y | Weather |
| Multi-entry | Splitting a trip into stages |
| Volume | Distance traveled — not a reason to drive recklessly |

---

## 5. Original Brief Problems to Avoid

| Anti-pattern | Why it fails for IB |
|--------------|---------------------|
| Volume-driven entries | Damages client equity and retention |
| Fixed lot without equity/risk math | Breaks trust across client tiers |
| Martingale / recovery sizing | Guardrail violation (G5, existing code blocks) |
| Ignoring spread at seed/close | Hidden slippage erodes execution quality |
| Auto-reject all correlation conflicts | Misses nuanced gold/DXY relationships |
| Auto-approve all correlation alignments | False confidence in macro filter |
| KPI on dashboard forcing trades | Conflicts with risk-first philosophy |
| Profit promises in seeding copy | Guardrail G4 violation |
| Broker execution in MVP | Out of scope — signal ops only |
| CRM / funnel / content engine | Scope creep — not IB desk |

---

## 6. Corrected System Direction

### Keep the adapted Hermes flow

```text
Hermes XAUUSD Agent
  → Telegram DM / Signal Group
  → XAUUSD Trading MCP
  → Strategy Rooms (Market, Signal, Lot, Seeding, Journal, Dashboard, AI Brain)
  → Signal Replay / Forward Test
  → IB Signal Dashboard
  → XAUUSD AI Brain
  → Alex IB Jarvis Vision (deferred)
```

### Add a Risk-First layer across existing rooms

```text
Market Room      → price, session, spread, DXY, US10Y, news risk
Signal Room      → validate + correlation tag + safety locks
Lot Room         → equity-based lot formula + multi-entry split
Seeding Room     → record entry spread at seed time
Journal Room     → close spread, slippage notes, volume lots
Dashboard Room   → risk metrics + volume KPI + spread audit
AI Brain         → learn from journal + spread + correlation tags
```

### Decision outcomes (extend current APPROVE / WAIT / REJECT)

| Decision | Meaning |
|----------|---------|
| `APPROVE` | Proceed to lot + seed + publish path |
| `WAIT` | Conditions unclear — news, correlation, spread pending |
| `REJECT` | Hard block — missing SL, bad RR, safety lock |
| `REDUCE_RISK` | **New** — allow smaller size or fewer entries, not full size |

---

## 7. Data Pipeline Upgrade

### New / extended market fields

| Field | Source (MVP) | Used by |
|-------|--------------|---------|
| `xauusd_price` | Manual stub / future feed | Market Room, journal |
| `dxy_direction` | `bullish` / `bearish` / `neutral` | Signal correlation filter |
| `us10y_direction` | `bullish` / `bearish` / `neutral` | Signal correlation filter |
| `session` | `asia` / `london` / `ny` | Already in `market_context.py` |
| `news_risk` | `low` / `elevated` / `high` | Signal gate + safety lock |
| `spread_pts` | Current spread | Market + spread lock |
| `spread_threshold` | Config (e.g. 30–35 pts) | Spread lock |
| `entry_spread` | Recorded at seed / trigger | Spread audit |
| `close_spread` | Recorded at close | Spread audit |

### Proposed file extensions

```text
data/market_context.json     → add dxy_direction, us10y_direction, xauusd_price
data/signals.json            → add correlation_risk_tag, entry_spread, spread_at_seed
data/spread_audit.jsonl      → new — per-event spread log
data/volume_tracker.json     → new — daily/weekly/monthly lot totals
data/risk_state.json         → new — floating risk %, daily DD, trade count
strategy-rooms/market-room/config.yaml → spread_threshold, correlation rules
```

### Pipeline flow

```text
[get_market_context]
  → enrich with DXY/US10Y + spread
[check_signal]
  → RR + news + correlation tag + safety locks
[calc_lot]
  → equity formula + floating risk check
[seed_signal]
  → capture entry_spread
[publish_signal]
  → Alex approve (G6) — still simulated in MVP until Telegram API wired
[close_signal]
  → journal + close_spread + volume increment + brain
[dashboard]
  → risk + volume KPI + spread audit panels
```

---

## 8. Correlation Filter Design

### Purpose

Gold often reacts to USD strength (DXY) and real-yield pressure (US10Y). The filter **tags and adjusts** — it does not blindly reject every conflict.

### Inputs

- `direction`: `buy` | `sell` on XAUUSD
- `dxy_direction`: `bullish` | `bearish` | `neutral`
- `us10y_direction`: `bullish` | `bearish` | `neutral`

### Conflict matrix (example logic)

| XAUUSD | DXY | US10Y | Severity | Suggested action |
|--------|-----|-------|----------|------------------|
| BUY | bullish | bullish | **High** | `REDUCE_RISK` or `WAIT` |
| BUY | bullish | neutral | Medium | `REDUCE_RISK` |
| SELL | bearish | bearish | **High** | `REDUCE_RISK` or `WAIT` |
| SELL | bearish | neutral | Medium | `REDUCE_RISK` |
| BUY | bearish | bearish | Low (tailwind) | `APPROVE` — note alignment |
| SELL | bullish | bullish | Low (tailwind) | `APPROVE` — note alignment |
| Any | neutral | neutral | None | No correlation tag |

### Output fields on signal record

```json
{
  "correlation_risk_tag": "high | medium | low | aligned | none",
  "correlation_reasons": ["DXY bullish conflicts with XAUUSD BUY"],
  "correlation_action": "WAIT | REDUCE_RISK | APPROVE"
}
```

### Rules

- Do **not** auto-reject every conflict — severity drives `WAIT` vs `REDUCE_RISK`
- Always **log reasons** for dashboard and brain review
- Operator (Alex) can override with explicit approval — logged in publish gate

### Implementation hook

Extend `src/signal_gate.py` → `check_signal()` with optional `dxy_direction` and `us10y_direction` parameters; call from `telegram_router._cmd_check_signal` after `get_market_context()`.

---

## 9. Lot Calculation Logic

### Formula

```text
Lot = (Equity × Risk%) / (SL distance × value per point)
```

Where:

- `Equity` = client account equity (operator input per calc)
- `Risk%` = from client tier (`client_groups.json`) capped by `max_risk_pct`
- `SL distance` = |entry_mid − stop_loss| in price points
- `value per point` = from `pip_value_per_0_01_lot` rules (extend for XAUUSD contract math)

### Hard rules

| Rule | Enforcement |
|------|-------------|
| No SL → no trade | `signal_gate` REJECT (existing) |
| No martingale | `lot_calculator` blocks recovery keywords (existing) |
| No fixed lot without equity/risk | Replace category-only output with computed lot |
| Risk before volume | Lot never scaled to hit 200 lots/month |
| Max floating risk reached | Block new `calc_lot` / publish |
| Spread above threshold | Block or WAIT before lot calc |
| Tier cap | `max_lot` per group in `client_groups.json` |

### Gap vs current MVP

Current `src/lot_calculator.py` returns **risk amount + lot category** — not explicit lot size from SL distance. Upgrade must add `suggested_lot` numeric output and `value_per_point` config for XAUUSD.

### Example

```text
Equity = 10,000
Risk%  = 1.0% (standard tier)
Risk$  = 100
SL dist = 9.0 points (e.g. 4090 → 4099 sell)
Value/pt per 0.01 lot = 0.1 (config)
Lot = 100 / (9 × 10) ≈ 1.11 → cap by max_lot tier
```

---

## 10. Multi-Entry Rules

### Allowed when

- Total risk across all entries **equals** the original single-entry risk plan
- Each leg has defined entry level and partial lot
- Sum of leg lots ≤ original `suggested_lot`
- Safety locks (floating risk, spread, daily DD) pass for the **combined** plan

### Example (valid)

```text
Original plan: 0.30 lot, 1.0% equity risk
Split:
  Entry 1: 0.10 @ 4092
  Entry 2: 0.10 @ 4090
  Entry 3: 0.10 @ 4088
Total risk unchanged — same SL, same aggregate risk$
```

### Forbidden

| Pattern | Why |
|---------|-----|
| Split to secretly add risk | Violates risk-first philosophy |
| Split to force volume | Volume is not a trade objective |
| Split to bypass max floating risk | Safety lock circumvention |
| Extra entry after full size filled | Requires new signal / new calc |

### Data model

```json
{
  "entries": [
    {"leg": 1, "lot": 0.10, "entry": 4092.0, "status": "pending"},
    {"leg": 2, "lot": 0.10, "entry": 4090.0, "status": "pending"},
    {"leg": 3, "lot": 0.10, "entry": 4088.0, "status": "pending"}
  ],
  "total_lot": 0.30,
  "risk_budget_usd": 100.0,
  "multi_entry_allowed": true
}
```

### MCP tool candidate

`split_entries(signal_id, legs[])` — validates sum(lots) == original and risk unchanged.

---

## 11. Safety Trigger Rules

### 1. Floating risk lock

```text
IF total_floating_risk >= 3% of equity
THEN block new trades (REJECT or WAIT on check_signal / calc_lot)
```

Track open signals + unrealized risk in `data/risk_state.json`.

### 2. Spread lock

```text
IF spread_pts > spread_threshold (e.g. 30)
THEN pause or cancel pending signals
```

Repo today: `SPREAD_THRESHOLD = 35` in `market_context.py` — align config with operator preference (30 vs 35).

### 3. News lock

```text
IF news_risk == high
THEN WAIT or REDUCE_RISK (existing partial — extend to REDUCE_RISK)
```

### 4. Daily loss lock

```text
IF daily_drawdown >= daily_limit (config per tier or desk-wide)
THEN block new signals for remainder of session/day
```

### 5. Trade count lock

```text
IF open_trades + new_signal > max_trades_per_day
THEN block new signals
```

### Safety evaluation order

```text
1. Missing SL / bad RR        → REJECT
2. Daily loss lock              → REJECT
3. Floating risk lock           → REJECT
4. Trade count lock             → REJECT
5. Spread lock                  → WAIT (pending) / cancel pending
6. News lock                    → WAIT / REDUCE_RISK
7. Correlation conflict         → WAIT / REDUCE_RISK
8. All clear                    → APPROVE
```

### New module candidate

`src/safety_locks.py` — single `evaluate_safety_locks(equity, risk_state, market_ctx) -> dict`.

---

## 12. Dashboard Upgrade

### Current state (MVP)

`src/dashboard.py` exports: total/open/closed signals, W/L/BE, PnL, lot categories, lessons.

### Risk metrics panel (add)

| Metric | Source |
|--------|--------|
| Equity (last used) | `risk_state.json` |
| Floating risk % | Sum open signal risk / equity |
| Daily drawdown | Journal + open PnL |
| Max risk used today | Risk state |
| Open trades | `signals.json` status live |
| Approved / rejected / waiting counts | Gate cache or signal audit log |

### Volume metrics panel (add)

| Metric | Source |
|--------|--------|
| Daily lots | `volume_tracker.json` |
| Weekly lots | Aggregated |
| Monthly lots | Aggregated |
| Progress to 200 lots/month | `monthly_lots / 200` — display only |
| Avg lot per signal | volume / signal count |
| Signals needed at avg lot | **informational** — `(200 - monthly) / avg_lot` with disclaimer |

### Spread audit panel (add)

| Metric | Source |
|--------|--------|
| Avg entry spread | `spread_audit.jsonl` |
| Avg close spread | Same |
| Max spread seen | Same |
| Spread warning count | spread > threshold events |
| Signals blocked by spread | Safety lock log |
| Slippage events | entry_spread vs trigger_spread delta |

### Signal quality panel (extend)

| Metric | Source |
|--------|--------|
| Win / loss / breakeven | Journal (existing) |
| Best / worst session | Brain (existing) |
| Best setup type | Brain + journal |
| Repeated mistakes | Brain (existing) |
| High correlation risk outcomes | Journal filtered by `correlation_risk_tag` |

### HTML

Extend `dashboard/ib-signals/index.html` with three sections: **Risk**, **Volume KPI**, **Spread Audit**.

---

## 13. Spread Audit Design

### Record spread at three events

| Event | When | Field |
|-------|------|-------|
| Seed | `seed_signal` runs | `spread_at_seed` |
| Entry trigger | Signal goes live / first fill (manual log in MVP) | `spread_at_entry` |
| Close | `close_signal` runs | `spread_at_close` |

### Audit log format (`data/spread_audit.jsonl`)

```json
{
  "ts": "2026-06-29T16:00:00Z",
  "signal_id": "sig-sell-4088",
  "event": "seed | entry | close",
  "spread_pts": 28.0,
  "threshold": 30.0,
  "spread_ok": true,
  "session": "london",
  "note": ""
}
```

### Uses

- Broker quality audit (widening patterns by session)
- Slippage review (`spread_at_entry - spread_at_seed`)
- Client protection (block publish when spread bad)
- Brain input (“spread widened on 40% of london sells”)

### Slippage flag

```text
IF spread_at_entry - spread_at_seed > slippage_tolerance
THEN tag signal with slippage_warning in journal
```

---

## 14. AI Brain Upgrade

### Current state

`src/ai_brain.py` learns from **journal only** (min 3 entries): best/worst session, mistakes, setup notes.

### Additional inputs (post-upgrade)

| Input | Brain question answered |
|-------|-------------------------|
| Journal outcomes | Which setups work best? |
| Session tags | Which sessions are safest? |
| `correlation_risk_tag` | Which DXY/US10Y conditions create risk? |
| Spread audit | How often does spread affect execution? |
| REDUCE_RISK / WAIT history | Which signals should have been skipped? |
| Volume tracker + equity | Is volume growing while equity protected? |
| Trade frequency | Sustainable volume vs overtrading? |

### New insight fields (proposed)

```json
{
  "insights": {
    "best_session": "london",
    "worst_session": "asia",
    "high_correlation_loss_rate": 0.67,
    "spread_block_rate": 0.12,
    "avg_entry_spread": 27.5,
    "monthly_volume_lots": 45.2,
    "volume_kpi_progress": 0.226,
    "sustainable_volume_note": "Volume rising with stable avg risk%; no overtrade pattern.",
    "overtrading_warning": false
  }
}
```

### Rules (preserve)

- **Do not invent profit** — brain reads structured data only
- **Do not promise outcomes** in generated copy
- Minimum sample sizes per insight type (e.g. 5 correlation-tagged trades before correlation insight)

---

## 15. Direct Mapping to Existing Hermes XAUUSD IB Desk

| Upgrade area | Existing artifact | Status | Upgrade action |
|--------------|-------------------|--------|----------------|
| Market context | `src/market_context.py` | Partial | Add DXY, US10Y, price, configurable spread threshold |
| Signal validate | `src/signal_gate.py` | Partial | Add correlation filter + `REDUCE_RISK` |
| Lot calc | `src/lot_calculator.py` | Partial | Add full lot formula + floating risk check |
| Multi-entry | — | Missing | New `src/multi_entry.py` + MCP tool |
| Safety locks | Guardrails G5 only | Partial | New `src/safety_locks.py` |
| Spread audit | — | Missing | New `src/spread_audit.py` + jsonl |
| Volume tracker | — | Missing | New `src/volume_tracker.py` |
| Dashboard | `src/dashboard.py` + HTML | Partial | Add risk/volume/spread panels |
| AI Brain | `src/ai_brain.py` | Partial | Ingest spread + correlation + volume |
| MCP tools | `mcp/xauusd-trading/server.py` | 11 tools | Add `create_signal`, `split_entries`, `safety_check`, extend existing |
| Replay gate | `src/signal_replay.py` | Done | No change |
| Publish gate | `src/publish_gate.py` | Done | Add spread check before publish |
| Telegram | Hermes + bot live | In progress | Real publish API deferred |
| Guardrails | `docs/guardrails.md` | Done | Add G10 volume-not-objective explicit rule |
| Client tiers | `data/client_groups.json` | Done | Add daily DD limit, max trades/day |
| Knowledge | This asset | New | Link from README + main knowledge asset |

### Room mapping

| Room | Upgrade focus |
|------|---------------|
| Market Room | DXY, US10Y, spread threshold, price |
| Signal Room | Correlation tag, safety locks, REDUCE_RISK |
| Lot Room | Full lot formula, multi-entry split |
| Seeding Room | Record spread at seed |
| Journal Room | Close spread, volume lots, slippage notes |
| Dashboard Room | Risk + volume KPI + spread audit |
| AI Brain Room | Correlation + spread + sustainable volume insights |

---

## 16. MVP Implementation Notes for Cursor

### Phase D scope (recommended next build)

**Goal:** Risk-first extensions on file-based MVP — no broker API, no CRM.

### Build order (dependency-safe)

```text
1. data schemas + config (market-room, client-groups, risk_state, volume_tracker, spread_audit)
2. safety_locks.py
3. market_context.py — DXY/US10Y/price fields
4. signal_gate.py — correlation filter + REDUCE_RISK
5. lot_calculator.py — full lot formula
6. spread_audit.py — seed/entry/close hooks
7. volume_tracker.py — increment on close
8. multi_entry.py — split validation
9. dashboard.py + index.html — new panels
10. ai_brain.py — extended insights
11. telegram_router.py + MCP server — wire new tools
12. tests — safety locks, correlation, lot formula, spread log, volume aggregate
```

### New / extended MCP tools

| Tool | Priority |
|------|----------|
| `create_signal` | High — removes manual JSON edits |
| `safety_check` | High |
| `split_entries` | Medium |
| `record_spread` | Medium |
| Extend `check_signal` | High — correlation + locks |
| Extend `calc_lot` | High — numeric lot |
| Extend `dashboard` | High |
| Extend `brain` | Medium |

### Config defaults (calibrate with Alex)

```yaml
# strategy-rooms/market-room/config.yaml
spread_threshold_pts: 30
slippage_tolerance_pts: 5
floating_risk_cap_pct: 3.0
daily_drawdown_cap_pct: 3.0
max_trades_per_day: 5
volume_kpi_monthly_lots: 200
xauusd_value_per_point_per_0_01_lot: 0.1
```

### New guardrail (propose G10)

**G10 — Volume Is Not Objective:** Dashboard may display volume KPI progress. No tool, cron, or agent prompt may increase trade frequency, lot size, or signal count to meet volume targets.

### Tests to add

- Correlation high → WAIT or REDUCE_RISK, not silent APPROVE
- Floating risk 3% → block new calc_lot
- Spread 31 > threshold 30 → WAIT
- Multi-entry split sum lot equals original
- Volume tracker increments on close only
- Brain does not invent insights below min sample

### Out of scope (Phase D)

- Live DXY/US10Y price feeds (manual direction input OK)
- Real Telegram publish (separate task)
- Broker execution
- Alex IB Jarvis Vision

---

## 17. Next Prompt to Run with `$mvp-code-builder`

Copy and run:

```text
$mvp-code-builder

PROJECT: Hermes XAUUSD IB Trading Desk
WORKDIR: hermes-xauusd-ib-desk
KNOWLEDGE ASSET: knowledge/distilled/hermes-xauusd-risk-first-volume-desk-upgrade.md

TASK: Implement Phase D — Risk-First Volume Desk upgrade on the existing file-based MVP.

BUILD IN THIS ORDER:
1. Add config defaults to strategy-rooms/market-room/config.yaml (spread 30, floating risk 3%, daily DD 3%, max trades/day 5, volume KPI 200 lots/month display-only).
2. Create src/safety_locks.py — evaluate floating risk, spread, news, daily DD, trade count locks.
3. Extend src/market_context.py — add xauusd_price, dxy_direction, us10y_direction, spread_threshold from config.
4. Extend src/signal_gate.py — DXY/US10Y correlation filter; return REDUCE_RISK where appropriate; store correlation_risk_tag on result.
5. Upgrade src/lot_calculator.py — Lot = (Equity × Risk%) / (SL distance × value per point); respect max_lot and safety locks.
6. Create src/spread_audit.py + data/spread_audit.jsonl — log spread at seed, entry, close.
7. Create src/volume_tracker.py + data/volume_tracker.json — track daily/weekly/monthly lots; KPI progress display only.
8. Create src/multi_entry.py — split entries only if total risk unchanged.
9. Add MCP tool create_signal — register signal in data/signals.json from Telegram/Hermes.
10. Extend dashboard.py and dashboard/ib-signals/index.html — risk panel, volume KPI panel, spread audit panel.
11. Extend ai_brain.py — insights from spread audit, correlation tags, volume vs equity protection.
12. Add tests in tests/ for safety locks, correlation, lot formula, multi-entry, volume tracker.
13. Update docs/guardrails.md with G10 (volume is not objective).

CONSTRAINTS:
- No broker API, no client passwords, no CRM, no profit guarantees.
- Volume KPI is dashboard-only — never a trade trigger.
- Keep existing replay/forward-test/publish gate flow.
- Match existing code style in src/ and mcp/xauusd-trading/server.py.
- Run tests/run_tests.py — all must pass.

ACCEPTANCE:
- check_signal returns correlation tag and REDUCE_RISK when DXY conflicts with XAUUSD BUY.
- calc_lot returns numeric suggested_lot from equity and SL distance.
- spread logged at seed and close.
- dashboard shows monthly volume progress toward 200 lots without affecting trade decisions.
- create_signal works from MCP without manual JSON edit.
```

---

## Asset Recommendations

| Asset | Path | Action |
|-------|------|--------|
| Supabase schema | `supabase/schema.sql` | Phase 2 reporting |
| Guardrail G10 draft | `docs/guardrails.md` | Add in Phase D |
| Market room config | `strategy-rooms/market-room/config.yaml` | Extend |
| SOP addendum | `docs/sop-ops-runbook.md` | Add risk-first daily review section |
| Cursor rule update | `.cursor/rules/hermes-xauusd-desk.mdc` | Reference volume-not-objective |

## Skill Candidates

| Candidate | Purpose |
|-----------|---------|
| `xauusd-risk-first-desk` | Agent skill for risk-first IB operations |
| `spread-audit-review` | Weekly spread/slippage audit playbook |

## Acceptance Criteria (knowledge asset)

- [x] All 16 sections present
- [x] Mapped to existing repo files and gaps
- [x] Volume KPI explicitly non-decision
- [x] Correlation filter design with WAIT / REDUCE_RISK
- [x] MVP implementation order for Cursor
- [x] Next `$mvp-code-builder` prompt included
- [ ] Phase E code (Supabase sync + Metabase)

---

## Related

- [hermes-xauusd-ib-desk-knowledge-asset.md](./hermes-xauusd-ib-desk-knowledge-asset.md)
- [docs/architecture.md](../../docs/architecture.md)
- [docs/guardrails.md](../../docs/guardrails.md)
- [docs/mvp-build-map.md](../../docs/mvp-build-map.md)
- [supabase/schema.sql](../../supabase/schema.sql)
