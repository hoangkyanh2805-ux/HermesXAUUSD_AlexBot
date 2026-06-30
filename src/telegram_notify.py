"""Operator Telegram alerts — safety locks and critical desk events."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from src.common import REPO_ROOT

TELEGRAM_ENV = REPO_ROOT / "telegram" / ".env"


def _load_telegram_env() -> dict[str, str]:
    env: dict[str, str] = {}
    if TELEGRAM_ENV.exists():
        for line in TELEGRAM_ENV.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    for key in ("TELEGRAM_BOT_TOKEN", "TELEGRAM_OPERATOR_USER_ID", "TELEGRAM_SIGNAL_GROUP_CHAT_ID"):
        env[key] = os.environ.get(key, env.get(key, ""))
    return env


def send_operator_alert(
    message: str,
    *,
    severity: str = "critical",
    parse_mode: str | None = None,
) -> dict[str, Any]:
    """
    Send alert to operator Telegram chat.
    severity: critical (red) | warning | info
    """
    cfg = _load_telegram_env()
    token = cfg.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = cfg.get("TELEGRAM_OPERATOR_USER_ID") or cfg.get("TELEGRAM_SIGNAL_GROUP_CHAT_ID", "")
    if not token or not chat_id:
        return {
            "ok": False,
            "skipped": True,
            "error": "Missing TELEGRAM_BOT_TOKEN or TELEGRAM_OPERATOR_USER_ID in telegram/.env",
        }

    prefix = {"critical": "🔴 SAFETY LOCK", "warning": "🟠 WARNING", "info": "ℹ️"}.get(
        severity, "🔴"
    )
    text = f"{prefix}\n{message}"

    body: dict[str, Any] = {"chat_id": chat_id, "text": text}
    if parse_mode:
        body["parse_mode"] = parse_mode

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        return {"ok": bool(payload.get("ok")), "result": payload.get("result")}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        return {"ok": False, "error": f"HTTP {exc.code}: {detail[:300]}"}
    except (urllib.error.URLError, OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": str(exc)}


def send_safety_lock_alert(lock_detail: str, *, floating_risk_pct: float, cap_pct: float) -> dict[str, Any]:
    """Red alert when floating lot risk blocks seeding."""
    msg = (
        f"Hermes IB Desk — seed_signal BLOCKED\n"
        f"Floating risk: {floating_risk_pct:.2f}% / cap {cap_pct:.1f}% equity\n"
        f"{lock_detail}\n"
        f"Action: reduce open exposure before new seeds."
    )
    return send_operator_alert(msg, severity="critical")


def send_correlation_alert(signal_id: str, correlation_data: dict[str, Any]) -> dict[str, Any]:
    """Red alert when DXY/US10Y conflicts at seed snapshot."""
    tag = correlation_data.get("tag", "unknown")
    score = correlation_data.get("condition_score")
    warnings = correlation_data.get("warnings") or correlation_data.get("reasons") or []
    warn_line = warnings[0] if warnings else "Correlation conflict detected"
    msg = (
        f"Hermes IB Desk — CORRELATION_RISK at seed\n"
        f"Signal: {signal_id}\n"
        f"Tag: {tag} | Score: {score}\n"
        f"{warn_line}\n"
        f"DXY: {correlation_data.get('dxy_direction')} | US10Y: {correlation_data.get('us10y_direction')}"
    )
    return send_operator_alert(msg, severity="critical")
