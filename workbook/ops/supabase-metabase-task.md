# Task — Supabase + Metabase Reporting OPS

> Agent/operator checklist. Full SOP: [knowledge/ops/supabase-metabase-reporting-sop.vi.md](../knowledge/ops/supabase-metabase-reporting-sop.vi.md)

## Status (Hermes XAUUSD) — updated 2026-06-30

| Step | Task | Status |
|------|------|--------|
| E1 | Run `supabase/schema.sql` | ✅ |
| E2 | Create `supabase/.env` | ⬜ operator |
| E3 | `python scripts/sync_to_supabase.py` | ⬜ |
| 4.1 | Start Metabase (`scripts/start_metabase.ps1`) | ✅ |
| 4.2 | Connect Session pooler + SSL require | ✅ |
| 4.3 | Browse tables + smoke SQL | ⬜ |
| 5.1 | Create collection + dashboard | ⬜ |
| 5.2 | Add 20 cards from `metabase/cards.sql` | ⬜ |
| 6 | Vercel portal | ⏸ deferred |
| **F1** | Direct Supabase writer + dry_run | ✅ |
| **F2** | Router hooks per pipeline step | ✅ |
| **F8** | `sig-test-001` runner + test | ✅ dry-run |

## Phase F — next coding (from progress-report)

1. `src/supabase_writer.py` — per-step upsert / dry_run payload
2. Wire `telegram_router.py` (check, lot, seed, publish)
3. `src/activity_log.py` — full event types
4. `supabase/migrations/001_*.sql` — dxy_context, us10y_context, activity types
5. `src/spread_guard.py`
6. `scripts/run_sig_test_001.py`

## Quick commands

```powershell
python tests/run_tests.py
python scripts/sync_to_supabase.py --dry-run
powershell -ExecutionPolicy Bypass -File scripts\start_metabase.ps1
```

## Connection template

```text
project_ref: tikouskusgdygktslmzj
pooler_host: aws-1-ap-south-1.pooler.supabase.com
pooler_port: 5432
db_user: postgres.tikouskusgdygktslmzj
ssl_mode: require
```

## Exit criteria (production-ready Supabase)

- [ ] Per-step direct write OR verified `run_sig_test_001` + Supabase rows
- [ ] `sig-test-001` in `signals` + `activity_logs` + `spread_audit`
- [ ] Metabase `select count(*) from signals` ≥ 1
- [ ] G10 footer on volume KPI cards
- [ ] No secrets committed
