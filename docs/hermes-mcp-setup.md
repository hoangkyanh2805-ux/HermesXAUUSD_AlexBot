# Hermes MCP — Hướng dẫn gắn XAUUSD Trading Desk

> Gắn **XAUUSD Trading MCP** vào Hermes Agent (Desktop). Không dùng Telegram thật hay broker API trong MVP.

## Yêu cầu

- Python 3.11+
- Hermes Agent + Desktop đã cài
- Repo: `hermes-xauusd-ib-desk`

```bash
cd hermes-xauusd-ib-desk
pip install mcp
python tests/run_tests.py    # xác nhận ổn định trước khi gắn
```

## Bước 1 — Kiểm tra MCP chạy local

```bash
python mcp/xauusd-trading/server.py
```

Server chạy stdio — sẽ chờ input (không thoát ngay = OK). Nhấn Ctrl+C để dừng.

## Bước 2 — Thêm vào Hermes Desktop

1. Mở **Hermes Desktop**
2. Vào **MCP Servers** → **Add Server**
3. Điền:

| Field | Giá trị |
|-------|---------|
| Name | `xauusd-trading` |
| Command | `python` (hoặc đường dẫn đầy đủ tới python.exe) |
| Args | `mcp/xauusd-trading/server.py` |
| Working directory | Thư mục gốc repo `hermes-xauusd-ib-desk` |

4. Save → Restart gateway nếu được hỏi
5. Kiểm tra trạng thái server **online**

Tham khảo file mẫu: `mcp/xauusd-trading/hermes-mcp.example.json` (sửa `cwd` cho máy bạn).

## Bước 3 — Tools có sẵn (11 tools)

| Tool | Tương đương video | Mô tả |
|------|-------------------|--------|
| `replay_signals` | Backtest | Replay 30 signal lịch sử, gate pass/fail |
| `check_signal` | Strategy Room | Market + validate signal |
| `calc_lot` | Lot Room | Lot theo tier |
| `seed_signal` | Seeding Room | Tin nhắn Telegram tự nhiên |
| `publish_signal` | Telegram | Mô phỏng publish — **cần Alex approve** |
| `close_signal` | Journal | Ghi journal + brain |
| `promote_setup` | Promotion | draft → replay_passed → forward_test → live |
| `start_forward_test` | Forward test | Bắt đầu paper track 7 ngày |
| `forward_test_check` | Cron | Kiểm tra forward test (notify only) |
| `dashboard` | Dashboard | Tóm tắt desk |
| `brain` | AI Brain | Bài học từ journal |

## Bước 4 — Quy trình gợi ý trong Hermes (Telegram)

Gửi Hermes theo thứ tự:

```text
1. replay_signals setup_name=london-breakout
2. start_forward_test setup_name=london-breakout   (sau replay pass)
3. promote_setup setup_name=london-breakout status=live   (sau 7 ngày forward test)
4. check_signal signal_id=sig-001
5. calc_lot signal_id=sig-001 equity=10000 tier=standard
6. seed_signal signal_id=sig-001
7. publish_signal signal_id=sig-001 alex_approved=true   (chỉ khi Alex đồng ý)
8. close_signal ... → dashboard → brain
```

## Phase C — Replay dataset

| File | Mô tả |
|------|--------|
| `data/replay/london-breakout.json` | 30 signal — **pass** gate |
| `data/replay/ny-reversal.json` | 30 signal — **fail** gate (demo) |
| `data/setups.json` | Trạng thái setup |
| `strategy-rooms/signal-room/replay/latest.json` | Kết quả replay gần nhất |

Gate mặc định (`strategy-rooms/signal-room/config.yaml`):

- Win rate ≥ 55%
- Avg R ≥ 1.5
- Max drawdown ≤ 15%
- Sample ≥ 20

## Lệnh local (trước khi gắn Hermes)

```bash
python src/main.py
```

Hoặc từng lệnh:

```text
/replay london-breakout
/forward_test start london-breakout
/promote_setup london-breakout live
/check_signal sig-001
...
```

## Giới hạn MVP (cố ý)

- Không gọi Telegram API thật
- Không gọi broker API
- `publish_signal` chỉ ghi `data/publish_log.json`
- Forward test không tự promote lên `live` — Alex quyết định

## Xử lý lỗi

| Lỗi | Cách xử lý |
|-----|------------|
| MCP offline | Kiểm tra `cwd` và đường dẫn `python` |
| Publish blocked | Chạy `/replay` + promote setup trước |
| Brain "not enough data" | Cần ≥3 signal đóng trong journal |
| Import error `mcp` | `pip install mcp` |

## Liên quan

- [Agent OS Operating Model](../docs/agent-os-operating-model.md)
- [Architecture](../docs/architecture.md)
- `agents/hermes-xauusd-agent.md`
