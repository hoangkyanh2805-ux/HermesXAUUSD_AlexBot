# Nâng cấp Risk-First Volume Desk — Tài sản tri thức

> **Loại nguồn:** Brief nâng cấp hệ thống / kinh doanh  
> **Tiêu đề nguồn:** Risk-First Volume Desk Upgrade for Hermes XAUUSD IB System  
> **Dự án:** Hermes XAUUSD IB Trading Desk  
> **Chưng cất:** 2026-06-29 (v2 — Reporting & Audit §3)  
> **Skill:** `knowledge-asset-factory`  
> **Bản tiếng Anh:** [hermes-xauusd-risk-first-volume-desk-upgrade.md](./hermes-xauusd-risk-first-volume-desk-upgrade.md)  
> **Tài sản gốc:** [hermes-xauusd-ib-desk-knowledge-asset.md](./hermes-xauusd-ib-desk-knowledge-asset.md)

---

## 1. Tóm tắt nguồn

### Brief nâng cấp đề xuất gì

Nâng cấp Hermes XAUUSD IB Desk từ **luồng signal cơ bản** thành **Risk-First Volume Desk** — hệ điều hành IB chuyên nghiệp: **bảo vệ equity khách trước**, theo dõi volume kinh doanh sau, và **không bao giờ** coi volume hoa hồng là mục tiêu vào lệnh.

### Bối cảnh nguồn

| Hạng mục | Chi tiết |
|----------|----------|
| **Vai trò operator** | Forex IB tập trung XAUUSD / Vàng |
| **Kênh** | Telegram DM + Signal Group |
| **Kiến trúc tham chiếu** | Flow trading desk video Hermes Agent, thích ứng cho IB signal |
| **KPI kinh doanh** | ~200 lots/tháng — **chỉ theo dõi**, không trigger trade |
| **Ẩn dụ cốt lõi** | Equity = bình xăng; risk = đồng hồ xăng; DXY/US10Y = thời tiết; multi-entry = chia chặng; volume = quãng đường đi |

### Kho nguồn

| Đầu vào | Loại | Độ tin cậy |
|---------|------|------------|
| Brief nâng cấp (tài liệu này) | Spec chính | Cao |
| Repo MVP hiện tại (Phase C) | Codebase đã xác minh | Cao |
| Mapping flow video Hermes | Knowledge asset trước | Cao |
| Ngưỡng correlation DXY/US10Y | Ví dụ trong brief | Trung bình — cần hiệu chỉnh |
| Ngưỡng spread (30 pts) | Ví dụ trong brief | Trung bình — repo hiện dùng 35 pts |
| KPI 200 lots/tháng | Mục tiêu kinh doanh | Cao — operator xác nhận |

### Brief KHÔNG yêu cầu

- API thực thi broker thật
- Xử lý mật khẩu khách
- CRM đầy đủ, Content Engine, X Funnel, BioLink
- Cam kết lợi nhuận hoặc overtrade vì hoa hồng
- Thay thế kiến trúc desk 8 lớp Hermes

---

## 2. Ý tưởng cốt lõi

**Nâng cấp desk từ “người đăng signal” thành “operator IB ưu tiên rủi ro”.**

Hệ thống giúp Alex:

1. Validate signal XAUUSD với bối cảnh thị trường + correlation
2. Tính size từ equity và risk — **không** từ mục tiêu volume
3. Chặn hoặc tạm dừng khi vượt floating risk, spread, tin tức, hoặc daily loss limit
4. Hỗ trợ multi-entry **chỉ khi** tổng risk không đổi
5. Audit spread lúc seed, entry, và close
6. Theo dõi volume tích lũy (ngày/tuần/tháng) hướng 200 lots/tháng **chỉ trên dashboard**
7. Đưa spread, correlation, session, hành vi risk vào AI Brain để vận hành bền vững

```text
Chất lượng signal + bảo vệ equity  →  mục tiêu tối ưu chính
Volume bền vững + hoa hồng IB       →  kết quả kinh doanh phụ (theo dõi, không ép)
```

---

## 3. Reporting & Audit — Yêu cầu (Supabase + Metabase)

### Mục đích

Thiết kế **lớp báo cáo & audit** giúp IB operator theo dõi trực quan:

1. Volume giao dịch tích lũy
2. Tiến độ hướng mục tiêu **200 lots/tháng**
3. Risk exposure
4. Chất lượng spread / slippage
5. Chất lượng signal
6. Volume có **an toàn** hay đến từ **overtrade**

**Stack đích:** **Supabase** (SoT) + **Metabase** (visual dashboard)

### Quy tắc quan trọng (G10 mở rộng)

Mục tiêu volume là **KPI báo cáo only** — **không** ép trade để đạt 200 lots/tháng.

**200 lots/tháng không bao giờ override:**

| Guard | Module hiện tại |
|-------|-----------------|
| Signal Gate | `src/signal_gate.py` |
| Risk Manager | `src/lot_calculator.py` + `src/safety_locks.py` |
| Spread Guard | `src/spread_audit.py` + spread lock |
| News Guard | `signal_gate` + `safety_locks` |
| Daily Loss Lock | `src/safety_locks.py` |
| Floating Risk Lock | `src/safety_locks.py` |

```text
Dashboard volume KPI  →  MONITOR ONLY
Trading pipeline      →  RISK-FIRST ALWAYS
```

---

### 3.1 Volume Progress Dashboard

Hiển thị volume tích lũy:

| Metric | Mô tả |
|--------|--------|
| Hôm nay | `daily_lots` |
| Tuần này | `weekly_lots` |
| Tháng này | `monthly_lots` |
| MTD progress | `monthly / 200` |
| Remaining lots | `200 - monthly` |
| Required daily pace | `remaining / trading_days_remaining` |
| Actual daily pace | `monthly / trading_days_passed` |
| Projected month-end | `actual_pace × total_trading_days_in_month` |

**Ví dụ:**

```text
Monthly target:           200 lots
Current month volume:     68.5 lots
Progress:                 34.25%
Remaining:                131.5 lots
Trading days passed:      8
Trading days remaining:   14
Required daily pace:      9.39 lots/day
Current daily pace:       8.56 lots/day
Projected month-end:      188.3 lots
```

**Phase 1 (hiện tại):** `src/volume_tracker.py` + `dashboard/ib-signals/`  
**Phase 3–5:** SQL view `volume_monthly` + Metabase gauge

---

### 3.2 Volume Breakdown

Phân tích volume theo:

- Ngày / tuần / tháng
- `signal_id`
- Client group / risk tier
- Session: Asia / London / NY
- Direction: Buy / Sell
- Setup type
- Broker account group (nếu có)

**Charts Metabase:**

| # | Chart |
|---|-------|
| 1 | Daily lot bar chart |
| 2 | Weekly lot trend |
| 3 | Monthly progress gauge |
| 4 | Volume by risk tier |
| 5 | Volume by session |
| 6 | Volume by signal type |

---

### 3.3 Risk vs Volume Dashboard (Critical)

Trả lời: **Volume tăng có đi kèm equity/drawdown được kiểm soát không?**

| Metric | Nguồn |
|--------|-------|
| Total lots / trades | `volume_*` + `trades` |
| Avg lot per trade | aggregate |
| Win / loss / BE | `journal` / `trades` |
| Max floating risk | `risk_audit` |
| Daily / monthly DD | `risk_audit` |
| Risk per trade | `trades.risk_percent` |
| Blocked trades | `activity_logs` + `signal_audit` |
| Reduced by risk guard | `REDUCE_RISK` count |
| Blocked by spread | spread lock count |
| Blocked by news | news lock count |

**Cảnh báo audit:** Nếu volume ↑ mà drawdown ↑ quá nhanh → `UNHEALTHY_VOLUME`

---

### 3.4 Spread & Execution Audit

Ghi spread tại:

| Thời điểm | Field |
|-----------|-------|
| Seed | `spread_seed` |
| Entry trigger | `spread_entry` |
| Close | `spread_close` |
| Max trong trade | `max_spread` (nếu có feed) |

**Quy tắc:** spread > ngưỡng (vd. 30 pts) → `HIGH_SPREAD_RISK`  
Pending order + spread rộng → `PAUSE_PENDING` hoặc `CANCEL_PENDING`

**Charts:** avg spread by day/session, spread warning timeline, entry vs close, broker audit table

---

### 3.5 Signal Quality Dashboard

| Metric | Mô tả |
|--------|--------|
| Total / approved / waiting / rejected / closed | `signals` + `signal_audit` |
| Win / loss / BE | `trades` |
| TP1 / TP2 / SL hit rate | `activity_logs` event types |
| Avg RR | `signals` / `trades` |
| Best / worst session & setup | AI Brain + aggregates |
| High correlation risk outcomes | `correlation_risk_tag` filter |

**Câu hỏi then chốt:** Signal nào tạo **volume an toàn** và **chất lượng tốt**?

---

### 3.6 IB Business Audit

| Metric | Ghi chú |
|--------|---------|
| Daily / weekly / monthly lots | Báo cáo |
| Progress 200 lots | KPI display |
| Estimated commission | **Chỉ hiển thị** nếu có `commission_rate` |
| Active clients / groups | Optional CRM-lite |
| Avg lots per client | Business only |

**Hoa hồng IB = business metric — không dùng để approve trade.**

---

### 3.7 Bảng Supabase đề xuất

Chi tiết SQL: [`supabase/schema.sql`](../../supabase/schema.sql)

| Bảng / View | Vai trò |
|-------------|---------|
| `signals` | Signal master + correlation tag |
| `trades` | Lệnh mở/đóng + lot + PnL |
| `activity_logs` | Event trail (SEEDED, APPROVED, SPREAD_WARNING, …) |
| `volume_daily` | View — lots/trades/ngày |
| `volume_weekly` | View — lots/tuần |
| `volume_monthly` | View — KPI pace + projection |
| `risk_audit` | Floating risk, DD, action taken |
| `spread_audit` | Spread seed/entry/close + status |

**Event types (`activity_logs`):**

`SIGNAL_SEEDED` · `SIGNAL_APPROVED` · `SIGNAL_WAITING` · `SIGNAL_REJECTED` · `ENTRY_TRIGGERED` · `SPREAD_WARNING` · `PENDING_CANCELLED` · `TP1_HIT` · `TP2_HIT` · `SL_HIT` · `TRADE_CLOSED` · `JOURNAL_UPDATED`

---

### 3.8 Metabase Dashboard Cards (20 cards)

1. Monthly Volume Progress Gauge  
2. Daily Lots Bar Chart  
3. Weekly Lots Trend  
4. Monthly Lots vs 200 Target  
5. Remaining Lots Needed  
6. Required Daily Pace  
7. Projected Month-End Lots  
8. Volume by Session  
9. Volume by Client Group  
10. Volume by Risk Tier  
11. Risk vs Volume Chart  
12. Drawdown vs Volume Chart  
13. Spread Warning Count  
14. Average Spread by Session  
15. Signals Approved / Waiting / Rejected  
16. Win / Loss / Breakeven Summary  
17. TP1 / TP2 / SL Hit Rate  
18. High Correlation Risk Outcomes  
19. Blocked Trades by Reason  
20. IB Commission Estimate  

---

### 3.9 Audit Logic — Cảnh báo tự động

| Status | Điều kiện | Hành động hiển thị |
|--------|-----------|-------------------|
| `BELOW_TARGET_PACE` | Volume tháng chậm hơn pace cần | Hiện lots/ngày cần bắt kịp — **không** auto-trade |
| `UNHEALTHY_VOLUME` | Volume ↑ + drawdown ↑ nhanh | Cảnh báo overtrade |
| `BROKER_EXECUTION_RISK` | Spread vượt ngưỡng thường xuyên | Log broker audit |
| `OVERTRADE_RISK` | Vượt max trades/day | Block / yêu cầu approve thủ công |

---

### 3.10 Lộ trình triển khai (Cursor)

| Phase | Deliverable |
|-------|-------------|
| **1** ✅ | JSON local + terminal/HTML dashboard (`Phase D`) |
| **2** | Supabase tables + insert từ pipeline |
| **3** | SQL views `volume_daily/weekly/monthly` |
| **4** | Metabase → Supabase connection |
| **5** | 20 Metabase cards |

**Không** build broker execution. **Không** auto-trade theo volume target.

**Mapping file local → Supabase:**

| Local (Phase 1) | Supabase (Phase 2+) |
|-----------------|---------------------|
| `data/signals.json` | `signals` |
| `data/journal.json` | `trades` |
| `data/spread_audit.jsonl` | `spread_audit` |
| `data/risk_state.json` | `risk_audit` |
| `data/signal_audit.json` | `activity_logs` |
| `data/volume_tracker.json` | `volume_monthly` view |

---

## 4. Triết lý Risk-First Volume

### Thứ tự ưu tiên (không được đảo)

```text
1. Bảo vệ equity
2. Kiểm soát risk
3. Chất lượng signal
4. Giữ chân khách
5. Volume bền vững
6. Hoa hồng IB
```

### Volume là chỉ số kinh doanh, không phải quy tắc quyết định

| Volume LÀ | Volume KHÔNG PHẢI |
|-----------|-------------------|
| Theo dõi trên dashboard | Lý do mở thêm lệnh |
| Review hàng tuần/tháng | Trigger tăng lot |
| So với KPI 200 lots/tháng | Override quy tắc risk |
| Audit tính bền vững | Thay thế replay/forward test |

### Guardrail định vị

**Không** thiết kế hệ thống overtrade vì hoa hồng. Desk kiếm trust trước; volume đến từ khách ở lại và signal chất lượng ổn định.

### Ẩn dụ (giữ trong copy và SOP)

| Khái niệm | Ẩn dụ |
|-----------|-------|
| Equity | Bình xăng |
| Quản lý risk | Đồng hồ xăng |
| DXY / US10Y | Thời tiết |
| Multi-entry | Chia chuyến thành nhiều chặng |
| Volume | Quãng đường đã đi — không phải lý do lái ẩu |

---

## 5. Vấn đề cần tránh (từ brief gốc)

| Anti-pattern | Vì sao thất bại với IB |
|--------------|------------------------|
| Vào lệnh vì volume | Tổn equity và mất khách |
| Lot cố định không tính equity/risk | Phá trust giữa các tier khách |
| Martingale / recovery sizing | Vi phạm guardrail (G5, code đã chặn) |
| Bỏ qua spread lúc seed/close | Slippage ẩn làm xấu execution |
| Auto-reject mọi conflict correlation | Bỏ sót quan hệ vàng/DXY phức tạp |
| Auto-approve mọi alignment | Ảo tưởng về bộ lọc macro |
| KPI dashboard ép trade | Mâu thuẫn triết lý risk-first |
| Cam kết lợi nhuận trong seeding | Vi phạm guardrail G4 |
| Broker execution trong MVP | Ngoài scope — chỉ signal ops |
| CRM / funnel / content engine | Scope creep — không phải IB desk |

---

## 6. Hướng hệ thống đã chỉnh

### Giữ flow Hermes đã thích ứng

```text
Hermes XAUUSD Agent
  → Telegram DM / Signal Group
  → XAUUSD Trading MCP
  → Strategy Rooms (Market, Signal, Lot, Seeding, Journal, Dashboard, AI Brain)
  → Signal Replay / Forward Test
  → IB Signal Dashboard
  → XAUUSD AI Brain
  → Alex IB Jarvis Vision (hoãn)
```

### Thêm lớp Risk-First trên các room hiện có

```text
Market Room      → giá, session, spread, DXY, US10Y, news risk
Signal Room      → validate + correlation tag + safety locks
Lot Room         → công thức lot theo equity + chia multi-entry
Seeding Room     → ghi spread lúc seed
Journal Room     → spread close, ghi slippage, volume lots
Dashboard Room   → risk metrics + volume KPI + spread audit
AI Brain         → học từ journal + spread + correlation tags
```

### Kết quả quyết định (mở rộng APPROVE / WAIT / REJECT)

| Quyết định | Ý nghĩa |
|------------|---------|
| `APPROVE` | Tiếp tục lot → seed → publish |
| `WAIT` | Điều kiện chưa rõ — tin tức, correlation, spread |
| `REJECT` | Chặn cứng — thiếu SL, RR kém, safety lock |
| `REDUCE_RISK` | **Mới** — cho size nhỏ hơn hoặc ít entry, không full size |

---

## 7. Nâng cấp data pipeline

### Trường thị trường mới / mở rộng

| Trường | Nguồn (MVP) | Dùng bởi |
|--------|-------------|----------|
| `xauusd_price` | Stub thủ công / feed sau | Market Room, journal |
| `dxy_direction` | `bullish` / `bearish` / `neutral` | Bộ lọc correlation Signal |
| `us10y_direction` | `bullish` / `bearish` / `neutral` | Bộ lọc correlation Signal |
| `session` | `asia` / `london` / `ny` | Đã có trong `market_context.py` |
| `news_risk` | `low` / `elevated` / `high` | Signal gate + safety lock |
| `spread_pts` | Spread hiện tại | Market + spread lock |
| `spread_threshold` | Config (vd. 30–35 pts) | Spread lock |
| `entry_spread` | Ghi lúc seed / trigger | Spread audit |
| `close_spread` | Ghi lúc close | Spread audit |

### File đề xuất

```text
data/market_context.json     → thêm dxy_direction, us10y_direction, xauusd_price
data/signals.json            → thêm correlation_risk_tag, entry_spread, spread_at_seed
data/spread_audit.jsonl      → mới — log spread theo sự kiện
data/volume_tracker.json     → mới — tổng lot ngày/tuần/tháng
data/risk_state.json         → mới — floating risk %, daily DD, số trade
strategy-rooms/market-room/config.yaml → spread_threshold, quy tắc correlation
```

### Luồng pipeline

```text
[get_market_context]
  → bổ sung DXY/US10Y + spread
[check_signal]
  → RR + tin tức + correlation tag + safety locks
[calc_lot]
  → công thức equity + kiểm tra floating risk
[seed_signal]
  → ghi entry_spread
[publish_signal]
  → Alex approve (G6) — MVP vẫn mô phỏng cho đến khi wire Telegram API
[close_signal]
  → journal + close_spread + cộng volume + brain
[dashboard]
  → panel risk + volume KPI + spread audit
```

---

## 8. Thiết kế bộ lọc correlation

### Mục đích

Vàng thường phản ứng với USD mạnh (DXY) và áp lực lợi suất thực (US10Y). Bộ lọc **gắn tag và điều chỉnh** — không reject mù quáng mọi conflict.

### Đầu vào

- `direction`: `buy` | `sell` trên XAUUSD
- `dxy_direction`: `bullish` | `bearish` | `neutral`
- `us10y_direction`: `bullish` | `bearish` | `neutral`

### Ma trận conflict (logic ví dụ)

| XAUUSD | DXY | US10Y | Mức độ | Hành động gợi ý |
|--------|-----|-------|--------|-----------------|
| BUY | bullish | bullish | **Cao** | `REDUCE_RISK` hoặc `WAIT` |
| BUY | bullish | neutral | Trung bình | `REDUCE_RISK` |
| SELL | bearish | bearish | **Cao** | `REDUCE_RISK` hoặc `WAIT` |
| SELL | bearish | neutral | Trung bình | `REDUCE_RISK` |
| BUY | bearish | bearish | Thấp (thuận gió) | `APPROVE` — ghi nhận alignment |
| SELL | bullish | bullish | Thấp (thuận gió) | `APPROVE` — ghi nhận alignment |
| Bất kỳ | neutral | neutral | Không | Không gắn tag |

### Trường output trên signal

```json
{
  "correlation_risk_tag": "high | medium | low | aligned | none",
  "correlation_reasons": ["DXY bullish xung đột với XAUUSD BUY"],
  "correlation_action": "WAIT | REDUCE_RISK | APPROVE"
}
```

### Quy tắc

- **Không** auto-reject mọi conflict — mức độ quyết định `WAIT` vs `REDUCE_RISK`
- Luôn **log lý do** cho dashboard và brain review
- Operator (Alex) có thể override với approve rõ ràng — ghi trong publish gate

### Điểm triển khai

Mở rộng `src/signal_gate.py` → `check_signal()` với tham số `dxy_direction` và `us10y_direction`; gọi từ `telegram_router._cmd_check_signal` sau `get_market_context()`.

---

## 9. Logic tính lot

### Công thức

```text
Lot = (Equity × Risk%) / (Khoảng cách SL × giá trị mỗi point)
```

Trong đó:

- `Equity` = equity tài khoản khách (operator nhập mỗi lần calc)
- `Risk%` = từ tier khách (`client_groups.json`), cap bởi `max_risk_pct`
- `Khoảng cách SL` = |entry_mid − stop_loss| (đơn vị giá)
- `Giá trị mỗi point` = từ rule `pip_value_per_0_01_lot` (mở rộng cho XAUUSD)

### Quy tắc cứng

| Quy tắc | Thực thi |
|---------|----------|
| Không SL → không trade | `signal_gate` REJECT (đã có) |
| Không martingale | `lot_calculator` chặn recovery (đã có) |
| Không lot cố định không tính equity/risk | Thay output category bằng lot tính toán |
| Risk trước volume | Lot không scale để đạt 200 lots/tháng |
| Đạt max floating risk | Chặn `calc_lot` / publish mới |
| Spread vượt ngưỡng | Chặn hoặc WAIT trước calc lot |
| Cap tier | `max_lot` mỗi group trong `client_groups.json` |

### Gap so với MVP hiện tại

`src/lot_calculator.py` hiện trả **số tiền risk + lot category** — chưa có lot số cụ thể từ SL distance. Nâng cấp cần thêm `suggested_lot` và config `value_per_point` cho XAUUSD.

### Ví dụ

```text
Equity = 10,000
Risk%  = 1.0% (tier standard)
Risk$  = 100
SL dist = 9.0 points (vd. sell 4090 → SL 4099)
Value/pt mỗi 0.01 lot = 0.1 (config)
Lot = 100 / (9 × 10) ≈ 1.11 → cap theo max_lot tier
```

---

## 10. Quy tắc multi-entry

### Cho phép khi

- Tổng risk tất cả entry **bằng** kế hoạch single-entry gốc
- Mỗi leg có mức entry và lot riêng
- Tổng lot các leg ≤ `suggested_lot` gốc
- Safety locks (floating risk, spread, daily DD) pass cho kế hoạch **gộp**

### Ví dụ (hợp lệ)

```text
Kế hoạch gốc: 0.30 lot, risk 1.0% equity
Chia:
  Entry 1: 0.10 @ 4092
  Entry 2: 0.10 @ 4090
  Entry 3: 0.10 @ 4088
Tổng risk không đổi — cùng SL, cùng risk$ tổng
```

### Cấm

| Pattern | Lý do |
|---------|-------|
| Chia để tăng risk ngầm | Vi phạm triết lý risk-first |
| Chia để ép volume | Volume không phải mục tiêu trade |
| Chia để bypass max floating risk | Lách safety lock |
| Thêm entry sau khi đã full size | Cần signal / calc mới |

### Mô hình dữ liệu

```json
{
  "entries": [
    {"leg": 1, "lot": 0.10, "entry": 4092.0, "status": "pending"},
    {"leg": 2, "lot": 0.10, "entry": 4090.0, "status": "pending"},
    {"leg": 3, "lot": 0.10, "entry": 4088.0, "status": "pending"}
  ],
  "total_lot": 0.30,
  "risk_budget_usd": 100.0,
  "multi_entry_allowed": true
}
```

### Tool MCP đề xuất

`split_entries(signal_id, legs[])` — validate tổng lot bằng gốc và risk không đổi.

---

## 11. Quy tắc safety trigger

### 1. Khóa floating risk

```text
NẾU total_floating_risk >= 3% equity
THÌ chặn trade mới (REJECT hoặc WAIT trên check_signal / calc_lot)
```

Theo dõi signal mở + risk chưa thực hiện trong `data/risk_state.json`.

### 2. Khóa spread

```text
NẾU spread_pts > spread_threshold (vd. 30)
THÌ tạm dừng hoặc hủy signal pending
```

Repo hiện tại: `SPREAD_THRESHOLD = 35` trong `market_context.py` — căn config theo Alex (30 vs 35).

### 3. Khóa tin tức

```text
NẾU news_risk == high
THÌ WAIT hoặc REDUCE_RISK (đã có một phần — mở rộng REDUCE_RISK)
```

### 4. Khóa lỗ trong ngày

```text
NẾU daily_drawdown >= daily_limit (config theo tier hoặc desk)
THÌ chặn signal mới trong phần còn lại của phiên/ngày
```

### 5. Khóa số lệnh

```text
NẾU open_trades + signal_mới > max_trades_per_day
THÌ chặn signal mới
```

### Thứ tự đánh giá safety

```text
1. Thiếu SL / RR kém           → REJECT
2. Khóa daily loss              → REJECT
3. Khóa floating risk           → REJECT
4. Khóa số lệnh/ngày            → REJECT
5. Khóa spread                  → WAIT (pending) / hủy pending
6. Khóa tin tức                 → WAIT / REDUCE_RISK
7. Conflict correlation         → WAIT / REDUCE_RISK
8. Tất cả OK                    → APPROVE
```

### Module mới đề xuất

`src/safety_locks.py` — hàm `evaluate_safety_locks(equity, risk_state, market_ctx) -> dict`.

---

## 12. Nâng cấp dashboard

### Trạng thái hiện tại (MVP)

`src/dashboard.py` xuất: tổng/mở/đóng signal, W/L/BE, PnL, lot category, bài học.

### Panel risk metrics (thêm)

| Chỉ số | Nguồn |
|--------|-------|
| Equity (dùng gần nhất) | `risk_state.json` |
| Floating risk % | Tổng risk signal mở / equity |
| Daily drawdown | Journal + PnL mở |
| Max risk dùng hôm nay | Risk state |
| Lệnh đang mở | `signals.json` status live |
| Approved / rejected / waiting | Gate cache hoặc audit log |

### Panel volume metrics (thêm)

| Chỉ số | Nguồn |
|--------|-------|
| Lots ngày | `volume_tracker.json` |
| Lots tuần | Tổng hợp |
| Lots tháng | Tổng hợp |
| Tiến độ 200 lots/tháng | `monthly_lots / 200` — **chỉ hiển thị** |
| Lot trung bình / signal | volume / số signal |
| Số signal cần (nếu risk cho phép) | **thông tin** — `(200 - monthly) / avg_lot` kèm disclaimer |

### Panel spread audit (thêm)

| Chỉ số | Nguồn |
|--------|-------|
| Spread entry trung bình | `spread_audit.jsonl` |
| Spread close trung bình | Cùng file |
| Spread max | Cùng file |
| Số cảnh báo spread | Sự kiện spread > threshold |
| Signal bị chặn vì spread | Safety lock log |
| Sự kiện slippage | Chênh entry_spread vs trigger_spread |

### Panel chất lượng signal (mở rộng)

| Chỉ số | Nguồn |
|--------|-------|
| Win / loss / breakeven | Journal (đã có) |
| Session tốt / xấu nhất | Brain (đã có) |
| Setup type tốt nhất | Brain + journal |
| Lỗi lặp lại | Brain (đã có) |
| Kết quả correlation risk cao | Journal lọc theo `correlation_risk_tag` |

### HTML

Mở rộng `dashboard/ib-signals/index.html` với 3 section: **Risk**, **Volume KPI**, **Spread Audit**.

---

## 13. Thiết kế spread audit

### Ghi spread tại 3 sự kiện

| Sự kiện | Khi nào | Trường |
|---------|---------|--------|
| Seed | `seed_signal` chạy | `spread_at_seed` |
| Entry trigger | Signal live / fill đầu (log thủ công trong MVP) | `spread_at_entry` |
| Close | `close_signal` chạy | `spread_at_close` |

### Định dạng audit log (`data/spread_audit.jsonl`)

```json
{
  "ts": "2026-06-29T16:00:00Z",
  "signal_id": "sig-sell-4088",
  "event": "seed | entry | close",
  "spread_pts": 28.0,
  "threshold": 30.0,
  "spread_ok": true,
  "session": "london",
  "note": ""
}
```

### Dùng để

- Audit chất lượng broker (pattern spread nở theo session)
- Review slippage (`spread_at_entry - spread_at_seed`)
- Bảo vệ khách (chặn publish khi spread xấu)
- Input cho Brain (“spread nở 40% lệnh sell london”)

### Cờ slippage

```text
NẾU spread_at_entry - spread_at_seed > slippage_tolerance
THÌ gắn slippage_warning trong journal
```

---

## 14. Nâng cấp AI Brain

### Trạng thái hiện tại

`src/ai_brain.py` học từ **journal only** (tối thiểu 3 entry): session tốt/xấu, lỗi, ghi chú setup.

### Đầu vào bổ sung (sau nâng cấp)

| Đầu vào | Câu hỏi Brain trả lời |
|---------|----------------------|
| Kết quả journal | Setup nào hiệu quả nhất? |
| Tag session | Session nào an toàn nhất? |
| `correlation_risk_tag` | Điều kiện DXY/US10Y nào tạo risk? |
| Spread audit | Spread ảnh hưởng execution bao nhiêu %? |
| Lịch sử REDUCE_RISK / WAIT | Signal nào lẽ ra nên bỏ qua? |
| Volume tracker + equity | Volume tăng trong khi equity vẫn được bảo vệ? |
| Tần suất trade | Volume bền vững hay overtrade? |

### Trường insight mới (đề xuất)

```json
{
  "insights": {
    "best_session": "london",
    "worst_session": "asia",
    "high_correlation_loss_rate": 0.67,
    "spread_block_rate": 0.12,
    "avg_entry_spread": 27.5,
    "monthly_volume_lots": 45.2,
    "volume_kpi_progress": 0.226,
    "sustainable_volume_note": "Volume tăng với avg risk% ổn định; không thấy overtrade.",
    "overtrading_warning": false
  }
}
```

### Quy tắc (giữ nguyên)

- **Không bịa lợi nhuận** — brain chỉ đọc dữ liệu có cấu trúc
- **Không hứa kết quả** trong copy sinh ra
- Sample tối thiểu mỗi loại insight (vd. 5 trade có tag correlation trước khi insight correlation)

---

## 15. Mapping trực tiếp với Hermes XAUUSD IB Desk hiện tại

| Hạng mục nâng cấp | Artifact hiện có | Trạng thái | Hành động |
|-------------------|------------------|------------|-----------|
| Market context | `src/market_context.py` | Một phần | Thêm DXY, US10Y, giá, ngưỡng spread config |
| Validate signal | `src/signal_gate.py` | Một phần | Thêm correlation + `REDUCE_RISK` |
| Tính lot | `src/lot_calculator.py` | Một phần | Công thức lot đầy đủ + floating risk |
| Multi-entry | — | Thiếu | `src/multi_entry.py` + MCP tool |
| Safety locks | Guardrails G5 | Một phần | `src/safety_locks.py` |
| Spread audit | — | Thiếu | `src/spread_audit.py` + jsonl |
| Volume tracker | — | Thiếu | `src/volume_tracker.py` |
| Dashboard | `src/dashboard.py` + HTML | Một phần | Panel risk/volume/spread |
| AI Brain | `src/ai_brain.py` | Một phần | Nhận spread + correlation + volume |
| MCP tools | `mcp/xauusd-trading/server.py` | 11 tools | Thêm `create_signal`, `split_entries`, `safety_check` |
| Replay gate | `src/signal_replay.py` | Xong | Không đổi |
| Publish gate | `src/publish_gate.py` | Xong | Kiểm spread trước publish |
| Telegram | Hermes + bot live | Đang test | Publish API thật hoãn |
| Guardrails | `docs/guardrails.md` | Xong | Thêm G10 volume-not-objective |
| Client tiers | `data/client_groups.json` | Xong | Thêm daily DD limit, max trades/ngày |
| Knowledge | Tài sản này | Mới | Link từ README + knowledge asset chính |

### Mapping theo room

| Room | Trọng tâm nâng cấp |
|------|---------------------|
| Market Room | DXY, US10Y, ngưỡng spread, giá |
| Signal Room | Correlation tag, safety locks, REDUCE_RISK |
| Lot Room | Công thức lot đầy đủ, chia multi-entry |
| Seeding Room | Ghi spread lúc seed |
| Journal Room | Spread close, volume lots, ghi slippage |
| Dashboard Room | Risk + volume KPI + spread audit |
| AI Brain Room | Correlation + spread + volume bền vững |

---

## 16. Ghi chú triển khai MVP cho Cursor

### Phạm vi Phase D (build tiếp theo đề xuất)

**Mục tiêu:** Mở rộng risk-first trên MVP file-based — không broker API, không CRM.

### Thứ tự build (an toàn dependency)

```text
1. Schema data + config (market-room, client-groups, risk_state, volume_tracker, spread_audit)
2. safety_locks.py
3. market_context.py — trường DXY/US10Y/giá
4. signal_gate.py — correlation + REDUCE_RISK
5. lot_calculator.py — công thức lot đầy đủ
6. spread_audit.py — hook seed/entry/close
7. volume_tracker.py — cộng dồn khi close
8. multi_entry.py — validate chia entry
9. dashboard.py + index.html — panel mới
10. ai_brain.py — insight mở rộng
11. telegram_router.py + MCP server — wire tool mới
12. tests — safety, correlation, lot, spread, volume
```

### Tool MCP mới / mở rộng

| Tool | Ưu tiên |
|------|---------|
| `create_signal` | Cao — bỏ sửa JSON thủ công |
| `safety_check` | Cao |
| `split_entries` | Trung bình |
| `record_spread` | Trung bình |
| Mở rộng `check_signal` | Cao — correlation + locks |
| Mở rộng `calc_lot` | Cao — lot số |
| Mở rộng `dashboard` | Cao |
| Mở rộng `brain` | Trung bình |

### Config mặc định (hiệu chỉnh với Alex)

```yaml
# strategy-rooms/market-room/config.yaml
spread_threshold_pts: 30
slippage_tolerance_pts: 5
floating_risk_cap_pct: 3.0
daily_drawdown_cap_pct: 3.0
max_trades_per_day: 5
volume_kpi_monthly_lots: 200
xauusd_value_per_point_per_0_01_lot: 0.1
```

### Guardrail mới (đề xuất G10)

**G10 — Volume không phải mục tiêu:** Dashboard có thể hiển thị tiến độ KPI volume. Không tool, cron, hay prompt agent nào được tăng tần suất trade, lot size, hay số signal để đạt mục tiêu volume.

### Test cần thêm

- Correlation cao → WAIT hoặc REDUCE_RISK, không APPROVE im lặng
- Floating risk 3% → chặn calc_lot mới
- Spread 31 > ngưỡng 30 → WAIT
- Multi-entry: tổng lot bằng gốc
- Volume tracker chỉ tăng khi close
- Brain không bịa insight dưới sample tối thiểu

### Ngoài scope Phase D

- Feed DXY/US10Y live (nhập hướng thủ công OK trong MVP)
- Publish Telegram thật (task riêng)
- Broker execution
- Alex IB Jarvis Vision

---

## 17. Prompt tiếp theo chạy với `$mvp-code-builder`

Copy và chạy:

```text
$mvp-code-builder

PROJECT: Hermes XAUUSD IB Trading Desk
WORKDIR: hermes-xauusd-ib-desk
KNOWLEDGE ASSET: knowledge/distilled/hermes-xauusd-risk-first-volume-desk-upgrade.vi.md

TASK: Triển khai Phase D — nâng cấp Risk-First Volume Desk trên MVP file-based hiện có.

BUILD THEO THỨ TỰ:
1. Thêm config mặc định vào strategy-rooms/market-room/config.yaml (spread 30, floating risk 3%, daily DD 3%, max trades/ngày 5, KPI volume 200 lots/tháng chỉ hiển thị).
2. Tạo src/safety_locks.py — đánh giá floating risk, spread, tin tức, daily DD, số lệnh.
3. Mở rộng src/market_context.py — thêm xauusd_price, dxy_direction, us10y_direction, spread_threshold từ config.
4. Mở rộng src/signal_gate.py — bộ lọc DXY/US10Y; trả REDUCE_RISK khi phù hợp; lưu correlation_risk_tag.
5. Nâng cấp src/lot_calculator.py — Lot = (Equity × Risk%) / (SL distance × value per point); tôn max_lot và safety locks.
6. Tạo src/spread_audit.py + data/spread_audit.jsonl — log spread lúc seed, entry, close.
7. Tạo src/volume_tracker.py + data/volume_tracker.json — theo dõi lots ngày/tuần/tháng; KPI chỉ hiển thị.
8. Tạo src/multi_entry.py — chia entry chỉ khi tổng risk không đổi.
9. Thêm MCP tool create_signal — đăng ký signal trong data/signals.json từ Telegram/Hermes.
10. Mở rộng dashboard.py và dashboard/ib-signals/index.html — panel risk, volume KPI, spread audit.
11. Mở rộng ai_brain.py — insight từ spread audit, correlation tags, volume vs bảo vệ equity.
12. Thêm tests trong tests/ cho safety locks, correlation, lot formula, multi-entry, volume tracker.
13. Cập nhật docs/guardrails.md với G10 (volume không phải mục tiêu).

RÀNG BUỘC:
- Không broker API, không mật khẩu khách, không CRM, không cam kết lợi nhuận.
- KPI volume chỉ trên dashboard — không bao giờ trigger trade.
- Giữ flow replay/forward-test/publish gate hiện có.
- Khớp style code trong src/ và mcp/xauusd-trading/server.py.
- Chạy tests/run_tests.py — tất cả phải pass.

TIÊU CHÍ CHẤP NHẬN:
- check_signal trả correlation tag và REDUCE_RISK khi DXY xung đột với XAUUSD BUY.
- calc_lot trả suggested_lot số từ equity và SL distance.
- spread được log lúc seed và close.
- dashboard hiển thị tiến độ volume tháng hướng 200 lots mà không ảnh hưởng quyết định trade.
- create_signal hoạt động từ MCP không cần sửa JSON thủ công.
```

---

## Khuyến nghị tài sản

| Tài sản | Đường dẫn | Hành động |
|---------|-----------|-----------|
| Knowledge asset (VI) | `knowledge/distilled/hermes-xauusd-risk-first-volume-desk-upgrade.vi.md` | Đã lưu |
| Knowledge asset (EN) | `knowledge/distilled/hermes-xauusd-risk-first-volume-desk-upgrade.md` | Đã lưu |
| Guardrail G10 | `docs/guardrails.md` | Thêm trong Phase D |
| Config Market Room | `strategy-rooms/market-room/config.yaml` | Mở rộng |
| SOP bổ sung | `docs/sop-ops-runbook.md` | Thêm mục review risk-first hàng ngày |
| Supabase schema | `supabase/schema.sql` | Phase 2 reporting |
| Cursor rule | `.cursor/rules/hermes-xauusd-desk.mdc` | Tham chiếu volume-not-objective |

## Ứng viên skill

| Ứng viên | Mục đích |
|----------|----------|
| `xauusd-risk-first-desk` | Skill agent cho vận hành IB risk-first |
| `spread-audit-review` | Playbook audit spread/slippage hàng tuần |

## Tiêu chí chấp nhận (knowledge asset)

- [x] Đủ 17 mục (bao gồm Reporting & Audit §3)
- [x] Mapping file repo hiện có và gap
- [x] KPI volume rõ ràng không phải quyết định trade
- [x] Thiết kế correlation với WAIT / REDUCE_RISK
- [x] Thứ tự triển khai MVP cho Cursor
- [x] Prompt `$mvp-code-builder` tiếp theo
- [x] Thiết kế Supabase + Metabase reporting layer
- [ ] Code Phase E (Supabase sync + Metabase)

---

## Liên quan

- [hermes-xauusd-ib-desk-knowledge-asset.md](./hermes-xauusd-ib-desk-knowledge-asset.md)
- [hermes-xauusd-risk-first-volume-desk-upgrade.md](./hermes-xauusd-risk-first-volume-desk-upgrade.md) (bản EN)
- [docs/architecture.md](../../docs/architecture.md)
- [docs/guardrails.md](../../docs/guardrails.md)
- [docs/mvp-build-map.md](../../docs/mvp-build-map.md)
- [supabase/schema.sql](../../supabase/schema.sql)
