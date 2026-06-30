"""Load desk configuration from strategy-rooms YAML (stdlib only)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.common import REPO_ROOT, load_json

MARKET_CONFIG_PATH = REPO_ROOT / "strategy-rooms" / "market-room" / "config.yaml"

DEFAULTS: dict[str, Any] = {
    "spread_threshold_pts": 30.0,
    "slippage_tolerance_pts": 5.0,
    "floating_risk_cap_pct": 3.0,
    "daily_drawdown_cap_pct": 3.0,
    "max_trades_per_day": 5,
    "volume_kpi_monthly_lots": 200,
    "xauusd_value_per_point_per_0_01_lot": 0.1,
    "correlation_reduce_risk_multiplier": 0.5,
}


def _parse_simple_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    out: dict[str, Any] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        if line.startswith("-") or line.endswith(":"):
            continue
        key, _, raw = line.partition(":")
        key = key.strip()
        raw = raw.strip().split("#", 1)[0].strip()
        if not raw:
            continue
        if raw.lower() in ("true", "false"):
            out[key] = raw.lower() == "true"
        else:
            try:
                out[key] = float(raw) if "." in raw else int(raw)
            except ValueError:
                out[key] = raw.strip('"').strip("'")
    return out


def load_market_config() -> dict[str, Any]:
    cfg = dict(DEFAULTS)
    cfg.update(_parse_simple_yaml(MARKET_CONFIG_PATH))
    return cfg


def load_client_rules() -> dict[str, Any]:
    return load_json(REPO_ROOT / "data" / "client_groups.json", {"groups": {}, "rules": {}})
