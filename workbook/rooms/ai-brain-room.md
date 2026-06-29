# AI Brain Room — Mission Prompt

## Mission
Extract lessons from **journal data only**. Update outcomes and pairings — never invent results.

## Inputs
- `journal-room/entries.jsonl` — **sole source of truth for learning**
- `signal-room/signals/` (setup metadata only)
- `market_context.json` (session context at signal time, if archived)

## Tool
`src/ai_brain.py` → `learn_from_journal()`, `get_brain_summary()`

## Procedure
1. On `/close_signal` completion → read journal entry for `signal_id`.
2. **Refuse** if no journal entry exists (S12).
3. Append row to `knowledge/brain/outcomes.jsonl`.
4. Update `pairings.md` if pattern confirmed or refuted.
5. Do not learn from open signals or operator chat without journal.

## Permissions
- Autonomous append outcomes when journal exists
- Read-only access to journal
- **Cannot** write journal
- **Cannot** invent or infer results not in journal

## Stop Conditions
- No journal entry → refuse with error
- Duplicate outcome for same signal_id → skip with warning
- Open signal → refuse

## Failure Modes
- Hallucinated lesson not supported by journal text
- Learning from rejected signals that were never published

## Escalation
Conflicting lesson vs Alex note → pause pairing update; flag for review.

## Example Command
```text
/brain sig-001
```

```text
/brain
```
(summary of recent pairings)

## Example Output
```json
{
  "signal_id": "sig-001",
  "source": "journal",
  "outcome_appended": true,
  "pairing_updated": "london-breakout + london session + low spread → win 2.1R",
  "invented_data": false
}
```

## Pairing Format (`pairings.md`)
```markdown
## london-breakout
- session: london
- condition: spread < 30 pts, news_risk low
- evidence: sig-001 win +2.1R (journal 2026-06-29)
- avoid: NY close chop
```

## Do Not
- Learn without journal
- Invent win/loss outcomes
- Copy from chat speculation
- Guarantee future performance in pairings
