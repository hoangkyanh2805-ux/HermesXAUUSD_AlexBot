# Hermes XAUUSD IB Desk — Supabase + Metabase Setup

> Phase E: đồng bộ `data/*.json` → Supabase → Metabase dashboards  
> Volume KPI **chỉ báo cáo** — không trigger trade (G10)

---

## Tổng quan

```text
Hermes / MCP pipeline
    → data/*.json (local SoT MVP)
    → scripts/sync_to_supabase.py
    → Supabase (PostgreSQL)
    → Metabase (visual dashboards)
```

---

## Bước 1 — Tạo Supabase project

1. [supabase.com](https://supabase.com) → **New project**
2. Lưu **Database password**
3. Đợi project **Active**

---

## Bước 2 — Chạy schema SQL

1. Supabase Dashboard → **SQL Editor** → **New query**
2. Copy toàn bộ [`supabase/schema.sql`](../supabase/schema.sql)
3. **Run**

Tạo các bảng: `signals`, `trades`, `activity_logs`, `risk_audit`, `spread_audit`  
Views: `volume_daily`, `volume_weekly`, `volume_monthly`

---

## Bước 3 — Cấu hình credentials (local)

```powershell
cd hermes-xauusd-ib-desk
copy supabase\env.example supabase\.env
```

Điền trong `supabase/.env`:

```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...
```

Lấy từ: **Project Settings → API**  
Dùng **service_role** (server only) — **không** commit, **không** đưa vào frontend.

---

## Bước 4 — Sync dữ liệu

### Dry run (không gọi network)

```powershell
python scripts/sync_to_supabase.py --dry-run
```

### Xem payloads

```powershell
python scripts/sync_to_supabase.py --payloads
```

### Sync thật

```powershell
python scripts/sync_to_supabase.py
```

### Auto-sync sau mỗi lệnh desk

Thêm vào `supabase/.env`:

```env
SYNC_TO_SUPABASE=true
```

Hoặc set biến môi trường hệ thống.

---

## Bước 5 — Mapping local → Supabase

| Local file | Supabase table |
|------------|----------------|
| `data/signals.json` | `signals` |
| `data/journal.json` | `trades` |
| `data/spread_audit.jsonl` | `spread_audit` (aggregated) |
| `data/signal_audit.json` | `activity_logs` |
| `data/risk_state.json` | `risk_audit` (snapshot) |
| — | `volume_*` views (từ `trades`) |

Signal không có SL (`sig-reject-demo`) được **bỏ qua** khi sync `signals`.

---

## Bước 6 — Kết nối Metabase

### Cài Metabase

- [metabase.com](https://www.metabase.com) cloud, hoặc
- Docker local: `docker run -d -p 3000:3000 metabase/metabase`

### Add database

1. Metabase → **Admin** → **Databases** → **Add database**
2. Type: **PostgreSQL**
3. Điền từ Supabase **Project Settings → Database**:

| Field | Giá trị |
|-------|---------|
| Host | `db.<project-ref>.supabase.co` |
| Port | `5432` |
| Database | `postgres` |
| Username | `postgres` |
| Password | Database password |
| SSL | **ON** |

4. **Save** → đợi sync schema

### Hoặc dùng connection string

```
postgresql://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres
```

---

## Bước 7 — Tạo Metabase cards (20 cards)

Tham chiếu knowledge asset **§3.8**:

| # | Card | Nguồn SQL |
|---|------|-----------|
| 1 | Monthly Volume Progress Gauge | `volume_monthly` |
| 2 | Daily Lots Bar Chart | `volume_daily` |
| 3 | Weekly Lots Trend | `volume_weekly` |
| 4 | Monthly vs 200 Target | `volume_monthly` |
| 5 | Remaining Lots | `volume_monthly.remaining_lots` |
| 6 | Required Daily Pace | `volume_monthly.required_daily_pace` |
| 7 | Projected Month-End | `volume_monthly.projected_month_end_lots` |
| 8 | Volume by Session | `trades` GROUP BY session |
| 9 | Volume by Client Group | `trades` GROUP BY client_group |
| 10 | Volume by Risk Tier | `trades` GROUP BY risk_tier |
| 11 | Risk vs Volume | join `risk_audit` + `trades` |
| 12 | Drawdown vs Volume | `risk_audit` time series |
| 13 | Spread Warning Count | `spread_audit` WHERE status != NORMAL |
| 14 | Avg Spread by Session | `spread_audit` + `signals` |
| 15 | Signals Approved/Waiting/Rejected | `activity_logs` |
| 16 | Win/Loss/BE | `trades` |
| 17 | TP/SL hit rates | `activity_logs` event types |
| 18 | Correlation risk outcomes | `signals.correlation_risk_tag` |
| 19 | Blocked trades by reason | `risk_audit.action_taken` |
| 20 | IB Commission estimate | custom SQL × rate (display only) |

---

## Bước 8 — MCP tool (Hermes)

Sau khi reload MCP:

```text
sync_supabase dry_run=true
sync_supabase
```

---

## Quy tắc quan trọng

- **G10:** KPI 200 lots/tháng chỉ hiển thị trên Metabase
- Sync **không** tạo signal mới
- Sync **không** override Signal Gate / Risk Manager
- `service_role` key chỉ trên server local / Hermes gateway

---

## Xử lý lỗi

| Lỗi | Cách sửa |
|-----|----------|
| Missing SUPABASE_URL | Tạo `supabase/.env` |
| HTTP 401 | Sai service_role key |
| HTTP 404 | Chưa chạy `schema.sql` |
| FK violation on trades | Sync `signals` trước (script đã đúng thứ tự) |
| RLS blocked | Dùng service_role hoặc tắt RLS cho MVP |

---

## Liên quan

- [Knowledge asset §3](../knowledge/distilled/hermes-xauusd-risk-first-volume-desk-upgrade.vi.md)
- [supabase/schema.sql](../supabase/schema.sql)
- [Guardrails G10](../docs/guardrails.md)
