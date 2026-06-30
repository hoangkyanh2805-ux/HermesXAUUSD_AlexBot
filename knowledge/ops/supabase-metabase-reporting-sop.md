# SOP OPS — Supabase + Metabase Reporting Stack

> **Reusable knowledge asset** for Hermes-style desks and similar projects.  
> **Version:** 1.0 | **Source case:** Hermes XAUUSD IB Desk (2026-06)  
> **Audience:** Operator, dev, AI agent

---

## 1. Purpose

Standard workflow to connect:

```text
Local desk (JSON / pipeline)
    → Supabase (PostgreSQL SoT)
    → Metabase (internal BI)
```

**Out of scope:** Vercel/custom portal (Phase 6 optional), real broker API.

**Guardrail:** Volume KPI and BI metrics are **display-only** — never trading triggers (G10).

---

## 2. Phase map (reporting)

| Phase | Name | Deliverable | Owner |
|-------|------|-------------|-------|
| **E** | Supabase sync | `schema.sql`, `sync_to_supabase.py`, `supabase/.env` | Dev |
| **4** | Metabase connect | PostgreSQL DB in Metabase, schema synced | Ops |
| **5** | BI dashboard | SQL cards + dashboard collection | Ops |
| **6** | Vercel *(optional)* | Custom portal beyond Metabase | Defer |

---

## 3. Prerequisites checklist

- [ ] Supabase project created (note `<project-ref>`)
- [ ] `supabase/schema.sql` executed in SQL Editor
- [ ] `supabase/.env` created (not committed): `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`
- [ ] At least one successful `python scripts/sync_to_supabase.py`
- [ ] Java 21+ (if Metabase JAR local) or Docker (optional)
- [ ] Database password known or reset via Connect modal

---

## 4. Credentials — what to use where

| Secret | Where to get | Used for | Never use for |
|--------|--------------|----------|---------------|
| **Database password** | Supabase → Connect → Reset password | Metabase PostgreSQL, `psql` | REST sync, frontend |
| **service_role / Secret** (`sb_secret_...`) | Settings → **API Keys** (Secret tab) | `sync_to_supabase.py`, server | Metabase DB form |
| **publishable** (`sb_publishable_...`) | Settings → **API Keys** (Publishable) | Client apps (RLS) | Metabase, sync script |
| **SUPABASE_URL** | Integrations → **Data API** or General | PostgREST sync | Metabase host field |

### Metabase connection fields (Session pooler — default for IPv4)

| Field | Pattern |
|-------|---------|
| Host | `aws-0-<region>.pooler.supabase.com` *(from Connect → Session pooler)* |
| Port | `5432` |
| Database | `postgres` |
| Username | `postgres.<project-ref>` |
| Password | Database password |
| SSL | ON, mode **`require`** |

### Do NOT use (common failures)

| Wrong | Why |
|-------|-----|
| Host `db.<ref>.supabase.co` | IPv6-only on free tier → fails on many Windows/IPv4 networks |
| Username `postgres` | Pooler requires `postgres.<ref>` |
| API keys as DB password | Auth fails with misleading "password incorrect" |
| SSL `verify-full` without PEM file | Connection fails |
| `SUPABASE_URL` as Metabase host | REST API ≠ PostgreSQL host |

---

## 5. Workflow A — Supabase setup (Phase E)

### A1. Run schema

1. Supabase Dashboard → **SQL Editor**
2. Paste full `supabase/schema.sql` → **Run**
3. Verify tables: `signals`, `trades`, `activity_logs`, `risk_audit`, `spread_audit`
4. Verify views: `volume_daily`, `volume_weekly`, `volume_monthly`

### A2. Configure sync credentials

```powershell
copy supabase\env.example supabase\.env
```

```env
SUPABASE_URL=https://<project-ref>.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<sb_secret from API Keys>
# Optional:
# SYNC_TO_SUPABASE=true
```

### A3. Sync local data

```powershell
python scripts/sync_to_supabase.py --dry-run
python scripts/sync_to_supabase.py
```

**Mapping:**

| Local | Supabase |
|-------|----------|
| `data/signals.json` | `signals` |
| `data/journal.json` | `trades` |
| `data/spread_audit.jsonl` | `spread_audit` |
| `data/signal_audit.json` | `activity_logs` |
| `data/risk_state.json` | `risk_audit` |

### A4. Verify

Supabase **Table Editor** → `signals` ≥ 1 row (after desk has valid signals).

---

## 6. Workflow B — Metabase local (Phase 4)

### B1. Choose runtime

| Option | When |
|--------|------|
| **JAR + Java 21** | No Docker; Windows MVP |
| **Docker** | `docker run -p 3000:3000 metabase/metabase` |
| **Metabase Cloud** | No local ops |

**Hermes desk default:** JAR via `scripts/start_metabase.ps1`

**Windows notes:**

- Metabase latest requires **Java 21+**
- JAR path must **not contain spaces** → use `C:\hermes-metabase\` (script copies JAR there)
- Open: `http://localhost:3000`

### B2. Setup wizard (first run)

1. Create Metabase admin (email + password — separate from Supabase)
2. Skip sample DB or keep for learning
3. Add PostgreSQL — use **Session pooler** credentials (Section 4)

### B3. Add / edit database (Admin → Databases)

1. **Connect** on Supabase → **Connection String** → **Session pooler**
2. Copy Host, Username, Port
3. Reset database password if needed (link in Connect modal)
4. Metabase form: SSL **ON**, mode **`require`**, no certificate file
5. **Save** → wait **Connected** + **Syncing tables...**

### B4. Verify Phase 4

- [ ] Status: **Connected** (green)
- [ ] Browse → `signals`, `volume_monthly`, …
- [ ] SQL: `select count(*) from signals;`

If `signals = 0` → run Workflow A3 sync.

---

## 7. Workflow C — BI dashboard (Phase 5)

1. Create collection: `Hermes XAUUSD IB Desk` (or project name)
2. **+ New → SQL query** → database = Supabase
3. Paste blocks from `metabase/cards.sql` (`-- CARD 01` … `20`)
4. Pick visualization per `docs/metabase-phase5-dashboard.md`
5. **+ New → Dashboard** → add saved questions
6. Footer note: *Volume KPI — reporting only (G10)*

**Sync cadence:** Metabase reads Supabase only. Re-run `sync_to_supabase.py` after desk pipeline; optional `SYNC_TO_SUPABASE=true`.

---

## 8. Troubleshooting runbook

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Metabase can't resolve host | Wrong host / IPv6 | Session pooler host from Connect |
| `password authentication failed` | Wrong password OR wrong username | `postgres.<ref>` + reset DB password |
| Metabase says password wrong, password is correct | Username still `postgres` | Use `postgres.<project-ref>` |
| SSL / certificate error | `verify-full` without PEM | SSL mode `require`, no cert file |
| Connection refused / timeout | Direct `db.*` on IPv4 | Session pooler |
| Tables empty in Metabase | No sync | `python scripts/sync_to_supabase.py` |
| HTTP 400 `PGRST102` keys must match | Inconsistent JSON keys in batch upsert | Fixed via `_normalize_batch` in `supabase_sync.py` |
| HTTP 401 on sync | Wrong or rotated secret key | Update `SUPABASE_SERVICE_ROLE_KEY` in `.env` |
| Metabase JAR crash on Windows | Java 17 or path with spaces | Java 21 + `C:\hermes-metabase\` |
| Can't find Database in Settings | Supabase UI changed | Connect → Session pooler → Reset password |

### Diagnostic command (dev)

```powershell
python -c "import psycopg2; c=psycopg2.connect(host='aws-0-REGION.pooler.supabase.com',port=5432,dbname='postgres',user='postgres.PROJECT_REF',password='***',sslmode='require'); print('OK')"
```

---

## 9. Security OPS

- [ ] `supabase/.env`, `telegram/.env` in `.gitignore` — never commit
- [ ] Rotate database password if exposed in chat/logs
- [ ] Rotate `service_role` if exposed
- [ ] Metabase: private workspace; no public dashboards without auth
- [ ] Production: read-only DB user for Metabase (optional hardening)

---

## 10. Project file index (Hermes XAUUSD)

| Path | Role |
|------|------|
| `supabase/schema.sql` | DB schema + views |
| `supabase/env.example` | Credential template |
| `src/supabase_sync.py` | Sync logic |
| `scripts/sync_to_supabase.py` | CLI sync |
| `scripts/start_metabase.ps1` | Local Metabase JAR |
| `metabase/cards.sql` | Phase 5 SQL |
| `docs/metabase-phase4-connect.md` | UI walkthrough |
| `docs/metabase-phase5-dashboard.md` | Card layout |
| `docs/reporting-roadmap.md` | Phase 2–6 map |

---

## 11. Agent task template (copy for new projects)

```text
TASK: Deploy reporting stack (Supabase + Metabase) for <PROJECT>.

1. Run supabase/schema.sql on project <REF>
2. Create supabase/.env (service_role) — do not commit
3. Run sync script; verify signals ≥ 1
4. Start Metabase local (Java 21 JAR or Docker)
5. Connect via Session pooler (NOT db.<ref> direct)
   - Host: aws-0-<region>.pooler.supabase.com
   - User: postgres.<ref>
   - SSL: require
6. Verify Connected + Browse tables
7. Build dashboard from metabase/cards.sql (adapt SQL)
8. Document project-ref and pooler host in project README

CONSTRAINTS: G10 volume display-only. No secrets in git.
```

---

## 12. Lessons learned (Hermes XAUUSD case study)

1. **Supabase free tier direct DB = IPv6** → Metabase on Windows needs **Session pooler**.
2. **"Password incorrect"** often means **wrong username** (`postgres` vs `postgres.ref`).
3. **Database password** location moved to **Connect modal** (not Settings → Database).
4. **Metabase ≠ `index.html`** — local HTML dashboard is separate from BI.
5. **Docker optional** — JAR + Java 21 works when Docker not installed.
6. **Sync and BI are separate steps** — connect can succeed while tables are empty.

---

## Related

- [reporting-roadmap.md](../../docs/reporting-roadmap.md)
- [supabase-metabase-setup.md](../../docs/supabase-metabase-setup.md)
- Knowledge §3: `knowledge/distilled/hermes-xauusd-risk-first-volume-desk-upgrade.md`
