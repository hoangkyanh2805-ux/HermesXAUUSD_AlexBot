# Hermes XAUUSD IB Desk — Progress Report

> **Generated:** 2026-06-30 (Phase F + live Supabase sync)  
> **Purpose:** Verified repo state vs Hermes bot progress report.  
> **Principle:** Risk-First Volume Desk — 200 lots/month is **reporting KPI only** (G10).

---

## Executive summary

| Layer | Status | Evidence |
|-------|--------|----------|
| Local pipeline (Phase C–D) | **Verified** | `python tests/run_tests.py` → **33+ passed** |
| Supabase per-step writer | **Verified** | `src/supabase_writer.py`; router hooks |
| Supabase batch sync (live) | **Verified** | `sync_all()` → signals 4, activity_logs 13, spread_audit 2 |
| Project ref | **Confirmed** | `tikouskusgdygktslmzj` (XAUUSD IB DESK) |
| API keys | **New format** | `sb_secret_...` in `supabase/.env` |
| DXY / US10Y pipeline | **Mock** | `market_context.py` `source: "mock"` |
| `sig-test-001` E2E | **Verified dry-run** | `scripts/run_sig_test_001.py` |
| Metabase BI | **Operator partial** | Connected; cards pending |

**Status label:**

> Supabase live sync **verified** on `tikouskusgdygktslmzj`. Next: Phase G (live DXY/US10Y API, correlation log).

---

## 1. Verified completed

| Item | Evidence |
|------|----------|
| Live Supabase sync | `python scripts/sync_to_supabase.py` → `ok: true` (2026-06-30) |
| Batch key normalize fix | `supabase_sync._normalize_batch` — fixes PGRST102 |
| Per-step writer + activity logs | Phase F modules |
| Schema spread_log + context | `schema.sql` + sync payloads |
| Correlation in check_signal | `signal_gate.py` + tests |

---

## 2. Partially completed

| Item | Gap |
|------|-----|
| DXY/US10Y live feed | Mock only — Phase G |
| `correlation_data` column | Not in schema yet |
| Metabase Phase 5 cards | Operator pending |
| Key rotation after chat exposure | Operator should rotate `sb_secret` |

---

## 3. Operator checklist

- [x] `supabase/.env` with `tikouskusgdygktslmzj`
- [x] `schema.sql` on Supabase
- [x] `sync_to_supabase.py` live OK
- [ ] Rotate API secret if exposed in chat
- [ ] `run_sig_test_001.py --live`
- [ ] Metabase cards

---

## 4. Test commands

```powershell
python tests/run_tests.py
python scripts/sync_to_supabase.py --dry-run
python scripts/sync_to_supabase.py
python scripts/run_sig_test_001.py --live
```

---

## Related

- [knowledge/ops/supabase-metabase-reporting-sop.vi.md](../knowledge/ops/supabase-metabase-reporting-sop.vi.md)
- [workbook/ops/supabase-metabase-task.md](../workbook/ops/supabase-metabase-task.md)
