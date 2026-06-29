# Tạo bot Telegram (BotFather) + gắn Hermes

> Dành cho **Alex — Hermes XAUUSD IB Desk**  
> MVP repo vẫn **mô phỏng** publish (`data/publish_log.json`). Bước này chuẩn bị **Hermes Agent + Telegram thật**.

---

## Tổng quan

```text
BotFather (tạo bot, lấy token)
    → Lấy User ID của bạn (Alex)
    → Nhập vào Hermes Agent / Hermes Desktop
    → Chat với Hermes qua Telegram
    → (Sau) Gắn XAUUSD Trading MCP
```

---

## Bước 1 — Tạo bot với BotFather

1. Mở Telegram, tìm **[@BotFather](https://t.me/BotFather)**
2. Gửi lệnh:

```text
/newbot
```

3. BotFather hỏi **tên hiển thị** (ví dụ):

```text
Hermes XAUUSD Desk
```

4. BotFather hỏi **username** (phải kết thúc bằng `bot`, ví dụ):

```text
HermesXAUUSD_AlexBot
```

5. BotFather trả về **HTTP API Token** dạng:

```text
7123456789:AAHxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Lưu token này** — chỉ hiện một lần. Không chia sẻ công khai.

### Tùy chọn BotFather (nên bật)

| Lệnh BotFather | Mục đích |
|----------------|----------|
| `/setdescription` | Mô tả bot cho khách |
| `/setabouttext` | Giới thiệu ngắn |
| `/setcommands` | Menu lệnh (xem mẫu bên dưới) |

**Mẫu `/setcommands` cho desk:**

```text
check_signal - Kiem tra signal XAUUSD
calc_lot - Tinh lot theo tier
seed_signal - Tao seeding Telegram
dashboard - Xem tom tat desk
brain - Bai hoc tu journal
replay - Replay setup (london-breakout)
help - Huong dan
```

---

## Bước 2 — Lấy User ID của bạn (Alex)

Hermes cần **User ID** để chỉ bạn mới điều khiển bot (DM operator).

1. Mở **[@userinfobot](https://t.me/userinfobot)** hoặc **[@getidsbot](https://t.me/getidsbot)**
2. Gửi `/start`
3. Copy số **Id** (ví dụ `123456789`) — đây là `TELEGRAM_OPERATOR_USER_ID`

---

## Bước 3 — Lưu token trong repo (local only)

```bash
cd hermes-xauusd-ib-desk
copy telegram\env.example telegram\.env
```

Mở `telegram/.env` và điền:

```env
TELEGRAM_BOT_TOKEN=7123456789:AAH...
TELEGRAM_OPERATOR_USER_ID=123456789
TELEGRAM_BOT_NAME=HermesXAUUSDBot
```

**Không commit** file `.env` (đã có trong `.gitignore`).

Kiểm tra token:

```bash
python scripts/telegram_verify.py
```

Kết quả mong đợi: `OK - Bot hop le` + username bot.

---

## Bước 4 — Gắn bot vào Hermes Agent

### Cách A — Cài Hermes lần đầu (terminal installer)

Theo video gốc:

1. Chạy **one-line installer** Hermes (trên trang Hermes Agent)
2. Chọn **Quick setup**
3. Chọn AI provider / model
4. Khi hỏi **Telegram**:
   - Dán **Bot Token** từ BotFather
   - Nhập **User ID** của bạn
5. Hoàn tất → mở bot trên Telegram → gửi `/start`

### Cách B — Đã cài Hermes → dùng Hermes Desktop

1. Mở **Hermes Desktop**
2. Vào **Messaging** / **Telegram**
3. Nhập:
   - **Bot Token** (từ BotFather)
   - **Allowed User ID** = User ID của Alex
4. **Save** → kiểm tra trạng thái bot **online**
5. Trên Telegram, mở bot → `/start` → thử chat

### Cách C — Sửa config Hermes (nếu biết đường dẫn)

Hermes lưu config trên máy local (không nằm trong repo này). Dùng Desktop để sửa — **không** paste token vào git.

---

## Bước 5 — Tạo nhóm Signal (IB clients)

1. Telegram → **New Group** (ví dụ tên: `XAUUSD Signals — Alex IB`)
2. **Add members** (khách / channel subscribers)
3. **Add bot** của bạn làm admin (quyền gửi tin)
4. (Tùy chọn) Bật **Topics** nếu muốn chia phòng như video:
   - `market-desk`
   - `signal-desk`
   - `journal-desk`

5. Lấy **Chat ID** nhóm (dùng [@getidsbot](https://t.me/getidsbot) forward 1 tin từ group, hoặc API `getUpdates`):

```bash
# Sau khi bot da trong group, gui 1 tin trong group roi:
# https://api.telegram.org/bot<TOKEN>/getUpdates
```

Thêm vào `telegram/.env` (optional):

```env
TELEGRAM_SIGNAL_GROUP_CHAT_ID=-1001234567890
```

> **MVP hiện tại:** `publish_signal` vẫn chỉ ghi `data/publish_log.json`. Khi bạn sẵn sàng bật Telegram thật, sẽ nối module gửi tin dùng token + chat ID này.

---

## Bước 6 — Gắn XAUUSD Trading MCP (sau khi Telegram OK)

Xem [hermes-mcp-setup.md](./hermes-mcp-setup.md):

1. Hermes Desktop → MCP → `xauusd-trading`
2. Trong Telegram chat với Hermes, thử nhờ agent gọi tool `replay_signals` hoặc `check_signal`

---

## Quy trình vận hành đề xuất

```text
1. Alex chat Hermes qua DM bot (operator)
2. Hermes goi MCP: replay -> check -> lot -> seed
3. Alex approve publish (G6)
4. (Sau MVP) Bot post vao Signal Group
5. close_signal -> journal -> brain -> dashboard
```

---

## Bảo mật

| Việc | Quy tắc |
|------|---------|
| Token bot | Chỉ trong `.env` / Hermes Desktop — **không commit** |
| User ID khách | Không lưu password broker |
| Publish | Luôn cần Alex approve trước Signal Group |
| CRM / funnel | Không dùng bot để spam lead |

---

## Xử lý lỗi

| Triệu chứng | Cách xử lý |
|-------------|------------|
| `telegram_verify.py` fail | Token sai hoặc copy thiếu ký tự |
| Hermes bot offline | Desktop → restart gateway / kiểm tra token |
| Bot không trả lời | `/start` lại; kiểm tra User ID trong Hermes |
| Không gửi được group | Bot phải là admin group; đúng Chat ID |

---

## Checklist nhanh

- [ ] Tạo bot `@...bot` qua BotFather
- [ ] Lưu token vào `telegram/.env`
- [ ] Lấy User ID → `TELEGRAM_OPERATOR_USER_ID`
- [ ] `python scripts/telegram_verify.py` → OK
- [ ] Nhập token + User ID vào Hermes Desktop
- [ ] Chat `/start` với bot thành công
- [ ] (Tùy chọn) Tạo Signal Group + thêm bot
- [ ] Gắn MCP `xauusd-trading` ([hermes-mcp-setup.md](./hermes-mcp-setup.md))

---

## Liên quan

- [Hermes MCP setup](./hermes-mcp-setup.md)
- [Signal format](../telegram/signal-format.md)
- [Seeding guidelines](../telegram/seeding-guidelines.md)
