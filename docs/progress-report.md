# Hermes XAUUSD IB Desk — Progress Report

> **Generated:** 2026-06-30 (Phase G + Metabase import complete)  
> **Principle:** Risk-First Volume Desk — 200 lots/month is **reporting KPI only** (G10).

---

## Executive summary

| Layer | Status | Evidence |
|-------|--------|----------|
| Local pipeline (Phase C–F) | **Verified** | `python tests/run_tests.py` → **36+ passed** |
| Phase G live market data | **Verified** | Yahoo Finance DXY + US10Y (`source=live`) |
| Correlation log | **Verified** | `CORRELATION_RISK` + `correlation_data` on Supabase |
| Supabase live sync | **Verified** | `sync_to_supabase.py` → trades + signals OK |
| Schema migration G | **Applied** | `002_phase_g.sql` via `run_supabase_migration.py` |
| Metabase dashboard | **Verified** | `import_metabase_dashboard.py` → 20 cards, dashboard/2 |
| Volume KPI data | **Verified** | `volume_monthly` → 5.0 / 200 lots (2.5%) |

**Status label:**

> **Production-ready** — desk, Supabase, Metabase reporting stack operational.

---

## Phase map

| Phase | Status |
|-------|--------|
| D Risk-First desk | ✅ |
| E Supabase batch sync | ✅ |
| F Per-step writer + sig-test | ✅ |
| **G Live DXY/US10Y + correlation** | ✅ |
| 4 Metabase connect | ✅ |
| 5 Metabase cards | ✅ automated import |
| 6 Vercel | ⏸ deferred |
| **3 Journal + Brain reconcile** | 📋 planned — [journal-brain-execution-plan.md](journal-brain-execution-plan.md) |

---

## Verify commands (run anytime)

```powershell
python scripts/verify_production.py
python scripts/run_sig_test_001.py --live
python scripts/sync_to_supabase.py
python scripts/run_supabase_migration.py supabase/migrations/002_phase_g.sql
python scripts/import_metabase_dashboard.py
```

Smoke SQL: `scripts/metabase_smoke.sql`

---

## Operator — Metabase

1. `metabase/.env` — Metabase login (not Supabase DB password)
2. `python scripts/import_metabase_dashboard.py`
3. Open `http://localhost:3000/dashboard/2`
4. Refresh after `sync_to_supabase.py` for volume cards

---

## Related

- [metabase-phase5-dashboard.md](metabase-phase5-dashboard.md)
- [knowledge/ops/supabase-metabase-reporting-sop.vi.md](../knowledge/ops/supabase-metabase-reporting-sop.vi.md)
