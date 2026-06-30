# Task — Supabase + Metabase Reporting OPS

> Agent/operator checklist. Full SOP: [knowledge/ops/supabase-metabase-reporting-sop.vi.md](../knowledge/ops/supabase-metabase-reporting-sop.vi.md)

## Status (Hermes XAUUSD) — updated 2026-06-30

| Step | Task | Status |
|------|------|--------|
| E1 | Run `supabase/schema.sql` | ✅ |
| E2 | Create `supabase/.env` (`sb_secret_...`) | ✅ |
| E3 | `python scripts/sync_to_supabase.py` | ✅ live (signals 4, activity 13) |
| 4.1 | Start Metabase (`scripts/start_metabase.ps1`) | ✅ |
| 4.2 | Connect Session pooler + SSL require | ✅ |
| 4.3 | Browse tables + smoke SQL | ⬜ |
| 5.1 | Create collection + dashboard | ⬜ |
| 5.2 | Add 20 cards from `metabase/cards.sql` | ⬜ |
| 6 | Vercel portal | ⏸ deferred |
| **F1–F8** | Phase F pipeline + sig-test-001 | ✅ |
| **G** | Live DXY/US10Y + correlation_data | ⬜ next |

## Credentials (confirmed)

```text
project_ref: tikouskusgdygktslmzj
supabase_url: https://tikouskusgdygktslmzj.supabase.co
api_keys: Settings → API Keys (sb_secret for .env, NOT publishable)
pooler_host: aws-1-ap-south-1.pooler.supabase.com
db_user: postgres.tikouskusgdygktslmzj
```

## Quick commands

```powershell
python tests/run_tests.py
python scripts/sync_to_supabase.py --dry-run
python scripts/sync_to_supabase.py
python scripts/run_sig_test_001.py --live
```

## Exit criteria (production-ready Supabase)

- [x] Live batch sync `ok: true`
- [x] `signals` ≥ 1 row in Supabase
- [ ] Rotate secret if exposed in chat
- [ ] `sig-test-001` rows via `--live`
- [ ] Metabase `select count(*) from signals` ≥ 1
- [ ] G10 footer on volume KPI cards
