#!/usr/bin/env python3
"""
Kiem tra Telegram bot token (BotFather).

Usage:
  1. Copy telegram/env.example -> telegram/.env
  2. Dien TELEGRAM_BOT_TOKEN
  3. python scripts/telegram_verify.py
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ENV_PATH = REPO / "telegram" / ".env"


def load_env(path: Path) -> dict[str, str]:
    if not path.exists():
        print(f"Chua co file: {path}")
        print("Copy tu telegram/env.example -> telegram/.env va dien token.")
        sys.exit(1)
    env: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    return env


def main() -> None:
    env = load_env(ENV_PATH)
    token = env.get("TELEGRAM_BOT_TOKEN", "")
    if not token:
        print("TELEGRAM_BOT_TOKEN trong trong telegram/.env")
        sys.exit(1)

    url = f"https://api.telegram.org/bot{token}/getMe"
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"Token khong hop le hoac loi API: {e}")
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Khong ket noi duoc Telegram API: {e}")
        sys.exit(1)

    if not data.get("ok"):
        print("Token loi:", data)
        sys.exit(1)

    bot = data["result"]
    print("OK - Bot hop le")
    print(f"  Username: @{bot.get('username')}")
    print(f"  Ten:      {bot.get('first_name')}")
    print(f"  Bot ID:   {bot.get('id')}")
    print()
    print("Buoc tiep: gan token vao Hermes Desktop (xem docs/telegram-bot-setup.md)")

    user_id = env.get("TELEGRAM_OPERATOR_USER_ID")
    if user_id:
        print(f"  Operator User ID da luu: {user_id}")
    else:
        print("  Chua co TELEGRAM_OPERATOR_USER_ID — them vao telegram/.env")


if __name__ == "__main__":
    main()
