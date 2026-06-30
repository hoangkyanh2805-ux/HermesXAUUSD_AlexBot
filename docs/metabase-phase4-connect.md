# Phase 4 — Connect Metabase to Supabase (UI walkthrough)

> Internal BI only. Metabase đọc Supabase — **không** đọc `data/*.json` local.  
> Project Supabase: `tikouskusgdygktslmzj`

---

## Trước khi mở Metabase

### Bước 0.1 — Sync dữ liệu lên Supabase

```powershell
cd "g:\Other computers\My Computer\Project\hermes-xauusd-ib-desk"
python scripts/sync_to_supabase.py
```

Kỳ vọng `"ok": true`. Kiểm tra nhanh trên Supabase:

1. [Supabase Table Editor](https://supabase.com/dashboard/project/tikouskusgdygktslmzj/editor)
2. Mở bảng `signals` → thấy ≥ 1 row

### Bước 0.2 — Chuẩn bị Database password

Metabase cần **Database password** (khác với `service_role` key):

1. Supabase → **Project Settings** (icon bánh răng) → **Database**
2. Copy **Database password** hoặc **Reset database password** nếu quên
3. Lưu tạm Notepad — dùng ở bước 3.5

---

## Phần A — Tạo Metabase (lần đầu)

### Bước 1 — Chọn cách chạy Metabase

**Cách 1 — Metabase Cloud (khuyên dùng, không cần Docker)**

1. Mở [metabase.com/start](https://www.metabase.com/start)
2. **Sign up** (Google hoặc email)
3. Tạo **workspace** (tên ví dụ: `Hermes Growth`)

**Cách 2 — Docker local**

```powershell
docker run -d -p 3000:3000 --name metabase metabase/metabase
```

Mở trình duyệt: `http://localhost:3000`

### Bước 2 — Setup wizard (chỉ lần đầu)

Metabase hiện màn hình **Welcome**. Điền lần lượt:

| Màn hình | Điền gì |
|----------|---------|
| **Language** | English hoặc tiếng bạn quen |
| **Your name** | Alex (hoặc tên operator) |
| **Email** | Email đăng nhập |
| **Password** | Mật khẩu Metabase (khác Supabase) |
| **Add your data** | Chọn **PostgreSQL** |
| **Usage data** | Tuỳ chọn — có thể tắt |

> Nếu wizard bỏ qua bước database → làm **Phần B** bên dưới.

---

## Phần B — Kết nối Supabase PostgreSQL

### Bước 3 — Mở màn hình Add database

**Nếu đang trong wizard:** chọn **PostgreSQL** → **Next**

**Nếu Metabase đã setup xong:**

1. Click **⚙️** (góc trên phải) → **Admin settings**
2. Sidebar trái → **Databases**
3. Click nút **Add database** (góc phải)

### Bước 4 — Điền form PostgreSQL

> **Quan trọng (Windows):** `db.tikouskusgdygktslmzj.supabase.co` chỉ có **IPv6** — Metabase trên mạng IPv4 sẽ **fail**.  
> Dùng **Session pooler** từ Supabase Dashboard → **Connect**.

**Lấy thông tin pooler:**

1. [Supabase Dashboard](https://supabase.com/dashboard/project/tikouskusgdygktslmzj) → nút **Connect**
2. **Connection string** → chọn **Session pooler** (port `5432`)
3. Copy Host + Username từ đó

| Field trên Metabase | Giá trị |
|---------------------|---------|
| **Display name** | `Hermes XAUUSD Supabase` |
| **Host** | `aws-0-<region>.pooler.supabase.com` *(từ Connect → Session pooler)* |
| **Port** | `5432` |
| **Database name** | `postgres` |
| **Username** | `postgres.tikouskusgdygktslmzj` ← **không** chỉ `postgres` |
| **Password** | Database password (Bước 0.2) |

**Không dùng:**

- `db.tikouskusgdygktslmzj.supabase.co` — IPv6-only, Windows thường fail
- `SUPABASE_URL` — REST API, không phải DB host
- `service_role` / `sb_secret_...` — API key, không phải DB password

### Bước 5 — Bật SSL (bắt buộc với Supabase)

Cuộn xuống phần **SSL** hoặc **Show advanced options**:

| Tuỳ chọn Metabase | Chọn |
|-------------------|------|
| **Use a secure connection (SSL)** | ✅ Bật |
| **SSL Mode** | `require` hoặc **Require SSL** |

Nếu có ô **Use an SSL certificate** — để trống (Supabase dùng cert mặc định).

### Bước 6 — Các tuỳ chọn khác (để mặc định)

| Field | Khuyên dùng |
|-------|-------------|
| **Schemas** | All (để trống = tất cả) |
| **Routines** | Off |
| **Connection pooling** | Off (MVP) |
| **Sync schedule** | Hourly (mặc định OK) |

### Bước 7 — Test và Save

1. Click **Test connection** (nếu có)
   - ✅ **Successful** → tiếp
   - ❌ Lỗi → xem [Xử lý lỗi](#xử-lý-lỗi-thường-gặp) cuối file
2. Click **Save**
3. Metabase bắt đầu **sync schema** (30 giây – 2 phút)

---

## Phần C — Xác nhận kết nối thành công

### Bước 8 — Browse data

1. Thoát Admin → click **🏠 Home** hoặc logo Metabase
2. Sidebar trái → **Browse** → **Databases**
3. Click **Hermes XAUUSD Supabase**
4. Mở schema **public**

Phải thấy:

| Tên | Loại |
|-----|------|
| `signals` | Table |
| `trades` | Table |
| `activity_logs` | Table |
| `risk_audit` | Table |
| `spread_audit` | Table |
| `volume_daily` | View |
| `volume_weekly` | View |
| `volume_monthly` | View |

**Không thấy views?** → Supabase SQL Editor → chạy lại `supabase/schema.sql`

### Bước 9 — Xem dữ liệu mẫu

1. Click bảng **`signals`**
2. Metabase hiện grid preview
3. Kiểm tra có `sig-sell-4088`, `sig-001`, v.v.

Lặp lại với `spread_audit`, `activity_logs` nếu đã sync.

### Bước 10 — Smoke test SQL

1. Sidebar → **+ New** → **SQL query**
2. Database dropdown (góc trên) → chọn **Hermes XAUUSD Supabase**
3. Paste:

```sql
select count(*) as signal_count from signals;
select count(*) as trade_count from trades;
select * from volume_monthly limit 1;
```

4. Click **Run** (hoặc Ctrl+Enter)
5. Kỳ vọng:
   - `signal_count` ≥ 1
   - `trade_count` có thể = 0 (chưa close signal trong journal)
   - `volume_monthly` có row với `target_lots = 200`

6. **Save** → đặt tên: `Smoke test — signal count`

---

## Phần D — Chuẩn bị cho Phase 5

### Bước 11 — Tạo Collection

1. Sidebar → **Collections** (hoặc **Browse** → **Collections**)
2. Click **+** → **Collection**
3. Tên: `Hermes XAUUSD IB Desk`
4. Description: `Internal BI — volume, risk, spread, signal audit (G10)`
5. **Create**

### Bước 12 — Lưu smoke test vào collection

1. Mở question vừa save (Bước 10)
2. Click **⋯** → **Move to collection** → chọn **Hermes XAUUSD IB Desk**

### Bước 13 — Tạo dashboard trống (tuỳ chọn, tiện cho Phase 5)

1. **+ New** → **Dashboard**
2. Tên: `Hermes XAUUSD IB Desk`
3. Collection: **Hermes XAUUSD IB Desk**
4. **Create** → để trống, Phase 5 sẽ thêm cards

---

## Phần E — Bảo mật (khuyên dùng)

### Bước 14 — Không public Metabase

- Metabase Cloud: giữ workspace **private**, chỉ invite email operator
- Không share link dashboard ra ngoài desk

### Bước 15 — Phân quyền (Metabase Cloud Pro / self-hosted)

1. **Admin** → **People** → Invite Alex
2. Group **Administrators** hoặc tạo group **Desk Operators**
3. Collection **Hermes XAUUSD IB Desk** → chỉ group operators xem được

---

## Sync sau này

Metabase **không tự** lấy data từ máy local. Mỗi khi desk chạy pipeline:

```powershell
python scripts/sync_to_supabase.py
```

Hoặc bật auto: `SYNC_TO_SUPABASE=true` trong `supabase/.env`

Metabase refresh theo **sync schedule** (hourly) hoặc **Admin → Databases → Sync database schema now**.

---

## Xử lý lỗi thường gặp

| Lỗi Metabase | Nguyên nhân | Cách sửa |
|--------------|-------------|----------|
| `Connection refused` / fail ngay | Dùng nhầm `db.*.supabase.co` (IPv6) | Dùng **Session pooler** + user `postgres.tikouskusgdygktslmzj` |
| `password authentication failed` | Sai password | Reset trong Supabase → Database → Reset password |
| `SSL required` | Chưa bật SSL | Bật **Require SSL** |
| `relation "signals" does not exist` | Chưa chạy schema | Chạy `supabase/schema.sql` trên Supabase |
| Tables có nhưng 0 rows | Chưa sync | `python scripts/sync_to_supabase.py` |
| `FATAL: no pg_hba.conf entry` | IP bị chặn | Supabase free thường OK; thử Metabase Cloud thay Docker |

---

## Checklist Phase 4 hoàn tất

- [ ] Metabase account / instance chạy
- [ ] Database `Hermes XAUUSD Supabase` — Test connection OK
- [ ] 5 tables + 3 views hiện trong Browse
- [ ] `signals` có ≥ 1 row
- [ ] SQL smoke test chạy OK
- [ ] Collection `Hermes XAUUSD IB Desk` đã tạo

**Tiếp theo:** [Phase 5 — Build dashboard cards](metabase-phase5-dashboard.md) + SQL từ [`metabase/cards.sql`](../metabase/cards.sql)

---

## Liên quan

- [reporting-roadmap.md](reporting-roadmap.md)
- [supabase-metabase-setup.md](supabase-metabase-setup.md)
