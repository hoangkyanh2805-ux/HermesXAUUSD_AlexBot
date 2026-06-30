#!/usr/bin/env python3
"""Ping Supabase REST — confirms supabase/.env or env vars are loaded."""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.supabase_sync import ENV_PATH, get_supabase_config


def main() -> int:
    cfg = get_supabase_config()
    out: dict = {
        "env_file": str(ENV_PATH),
        "env_file_exists": ENV_PATH.exists(),
        "url": cfg["url"],
        "key_set": bool(cfg["service_key"]),
        "key_prefix": (cfg["service_key"][:12] + "...") if cfg["service_key"] else None,
    }

    if not cfg["url"] or not cfg["service_key"]:
        out["ok"] = False
        out["error"] = (
            "Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY. "
            f"Copy supabase/env.example -> {ENV_PATH.name} and fill values."
        )
        print(json.dumps(out, indent=2))
        return 1

    url = f"{cfg['url']}/rest/v1/signals?select=signal_id&limit=1"
    req = urllib.request.Request(
        url,
        headers={
            "apikey": cfg["service_key"],
            "Authorization": f"Bearer {cfg['service_key']}",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            out["ok"] = True
            out["http_status"] = resp.status
            out["sample"] = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        out["ok"] = False
        out["http_status"] = exc.code
        out["error"] = exc.read().decode(errors="replace")[:300]
    except urllib.error.URLError as exc:
        out["ok"] = False
        out["error"] = f"Could not resolve host / network: {exc.reason}"

    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0 if out.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
