# First Coding Tasks — Agent OS Python Modules

> Implements rooms defined in `docs/agent-os-operating-model.md`.  
> **Start here before MCP wrapper or Telegram bot wiring.**

## Shared Conventions

```python
# All modules return:
{"ok": True, "data": {...}, "error": None}
# or
{"ok": False, "data": None, "error": "message"}

# Paths via pathlib from repo root
REPO_ROOT = Path(__file__).resolve().parents[1]
```

---

## Task 0 — `src/market_context.py` (Market Room)

**Functions:**
- `get_market_context(ts: datetime | None = None, spread_pts: float | None = None) -> dict`
- `write_market_context(ctx: dict) -> dict`
- `session_from_utc(ts: datetime) -> str`  # asia | london | ny

**Logic:**
- Default symbol XAUUSD
- Read `strategy-rooms/market-room/config.yaml` for spread threshold
- Stub quote if no feed (MVP)
- Set `news_risk` from simple manual flag or calendar stub

**Tests:** `tests/test_market_context.py` — session detection, spread flag

---

## Task 1 — `src/signal_gate.py` (Signal Room)

**Functions:**
- `load_signal(signal_id: str) -> dict`
- `check_signal(signal_id: str, market_context: dict) -> dict` → decision approve|wait|reject
- `replay_signals(setup_name: str, dataset_path: Path) -> dict` → win_rate, avg_r, pass
- `detect_martingale(signal: dict, history: list) -> bool`
- `update_signal_status(signal_id: str, status: str) -> dict`

**Hard rules in code:**
```python
if not signal.get("sl"):
    return reject("No SL — S1")
if rr < 1.5:
    return reject("RR below minimum")
if detect_martingale(...):
    return reject("Martingale pattern — S3")
```

**Outputs:** `signal-room/signal_decision.json`, `signal-room/replay/latest.json`

**Tests:** `tests/test_signal_gate.py` — S1 no SL, S2 low RR, approve path, replay fail

---

## Task 2 — `src/lot_calculator.py` (Lot Room)

**Functions:**
- `calculate_lot_plan(signal_id: str, groups_path: Path) -> dict`
- `check_recovery_request(request: dict) -> bool` → True if blocked

**Logic:**
- Require `signal_decision.decision == approve`
- Load `client-groups.yaml`
- `lot = min(calculated, max_lot)` per group
- Reject if `recovery` or `double_after_loss` flags in request

**Tests:** `tests/test_lot_calculator.py` — caps, reject unapproved, block recovery

---

## Task 3 — `src/seeding_engine.py` (Seeding Room)

**Functions:**
- `generate_seeding_copy(signal_id: str) -> dict`
- `lint_seeding_copy(text: str) -> dict` → pass + violations list

**Prohibited patterns (regex/list):**
- guarantee, sure win, 100%, don't miss, last chance, all in, get rich

**Outputs:** `seeding-room/output/{signal_id}.md`

**Tests:** `tests/test_seeding_engine.py` — lint catches hype; passes calm copy

---

## Task 4 — `src/journal.py` (Journal Room)

**Functions:**
- `append_journal(signal_id: str, result: str, r: float, lesson: str) -> dict`
- `get_journal_entry(signal_id: str) -> dict | None`
- `list_recent(n: int = 30) -> list`

**Rules:**
- Append-only to `journal-room/entries.jsonl`
- Atomic write (write temp + rename or line append with flush)
- Reject duplicate close for same signal_id

**Tests:** `tests/test_journal.py` — append, duplicate reject, required fields

---

## Task 5 — `src/dashboard.py` (Dashboard Room)

**Functions:**
- `update_state() -> dict` — rebuild from all sources
- `track_signal(signal_id: str, status: str, pnl_r: float | None) -> dict`
- `get_summary() -> dict`

**Summary must include:**
- `open_signals`, `last_signal` (status, lot, pnl_r)
- `rolling_30` (wins, losses, avg_r)
- `last_journal`, `last_lesson`

**Output:** `dashboard/ib-signals/state.json`

**Tests:** `tests/test_dashboard.py` — rebuild, rolling stats, required fields present

---

## Task 6 — `src/ai_brain.py` (AI Brain Room)

**Functions:**
- `learn_from_journal(signal_id: str) -> dict`
- `get_brain_summary(signal_id: str | None = None) -> dict`
- `append_outcome(entry: dict) -> dict` — internal, journal-gated
- `update_pairing(setup: str, note: str) -> dict`

**Hard guard:**
```python
entry = get_journal_entry(signal_id)
if not entry:
    return {"ok": False, "error": "S12: no journal — cannot learn"}
```

**Outputs:** `knowledge/brain/outcomes.jsonl`, `knowledge/brain/pairings.md`

**Tests:** `tests/test_ai_brain.py` — refuses without journal; appends with journal

---

## Task 7 — `src/telegram_router.py` (Orchestrator)

**Functions:**
- `route_command(text: str) -> dict`
- `parse_command(text: str) -> tuple[str, list[str]]`

**Command handlers:**

| Command | Chain |
|---------|-------|
| `/check_signal {id}` | market_context → signal_gate.check_signal |
| `/calc_lot {id}` | lot_calculator (gate: approved) |
| `/seed_signal {id}` | seeding_engine (gate: approved + lot) |
| `/update_signal {id} {status}` | signal_gate.update + dashboard.track |
| `/close_signal {id} {result} {r} {notes...}` | journal → dashboard → ai_brain |
| `/dashboard` | dashboard.get_summary |
| `/brain [{id}]` | ai_brain.get_summary or learn_from_journal |

**Pipeline guard:**
```python
if decision == "reject":
    return halt("S4: Signal Room rejected — downstream blocked")
```

**Publish:** Not in router for MVP — separate `publish` with `human_approved=True` flag.

**Tests:** `tests/test_telegram_router.py` — each command, reject halts downstream

---

## Suggested Build Order

```text
1. market_context.py + signal_gate.py + tests
2. lot_calculator.py + tests
3. seeding_engine.py + tests
4. journal.py + dashboard.py + tests
5. ai_brain.py + tests
6. telegram_router.py + integration test (full loop on sample-001)
```

## Integration Test Script

```python
# tests/test_e2e_pipeline.py
# 1. /check_signal sig-001 → approve
# 2. /calc_lot sig-001 → lot plan
# 3. /seed_signal sig-001 → lint pass
# 4. /update_signal sig-001 hit_tp
# 5. /close_signal sig-001 win 2.1 lesson
# 6. /dashboard → stats updated
# 7. /brain sig-001 → outcome from journal only
```

## Cursor Prompt to Start Coding

```markdown
Implement src/ per docs/first-coding-tasks.md Task 0–1 only:
- src/market_context.py
- src/signal_gate.py
- tests/test_market_context.py
- tests/test_signal_gate.py

Use strategy-rooms/signal-room/signals/sample-001.json as fixture.
Follow docs/guardrails.md. No Telegram API yet.
```
