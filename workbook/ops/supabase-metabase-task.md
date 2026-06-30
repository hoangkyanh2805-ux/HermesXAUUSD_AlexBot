# Task — Supabase + Metabase Reporting OPS

> Agent/operator checklist. Full SOP: [knowledge/ops/supabase-metabase-reporting-sop.vi.md](../knowledge/ops/supabase-metabase-reporting-sop.vi.md)

## Status (Hermes XAUUSD)

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

## Quick commands

```powershell
# Phase E
python scripts/sync_to_supabase.py --dry-run
python scripts/sync_to_supabase.py

# Phase 4
powershell -ExecutionPolicy Bypass -File scripts\start_metabase.ps1
# → http://localhost:3000
```

## Connection template (fill per project)

```text
project_ref: tikouskusgdygktslmzj
pooler_host: aws-1-ap-south-1.pooler.supabase.com
pooler_port: 5432
db_user: postgres.tikouskusgdygktslmzj
ssl_mode: require
```

## Exit criteria

- [ ] Metabase **Connected** (green)
- [ ] `select count(*) from signals` ≥ 1
- [ ] Dashboard collection created
- [ ] G10 footer on volume KPI cards
- [ ] No secrets committed
