---
name: progress-sync-updater
description: >-
  Verify Hermes XAUUSD IB Desk progress claims against the repo, update
  docs/progress-report.md, and produce next tasks plus a safe test plan. Use when
  a Hermes bot, Cursor agent, or developer reports project progress, status sync,
  Phase completion, Supabase/Metabase readiness, or sig-test-001 — never mark
  features complete without file/function/test evidence.
disable-model-invocation: true
---

# Progress Sync Updater

Reconcile **reported progress** with **verified repo state**. Update `docs/progress-report.md` and emit next tasks without scope creep.

## When to use

Invoke when the user or Hermes bot says things like:

- "Phase X is done" / progress update / status sync
- Supabase or Metabase is "complete" or "connected"
- `sig-test-001` / pipeline / direct writes ready
- DXY/US10Y, spread guard, activity logs implemented

## Core rule

**Never mark DONE without evidence.** Acceptable evidence:

- File + function exists and is wired
- Schema column / event type in `supabase/schema.sql`
- Test in `tests/` that exercises the behavior
- Log or data file produced by a command run
- Operator-verified run with output (not assumed)

If only mentioned in chat → **CLAIMED BUT UNVERIFIED**.

## Project scope (do not expand)

Stay inside the Hermes XAUUSD IB Desk flow:

```text
Hermes XAUUSD Agent → Telegram → XAUUSD Trading MCP → Strategy Rooms
→ Signal Replay / Forward Test → IB Signal Dashboard → AI Brain → Jarvis (deferred)
```

**Do not build or recommend:** CRM, Content Engine, X Funnel, BioLink, real broker execution, client passwords, overtrading / volume-forcing logic.

**G10:** 200 lots/month = reporting KPI only — never a trade trigger.

---

## Workflow

### Step 1 — Capture the report

Extract from the incoming message:

- What was claimed complete / in progress
- Phase labels (C, D, E, F, Metabase 4–5, etc.)
- Named artifacts (Supabase, Metabase, sig-test-001, MCP tools)
- Implicit claims (e.g. "production-ready")

### Step 2 — Verify in repo (mandatory)

Run verification before updating docs:

```bash
python tests/run_tests.py
python scripts/sync_to_supabase.py --dry-run
```

Search and read code for each [verification area](verification-checklist.md). Record **file paths + symbols** as evidence.

| Status | Meaning |
|--------|---------|
| **DONE** | Code + tests or runnable proof |
| **PARTIAL** | Exists but incomplete wiring, schema gap, or no E2E |
| **MISSING** | No implementation |
| **UNVERIFIED** | Claimed in chat only |

### Step 3 — Compare report vs codebase

Build a gap table: claim → evidence → verdict.

Pay special attention:

- **Supabase:** batch `sync_all()` ≠ per-step direct writes ≠ production-ready
- **Metabase:** connected UI ≠ data synced ≠ cards built
- **Market data:** `get_market_context()` defaults ≠ live DXY/US10Y feed
- **Activity logs:** schema types ≠ runtime emission

### Step 4 — Update `docs/progress-report.md`

Refresh these sections (keep structure):

1. Executive summary table + "Correction vs claims"
2. §1 Implemented (with file evidence)
3. §2 Partially implemented (gaps explicit)
4. §3 Missing
5. §4 Claimed but unverified
6. §5 Before `sig-test-001` checklist
7. §6 Recommended implementation order
8. §7 Acceptance criteria tracker (update checkboxes)
9. §9 Status label for README

Set **Generated** date to today. Do not delete historical lessons; update in place.

Also update README status line if Supabase/Metabase wording is stale.

### Step 5 — Emit user-facing output

Use the [output template](output-template.md) — all 9 sections required.

### Step 6 — Next tasks (scoped)

List **minimal** coding tasks ordered by dependency. Prefer:

- Direct Supabase writes before new dashboards
- Schema migration before new emitters
- `sig-test-001` integration test before "production-ready" label

Each task: one sentence **what** + **files** + **acceptance check**.

### Step 7 — Safe test plan

Include:

- Commands that run without secrets (`--dry-run`)
- What requires `supabase/.env` (mark operator-only)
- No real broker / no client passwords
- Expected rows or JSON fields after each step
- Rollback: local JSON is SoT for MVP; Supabase is reporting layer

---

## Verification quick map

| Area | Primary paths |
|------|----------------|
| Supabase sync | `src/supabase_sync.py`, `scripts/sync_to_supabase.py`, hooks in `src/dashboard.py`, `src/telegram_router.py` |
| Signals model | `supabase/schema.sql`, `src/supabase_sync.py::_signal_row`, `data/signals.json` |
| Activity logs | `supabase/schema.sql`, `src/supabase_sync.py::_activity_rows`, pipeline emitters |
| DXY / US10Y | `src/market_context.py`, `src/signal_gate.py` |
| Correlation | `src/signal_gate.py`, `tests/test_signal_gate.py` |
| Spread guard | `src/spread_guard.py` or `src/spread_audit.py` + `src/safety_locks.py` |
| Lot calculator | `src/lot_calculator.py`, `tests/test_lot_calculator.py` |
| Multi-entry | `src/multi_entry.py`, `tests/test_phase_d.py` |
| Volume KPI | `src/volume_tracker.py`, `src/reporting_audit.py`, `docs/guardrails.md` G10 |
| E2E sig-test-001 | `tests/`, `data/signals.json`, grep `sig-test-001` |
| MCP | `mcp/xauusd-trading/server.py` |

Full checklist: [verification-checklist.md](verification-checklist.md)

---

## Anti-patterns

- Marking Supabase complete after MCP tool exists without per-pipeline write proof
- Trusting Metabase "Connected" without `select count(*) from signals`
- Adding CRM/funnel/broker scope to "finish" reporting
- Large refactors when progress sync only needs doc + small gaps
- Committing secrets or test passwords in progress report

---

## Related project docs

- `docs/progress-report.md` — canonical status (update target)
- `docs/reporting-roadmap.md` — phases E–6
- `knowledge/ops/supabase-metabase-reporting-sop.vi.md` — ops SOP
- `workbook/ops/supabase-metabase-task.md` — operator checklist
- `docs/guardrails.md` — G10
