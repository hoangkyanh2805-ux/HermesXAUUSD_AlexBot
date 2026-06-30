# Phase 5 — Metabase Dashboard Cards

Build one dashboard: **Hermes XAUUSD IB Desk**

SQL source: [`metabase/cards.sql`](../metabase/cards.sql)

## Layout (4 rows)

```text
Row 1 — Volume KPI (gauge + pace)
Row 2 — Volume trends (daily / weekly / breakdown)
Row 3 — Risk + spread audit
Row 4 — Signal decisions + trade outcomes
```

## Automated import (recommended)

1. Copy credentials:

```powershell
copy metabase\env.example metabase\.env
```

2. Edit `metabase/.env` — set `METABASE_EMAIL` and `METABASE_PASSWORD` (Metabase login, not Supabase).

3. Run:

```powershell
python scripts/import_metabase_dashboard.py
```

Creates collection + **20 cards** + dashboard **Hermes XAUUSD IB Desk** automatically.  
Open the printed `http://localhost:3000/dashboard/<id>` URL.

## Manual import (alternative)

1. Metabase → **New** → **SQL query**
2. Select database `Hermes XAUUSD Supabase`
3. Paste SQL block from `metabase/cards.sql`
4. **Visualize** → pick chart type below
5. Save to collection **Hermes XAUUSD IB Desk**
6. Add to dashboard

## Card reference

### Volume (cards 1–10)

| # | Name | Viz | SQL tag in cards.sql |
|---|------|-----|----------------------|
| 1 | Monthly Volume Progress | Gauge / Progress | `-- CARD 01` |
| 2 | Daily Lots | Bar | `-- CARD 02` |
| 3 | Weekly Lots Trend | Line | `-- CARD 03` |
| 4 | Monthly vs 200 Target | Bar (grouped) | `-- CARD 04` |
| 5 | Remaining Lots | Number | `-- CARD 05` |
| 6 | Required Daily Pace | Number | `-- CARD 06` |
| 7 | Projected Month-End | Number | `-- CARD 07` |
| 8 | Volume by Session | Bar | `-- CARD 08` |
| 9 | Volume by Client Group | Pie / Bar | `-- CARD 09` |
| 10 | Volume by Risk Tier | Pie / Bar | `-- CARD 10` |

### Risk (cards 11–12, 19)

| # | Name | Viz | SQL tag |
|---|------|-----|---------|
| 11 | Risk vs Volume (latest) | Table | `-- CARD 11` |
| 12 | Drawdown over time | Line | `-- CARD 12` |
| 19 | Blocked trades by reason | Bar | `-- CARD 19` |

### Spread (cards 13–14)

| # | Name | Viz | SQL tag |
|---|------|-----|---------|
| 13 | Spread warning count | Number | `-- CARD 13` |
| 14 | Avg spread by session | Bar | `-- CARD 14` |

### Signal audit (cards 15–18)

| # | Name | Viz | SQL tag |
|---|------|-----|---------|
| 15 | Signal decisions | Pie | `-- CARD 15` |
| 16 | Win / Loss / BE | Pie | `-- CARD 16` |
| 17 | Event type breakdown | Bar | `-- CARD 17` |
| 18 | Correlation risk outcomes | Bar | `-- CARD 18` |

### Commission (card 20 — display only)

| # | Name | Viz | SQL tag |
|---|------|-----|---------|
| 20 | IB Commission estimate | Number | `-- CARD 20` |

Edit `$8` per lot in SQL to match your IB rebate rate.

## G10 guardrail

- Label dashboard footer: **"Volume KPI — reporting only, not a trading objective"**
- Do not add alerts that trigger trades from pace metrics
- `BELOW_TARGET_PACE` is informational — show catch-up pace, never auto-size up

## Empty data tips

| Symptom | Cause | Fix |
|---------|-------|-----|
| Volume cards empty | No closed trades in `journal.json` | Close a signal via `/close_signal`, sync |
| Spread cards empty | No spread events | Run `/seed_signal`, sync |
| Activity empty | No gate decisions | Run `/check_signal`, sync |

## Phase 6 (optional)

If Metabase is enough for internal BI, **skip Vercel**.

See [reporting-roadmap.md](reporting-roadmap.md#phase-6--vercel-optional).
