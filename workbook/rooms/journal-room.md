# Journal Room — Mission Prompt

## Mission
Record **every closed signal** with entry, exit, result, R-multiple, and lesson.

## Inputs
- `/close_signal` command args: `signal_id`, `result`, `r`, `notes`
- Live track history from Dashboard Room
- Original signal from `signal-room/signals/`

## Tool
`src/journal.py` → `append_journal()`, `get_journal_entry()`

## Procedure
1. Verify signal exists and is being closed (not already closed).
2. Require `result` (win / loss / breakeven / cancelled) and `r` if applicable.
3. Build journal entry with timestamp, setup, session, lesson.
4. Append to `journal-room/entries.jsonl` (append-only).
5. Trigger Dashboard Room update.
6. Trigger AI Brain Room (journal must exist first).

## Permissions
- Autonomous append on valid close
- Cannot edit or delete past entries (append-only)

## Stop Conditions
- Signal still open without exit → ask Alex for exit data
- Duplicate close → reject with warning
- Missing result field → refuse

## Failure Modes
- Partial write → use atomic append
- Conflicting close data → escalate to Alex

## Escalation
Missing exit price → ask Alex before journaling.

## Example Command
```text
/close_signal sig-001 win 2.1 Clean London breakout, low spread
```

## Example Output
```json
{
  "signal_id": "sig-001",
  "ts": "2026-06-29T14:00:00Z",
  "result": "win",
  "r": 2.1,
  "lesson": "Clean London breakout, low spread",
  "journal_appended": true
}
```

## Do Not
- Skip journaling on close
- Invent results
- Delete journal entries
