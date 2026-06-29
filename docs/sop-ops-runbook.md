# SOP / Ops Runbook — Hermes XAUUSD IB Trading Desk

> Owner: **Alex (IB operator)**  
> System: Hermes XAUUSD Agent + 5 Strategy Rooms + XAUUSD Trading MCP

## Operating Principles

1. **Quality over volume** — fewer validated signals beat frequent unvalidated ones
2. **Test before broadcast** — replay + forward test gates are non-negotiable
3. **Human approves publish** — especially during MVP and new setup promotion
4. **Every close teaches** — journal + brain update after every signal
5. **No execution in this system** — signals only; clients execute at their broker

---

## Daily Operations

### Morning — Session Prep (15 min)

| Step | Action | Output |
|------|--------|--------|
| 1 | Open Hermes Desktop — verify bot online, gateway healthy | Ops log note |
| 2 | Check `strategy-rooms/market-room/` — run or review market context | `market_context.json` |
| 3 | Review dashboard for open signals | Status confirmed |
| 4 | Check economic calendar for XAUUSD / USD high-impact news | news_risk flag updated |

**Escalation:** Bot offline → restart via Desktop; if fails, manual DM only, no group publish.

### Signal Processing — New Signal (Per Event)

```text
1. Draft signal → Signal Room
2. Hermes: get_market_context
3. Hermes: validate_signal → approve | wait | reject
4. If new setup: replay_signals (must pass)
5. If approve: calculate_lot_plan
6. generate_seeding_copy
7. [ALEX REVIEWS] lot plan + seeding tone
8. [ALEX APPROVES] post_signal_to_telegram
9. Dashboard tracks live status
```

**Stop conditions:**
- `reject` → log reason, do not publish
- `wait` → re-check at next session window
- replay `pass: false` → do not promote; journal the failure

### Evening — Close + Learn (10 min)

| Step | Action | Output |
|------|--------|--------|
| 1 | Close any completed signals | journal entry |
| 2 | Run append_journal + update_brain | outcomes.jsonl + pairings.md |
| 3 | Review dashboard stats (rolling 30) | ops note |
| 4 | Check cron jobs in Hermes Desktop | no runaway schedules |

---

## Weekly Operations

| Day | Task | Owner |
|-----|------|-------|
| Monday | Review replay metrics for active setups | Alex |
| Wednesday | Audit seeding copy for compliance (no profit claims) | Alex |
| Friday | Review brain pairings — confirm or refute patterns | Alex + Hermes |
| Friday | Token/cron audit in Hermes Desktop | Alex |

**Weekly output:** Short ops note in `strategy-rooms/journal-room/weekly-notes.md` (optional).

---

## Monthly Operations

| Task | Purpose |
|------|---------|
| Review client group risk params (`lot-room/client-groups.yaml`) | Ensure lots still appropriate |
| Replay full historical set for live setups | Detect edge decay |
| Archive old journal entries | Keep repo performant |
| Review defer list — any Phase 2 item ready? | Controlled scope expansion |

---

## Approval Gates

| Action | Approver | Tool / Location |
|--------|----------|-----------------|
| New setup → `live` | Alex | STATUS file + replay pass |
| Telegram Signal Group publish | **Alex (MVP: always)** | `post_signal_to_telegram` |
| Seeding copy with session/news context | Alex review | Seeding Room output |
| Cron job creation | Alex | Hermes Desktop |
| Client group risk change | Alex | `lot-room/client-groups.yaml` |

---

## Monitoring

| Signal | Check | Threshold | Action |
|--------|-------|-----------|--------|
| Hermes bot status | Desktop | offline > 5 min | Restart bot |
| Open signal age | Dashboard | > 48h without update | Manual review |
| Replay win rate | Dashboard | < 50% rolling 30 | Pause setup promotion |
| Cron token usage | Desktop | > 2x daily baseline | Disable cron, review missions |
| Seeding compliance | Manual audit | any profit guarantee | Block publish, rewrite |

---

## Escalation Paths

| Level | Condition | Action |
|-------|-----------|--------|
| L1 | Tool error / bad JSON | Retry once; check MCP logs |
| L2 | Replay gate fail on live setup | Pause publishes for that setup; re-replay |
| L3 | Telegram publish failure | Manual post using `signal-format.md`; fix bot |
| L4 | Suspected scope creep (CRM, execution) | Stop work; review guardrails |
| L5 | Client complaint on signal quality | Journal review + brain pairing update |

---

## Backup + Recovery

| Asset | Location | Backup cadence |
|-------|----------|----------------|
| Brain outcomes | `knowledge/brain/outcomes.jsonl` | Git commit daily |
| Journal entries | `strategy-rooms/journal-room/entries.jsonl` | Git commit daily |
| Room configs | `strategy-rooms/*/config.yaml` | Git commit on change |
| Telegram templates | `telegram/` | Git commit on change |

**Recovery:** All MVP state is file-based. `git pull` restores desk state. No database migration needed.

---

## Deployment (MVP)

| Component | Deploy method |
|-----------|---------------|
| MCP server | Local run; document start command in `mcp/README.md` (Phase 1) |
| Dashboard | Open static HTML locally or simple static host |
| Hermes Agent | Existing Hermes install — not deployed from this repo |
| Config changes | Edit YAML/JSON → commit → Hermes picks up on next mission |

---

## Audit Checklist (Monthly)

- [ ] No broker credentials in repo
- [ ] No client passwords in repo or agent context
- [ ] No profit guarantee language in recent seeding copy
- [ ] All live setups have replay pass on file
- [ ] Human approval logged for all publishes (MVP)
- [ ] Cron jobs documented and justified
- [ ] Brain pairings reviewed for accuracy

---

## Related Docs

- [Guardrails](./guardrails.md)
- [Architecture](./architecture.md)
- [MVP Build Map](./mvp-build-map.md)
- [First Sprint](./first-sprint.md)
