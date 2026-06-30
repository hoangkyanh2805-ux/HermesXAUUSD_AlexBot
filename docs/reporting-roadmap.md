# Reporting Roadmap — Phases 2–6

> Internal BI = **Metabase**. Vercel = optional later (Phase 6).

## Phase map

| Phase | Name | Status | Deliverable |
|-------|------|--------|-------------|
| **D** | Risk-First Volume Desk | ✅ Done | Local pipeline, safety locks, volume KPI |
| **E** | Supabase sync | ✅ Done | `scripts/sync_to_supabase.py`, `supabase/schema.sql` |
| **2–3** | *(in knowledge §3.10)* | ✅ Done | Tables + `volume_*` views in Supabase |
| **4** | Metabase → Supabase | **Next** | PostgreSQL connection, schema sync |
| **5** | Metabase dashboard cards | After 4 | Volume, risk, spread, signal audit (20 cards) |
| **6** | Vercel *(optional)* | Deferred | Custom portal only if Metabase is not enough |

```text
Hermes desk → data/*.json → sync script → Supabase → Metabase (Phases 4–5)
                                                      ↘ Vercel (Phase 6, optional)
```

## Phase 4 — Connect Metabase

**Goal:** Internal BI dashboard on live Supabase data.

1. Run sync at least once: `python scripts/sync_to_supabase.py`
2. Create Metabase (cloud or Docker)
3. Add PostgreSQL database → Supabase host `db.tikouskusgdygktslmzj.supabase.co`, SSL on
4. Confirm tables: `signals`, `trades`, `activity_logs`, `risk_audit`, `spread_audit`, views `volume_*`

→ Full steps: [metabase-phase4-connect.md](metabase-phase4-connect.md)

## Phase 5 — Build dashboard cards

**Goal:** Operator-facing KPIs — volume, risk, spread, signal audit.

- Copy SQL from [`metabase/cards.sql`](../metabase/cards.sql) into Metabase **New → SQL question**
- Group into one dashboard: **Hermes XAUUSD IB Desk**
- **G10:** 200 lots/month is display-only — never a trading trigger

→ Card-by-card guide: [metabase-phase5-dashboard.md](metabase-phase5-dashboard.md)

## Phase 6 — Vercel *(optional)*

**Only if you need:**

- Client-facing branded portal
- Custom operator UI beyond Metabase
- Public URL with auth wrapper

**Not needed when:**

- Metabase covers internal BI (recommended default)
- `dashboard/ib-signals/index.html` is enough for local HTML preview

Do **not** deploy Hermes gateway, MCP, or sync scripts to Vercel.

## Related

- **[SOP OPS — Supabase + Metabase](../knowledge/ops/supabase-metabase-reporting-sop.vi.md)** — reusable knowledge
- [Task checklist](../workbook/ops/supabase-metabase-task.md)
- [supabase-metabase-setup.md](supabase-metabase-setup.md)
- [metabase-phase4-connect.md](metabase-phase4-connect.md)
- [metabase-phase5-dashboard.md](metabase-phase5-dashboard.md)
- [guardrails.md](guardrails.md) — G10
