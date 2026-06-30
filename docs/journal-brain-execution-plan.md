# Plan — Journal + Brain + Execution Reconcile

> **Trạng thái:** Plan (chưa implement đầy đủ)  
> **Liên quan:** Phase 3 MVP · G8 (`docs/guardrails.md`) · G2 (không auto trade)  
> **Cập nhật:** 2026-06-30

---

## 1. Vấn đề cần giải quyết

Hermes IB Desk quản **tín hiệu + risk + vận hành**. MT5 là **lớp thực thi riêng** — khách tự vào lệnh, chỉnh volume, partial TP, dời SL.

| Thực tế | Signal desk (hiện tại) | MT5 (ngoài repo) |
|---------|------------------------|------------------|
| Giá vào | Zone `entry_low`–`entry_high` | Fill price khác zone |
| Volume | `suggested_lot` từ `/calc_lot` | Client tự chỉnh |
| SL/TP | Cố định trên signal | Có thể BE / partial |
| PnL | Operator **gõ tay** lúc close | Ground truth trên account |

**Gap:** `close_signal` ghi journal với entry/lot **theo kế hoạch desk**, không phải deal MT5. Chỉ `pnl` + `lesson` mang thông tin thực tế (nếu Alex nhập đúng).

**Mục tiêu plan:** Tách rõ **plan vs actual**, hoàn thiện G8 brain writers, không vi phạm G2/G3.

---

## 2. Phạm vi — làm gì / không làm gì

### Làm (trong plan)

- Mở rộng journal: `planned_*` vs `actual_*`
- `update_brain` ghi `knowledge/brain/outcomes.jsonl` + `pairings.md`
- Close flow hỗ trợ reconcile thủ công (Hướng A)
- (Tùy chọn sau) Import MT5 deals read-only (Hướng B)
- E2E test: close → journal → brain files → dashboard

### Không làm

- Broker execution API / đặt lệnh tự động (G2)
- Lưu password MT5 khách (G3)
- Dùng volume KPI để trigger signal (G10)

---

## 3. Kiến trúc hai lớp

```text
┌─────────────────────────────────────────────────────────────┐
│  SIGNAL DESK (tự động, tin được trước publish)              │
│  check → lot gợi ý → seed → publish → correlation snapshot   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │  MT5 — khách trade   │  ← ngoài repo
                 └─────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  EXECUTION RECONCILE (sau close)                             │
│  planned_* (từ signal)  +  actual_* (từ Alex / MT5 export)   │
│  → journal → outcomes.jsonl → pairings.md → ai_brain.json    │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Trạng thái hiện tại vs mục tiêu

| Hạng mục | Hiện tại | Mục tiêu plan |
|----------|----------|---------------|
| `append_journal` | ✅ `data/journal.json` | Giữ + thêm `planned_*` / `actual_*` |
| `summarize()` → `ai_brain.json` | ✅ | Giữ; đọc từ actual khi có |
| `update_brain` MCP | ❌ | ✅ tool + gọi từ `close_signal` |
| `knowledge/brain/outcomes.jsonl` | ❌ trống | ✅ 1 dòng JSON mỗi close |
| `knowledge/brain/pairings.md` | ❌ placeholder | ✅ append khi pattern rõ |
| Volume KPI | Lot **gợi ý** | Option: `actual_lots` cho KPI |
| `run_sig_test_001` | Dừng ở publish | ✅ thêm close + assert brain |
| MT5 bridge | ❌ | Hướng B — Phase I (defer) |

---

## 5. Lộ trình triển khai

### Phase 3A — Manual reconcile + brain writers (ưu tiên)

**Goal:** Operator đóng lệnh với plan vs actual; G8 đủ 3 bước.

| # | Task | Output | Verify |
|---|------|--------|--------|
| 3A.1 | Schema journal mở rộng | `planned_entry`, `actual_fill`, `planned_lots`, `actual_lots`, `actual_exit`, `pnl_source` | Unit test append |
| 3A.2 | `/close_signal` nhận actual (args hoặc key=value) | Router parse `actual_fill=4017.2` | Integration test |
| 3A.3 | `update_brain()` module | `src/brain_writer.py` | Ghi outcomes + pairings |
| 3A.4 | MCP `update_brain` | `mcp/xauusd-trading/server.py` | tools/list có tool |
| 3A.5 | `close_signal` gọi `update_brain` | Sau `append_journal` | File brain không còn trống |
| 3A.6 | Volume: `record_volume(actual_lots or planned_lots)` | `volume_tracker.py` | KPI dùng actual nếu có |
| 3A.7 | Supabase sync map fields mới | `supabase_sync.py` + migration nếu cần | trades row có actual_* |
| 3A.8 | E2E `run_sig_test_001` + close | `pipeline_test_flow.py` | 46+ tests, full 9-step |

**Lệnh close mẫu (draft):**

```text
/close_signal sig-001 win 187.5 \
  actual_fill=4017.2 actual_lots=0.08 actual_exit=4005.0 \
  "TP1 partial, rest BE"
```

**Acceptance 3A:**

- [ ] Close 1 signal → `journal.json` có cả `planned_*` và `actual_*`
- [ ] `outcomes.jsonl` có ≥1 dòng
- [ ] `pairings.md` cập nhật (hoặc ghi "insufficient pattern" nếu <3 samples)
- [ ] `ai_brain.json` refresh
- [ ] `test_sig_test_001` chạy qua close
- [ ] G2/G3/G10 không bị phá

---

### Phase 3B — E2E demo + docs hygiene

| # | Task | Output |
|---|------|--------|
| 3B.1 | Cập nhật `mvp-build-map.md` checkbox Phase 0–3 | Trạng thái thực tế |
| 3B.2 | Cập nhật `docs/first-sprint.md` demo script | 9 bước + close actual |
| 3B.3 | SOP operator: đọc MT5 → gõ close | `docs/sop-ops-runbook.md` § close |
| 3B.4 | Metabase card (optional): plan vs actual slippage | SQL trên `trades` |

**Acceptance 3B:**

- [ ] `python src/main.py` + `run_sig_test_001 --live` documented
- [ ] Operator SOP có checklist MT5 → close_signal

---

### Phase I — MT5 export read-only (defer, sau 3A)

**Goal:** Giảm nhập tay; vẫn G2 read-only.

| # | Task | Output |
|---|------|--------|
| I.1 | Spec format `data/mt5_deals/import.json` | Doc trong plan |
| I.2 | `scripts/import_mt5_deals.py` | Map ticket → signal_id |
| I.3 | `reconcile_signal(signal_id, deal)` | Fill actual_* từ import |
| I.4 | Alex gán `mt5_ticket` lúc publish (optional) | Field trên signal |

**Không bao gồm:** EA auto-trade, credential pool, multi-account sync realtime.

---

## 6. Schema journal (draft)

```json
{
  "signal_id": "sig-001",
  "result": "win",
  "pnl": 187.5,
  "pnl_source": "mt5_manual",
  "planned": {
    "entry": 4017.0,
    "stop_loss": 4028.0,
    "take_profits": [4000.0],
    "lots": 0.1,
    "lot_category": "small",
    "risk_percent_used": 1.0
  },
  "actual": {
    "fill": 4017.2,
    "exit": 4005.0,
    "lots": 0.08,
    "mt5_ticket": null,
    "notes": "TP1 partial"
  },
  "session": "london",
  "correlation_risk_tag": "medium",
  "spread_at_close": 28.0,
  "lesson": "TP1 partial, macro aligned",
  "date": "2026-06-30"
}
```

Backward compatible: nếu không có `actual`, coi như chỉ plan + pnl manual (hành vi hiện tại).

---

## 7. Brain writers — hợp đồng G8

Sau mỗi `close_signal` thành công:

1. **`append_journal`** → `data/journal.json`
2. **`update_brain`** →
   - append 1 line `knowledge/brain/outcomes.jsonl`
   - update `knowledge/brain/pairings.md` nếu setup/session pattern đủ mẫu
   - gọi `summarize()` → `data/ai_brain.json`
3. **`export_state`** → dashboard

`outcomes.jsonl` mẫu:

```json
{"signal_id":"sig-001","result":"win","pnl":187.5,"session":"london","setup":"london-breakout","planned_lots":0.1,"actual_lots":0.08,"slippage_pts":0.2,"correlation_tag":"medium","ts":"2026-06-30T12:00:00Z"}
```

---

## 8. Rủi ro & giảm thiểu

| Rủi ro | Giảm thiểu |
|--------|------------|
| Alex nhập sai PnL | `pnl_source` + double-check SOP; sau này import MT5 |
| Volume KPI lệch broker | G10: KPI chỉ xem; ưu tiên `actual_lots` khi có |
| Scope creep → full OMS | Chỉ read-only import; G2 trong review PR |
| Journal phình schema | `planned` / `actual` nested object; migration script |

---

## 9. Liên kết tài liệu

| File | Vai trò |
|------|---------|
| [mvp-build-map.md](./mvp-build-map.md) | Critical path item 7–8 |
| [guardrails.md](./guardrails.md) | G2, G3, G8, G10 |
| [flow.md](./flow.md) | 9-step use case |
| [soul.md](../soul.md) | Pipeline operator |
| [sop-ops-runbook.md](./sop-ops-runbook.md) | Close + reconcile SOP (sau 3B) |

---

## 10. Definition of Done (Phase 3 plan)

Plan coi **hoàn tất** khi Phase **3A + 3B** acceptance criteria đều checked. Phase **I** (MT5 export) là stretch goal, không chặn MVP desk close loop.
