# SOP OPS — Supabase + Metabase (Báo cáo & Audit)

> **Knowledge tái sử dụng** cho desk Hermes và dự án tương tự.  
> **Phiên bản:** 1.0 | **Case:** Hermes XAUUSD IB Desk (2026-06)  
> **Đối tượng:** Operator, dev, AI agent

---

## 1. Mục đích

Workflow chuẩn kết nối:

```text
Desk local (JSON / pipeline)
    → Supabase (PostgreSQL — SoT báo cáo)
    → Metabase (BI nội bộ)
```

**Ngoài scope:** Vercel/portal custom (Phase 6 tùy chọn).

**Guardrail G10:** KPI volume chỉ hiển thị — không trigger trade.

---

## 2. Bản đồ phase

| Phase | Tên | Deliverable |
|-------|-----|-------------|
| **E** | Sync Supabase | `schema.sql`, `sync_to_supabase.py`, `.env` |
| **4** | Metabase connect | DB PostgreSQL + sync schema |
| **5** | Dashboard BI | SQL cards + collection |
| **6** | Vercel *(optional)* | Portal custom |

---

## 3. Checklist trước khi bắt đầu

- [ ] Supabase project + `<project-ref>`
- [ ] Chạy `supabase/schema.sql`
- [ ] `supabase/.env` (không commit)
- [ ] `python scripts/sync_to_supabase.py` thành công
- [ ] Java 21+ (Metabase JAR) hoặc Docker
- [ ] Biết / reset Database password

---

## 4. Credentials — dùng đúng chỗ

| Secret | Lấy ở đâu | Dùng cho | Không dùng cho |
|--------|-----------|----------|----------------|
| **Database password** | Connect → Reset password | Metabase, psql | Sync script, frontend |
| **service_role** (`sb_secret_...`) | API Keys | `sync_to_supabase.py` | Form Metabase |
| **publishable** | API Keys | Client RLS | Metabase, sync |
| **SUPABASE_URL** | API | PostgREST sync | Host Metabase |

### Metabase — Session pooler (IPv4, khuyên dùng)

| Field | Giá trị |
|-------|---------|
| Host | `aws-0-<region>.pooler.supabase.com` |
| Port | `5432` |
| Database | `postgres` |
| Username | `postgres.<project-ref>` |
| Password | Database password |
| SSL | ON, **`require`** |

### Không dùng (lỗi thường gặp)

| Sai | Hậu quả |
|-----|---------|
| `db.<ref>.supabase.co` | IPv6 — Windows fail |
| Username `postgres` | Pooler báo password sai |
| API key làm DB password | Auth fail |
| SSL `verify-full` không có PEM | Fail |
| `SUPABASE_URL` làm host Metabase | Sai protocol |

---

## 5. Workflow A — Supabase (Phase E)

### A1. Schema

SQL Editor → paste `supabase/schema.sql` → Run.

### A2. Credentials sync

```powershell
copy supabase\env.example supabase\.env
```

```env
SUPABASE_URL=https://<project-ref>.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<sb_secret>
```

### A3. Sync

```powershell
python scripts/sync_to_supabase.py --dry-run
python scripts/sync_to_supabase.py
```

### A4. Verify

Table Editor → `signals` ≥ 1 row.

---

## 6. Workflow B — Metabase (Phase 4)

### B1. Chạy Metabase local

```powershell
powershell -ExecutionPolicy Bypass -File scripts\start_metabase.ps1
```

- Cần **Java 21+**
- JAR tại `C:\hermes-metabase\` (tránh path có khoảng trắng)
- Mở **http://localhost:3000**

### B2. Wizard lần đầu

Tạo admin Metabase (khác password Supabase).

### B3. Add database

1. Supabase → **Connect** → **Session pooler** (port 5432)
2. Copy Host + Username (`postgres.<ref>`)
3. Reset password nếu cần (link trong Connect — **không** có menu Database trong Settings mới)
4. Metabase: SSL **ON**, `require`, không file cert
5. **Save** → **Connected** + Syncing tables

### B4. Verify

```sql
select count(*) from signals;
```

### Lưu ý

- **`index.html`** = dashboard local — **không phải** Metabase
- Metabase = **localhost:3000**

---

## 7. Workflow C — Dashboard (Phase 5)

1. Collection: `Hermes XAUUSD IB Desk`
2. Paste SQL từ `metabase/cards.sql`
3. Dashboard + cards theo `docs/metabase-phase5-dashboard.md`
4. Ghi chú G10 trên dashboard

**Refresh data:** `python scripts/sync_to_supabase.py` sau mỗi phiên desk.

---

## 8. Troubleshooting

| Triệu chứng | Nguyên nhân | Sửa |
|-------------|-------------|-----|
| Password sai (password đúng) | Username `postgres` | `postgres.<ref>` |
| Fail ngay | Host `db.*` IPv6 | Session pooler |
| SSL error | verify-full | `require` |
| Bảng trống | Chưa sync | `sync_to_supabase.py` |
| JAR crash | Java 17 / path space | Java 21 + `C:\hermes-metabase` |
| Không thấy Reset password | UI mới | Connect → Session pooler |

---

## 9. Bảo mật OPS

- Không commit `.env`
- Rotate password nếu lộ chat/log
- Metabase private — không public
- Production: user DB read-only cho Metabase (tùy chọn)

---

## 10. File trong repo

| File | Vai trò |
|------|---------|
| `knowledge/ops/supabase-metabase-reporting-sop.md` | SOP EN |
| `knowledge/ops/supabase-metabase-reporting-sop.vi.md` | SOP VI (file này) |
| `supabase/schema.sql` | Schema |
| `scripts/sync_to_supabase.py` | Sync CLI |
| `scripts/start_metabase.ps1` | Metabase local |
| `metabase/cards.sql` | SQL cards |

---

## 11. Task template (agent / dự án mới)

```text
TASK: Triển khai reporting Supabase + Metabase cho <PROJECT>.

1. Chạy schema.sql trên Supabase <REF>
2. Tạo supabase/.env (service_role) — không commit
3. Sync + verify signals ≥ 1
4. Metabase local (Java 21 JAR)
5. Connect Session pooler — KHÔNG dùng db.<ref> direct
6. Verify Connected + Browse
7. Build cards từ metabase/cards.sql
8. Ghi pooler host + ref vào README dự án

RÀNG BUỘC: G10. Không secrets trong git.
```

---

## 12. Bài học (case Hermes XAUUSD)

1. Free tier **direct DB = IPv6** → Windows cần **Session pooler**
2. **"Password sai"** thường do **username** thiếu `.project-ref`
3. Reset password ở **Connect**, không phải Settings → Database
4. Metabase ≠ HTML dashboard local
5. Connect OK ≠ có data — cần sync riêng

---

## Liên quan

- [reporting-roadmap.md](../../docs/reporting-roadmap.md)
- [metabase-phase4-connect.md](../../docs/metabase-phase4-connect.md)
- [metabase-phase5-dashboard.md](../../docs/metabase-phase5-dashboard.md)
