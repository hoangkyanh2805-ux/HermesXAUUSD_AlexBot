# Dashboard Room — Mission Prompt

## Mission
Aggregate and display **signal status, lot, PnL, journal entries, and lessons** for operator and clients.

## Inputs
- `signal-room/` decisions and live status
- `lot-room/lot_plan.json`
- `journal-room/entries.jsonl`
- `knowledge/brain/outcomes.jsonl` and `pairings.md`

## Tool
`src/dashboard.py` → `update_state()`, `get_summary()`, `track_signal()`

## Procedure
1. On `/update_signal` → update signal status (open / hit_tp / hit_sl / manual_close).
2. On journal append → refresh rolling stats (W/L, avg R last 30).
3. Rebuild `dashboard/ib-signals/state.json`.
4. Serve read-only summary for `/dashboard` and static HTML view.

## Permissions
- Autonomous read all desk data
- Autonomous write `dashboard/state.json`
- **Cannot** publish externally
- **Cannot** modify journal or brain (read-only source)

## Stop Conditions
- Unknown signal_id → return error
- Corrupt state file → rebuild from sources

## Failure Modes
- Stale open signal (>48h no update) → flag in summary
- Stats mismatch vs journal → prefer journal as truth for closed

## Escalation
Data conflict → log warning; journal wins for closed signals.

## Example Command
```text
/dashboard
```

```text
/update_signal sig-001 hit_tp
```

## Example Output (`/dashboard`)
```json
{
  "open_signals": [],
  "last_signal": {
    "id": "sig-001",
    "status": "closed_tp",
    "lot_standard": 0.02,
    "pnl_r": 2.1
  },
  "rolling_30": { "wins": 18, "losses": 12, "avg_r": 1.6 },
  "last_journal": "sig-001 win +2.1R — Clean London breakout",
  "last_lesson": "london-breakout + low spread → win"
}
```

## Must Display
- [ ] Signal status
- [ ] Lot (per group tier)
- [ ] PnL (R-multiple)
- [ ] Journal excerpt
- [ ] Latest lesson from brain

## Do Not
- Invent PnL
- Write to journal or brain
- Optimize for signal volume metrics
