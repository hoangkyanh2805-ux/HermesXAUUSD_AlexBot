"""Signal Replay / Forward Test — quality gate (video backtest equivalent)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.common import REPO_ROOT, data_path, load_json, save_json

DEFAULT_GATE = {
    "min_win_rate": 0.55,
    "min_avg_r": 1.5,
    "max_drawdown": 0.15,
    "min_sample_size": 20,
}


def _replay_file(setup_name: str) -> Path:
    return data_path(f"replay/{setup_name}.json")


def _load_gate_config() -> dict:
    cfg_path = REPO_ROOT / "strategy-rooms" / "signal-room" / "config.yaml"
    if not cfg_path.exists():
        return DEFAULT_GATE.copy()
    # Minimal YAML parse for replay_gate block
    gate = DEFAULT_GATE.copy()
    in_gate = False
    for line in cfg_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("replay_gate:"):
            in_gate = True
            continue
        if in_gate:
            if not stripped or not stripped.startswith(" " * 2) and ":" in stripped and not stripped.startswith(" "):
                if not stripped.startswith("min_") and not stripped.startswith("max_"):
                    break
            if "min_win_rate:" in stripped:
                gate["min_win_rate"] = float(stripped.split(":")[1].strip())
            elif "min_avg_r:" in stripped:
                gate["min_avg_r"] = float(stripped.split(":")[1].strip())
            elif "max_drawdown:" in stripped:
                gate["max_drawdown"] = float(stripped.split(":")[1].strip())
            elif "min_sample_size:" in stripped:
                gate["min_sample_size"] = int(stripped.split(":")[1].strip())
    return gate


def _max_drawdown_rs(r_values: list[float]) -> float:
    peak = 0.0
    cumulative = 0.0
    max_dd = 0.0
    for r in r_values:
        cumulative += r
        peak = max(peak, cumulative)
        if peak > 0:
            max_dd = max(max_dd, (peak - cumulative) / peak)
    return round(max_dd, 4)


def replay_signals(
    setup_name: str,
    dataset_path: Path | None = None,
    gate: dict | None = None,
) -> dict[str, Any]:
    """
    Replay historical signals for a setup.
    Returns win_rate, avg_r, max_dd, pass, trades, reasons.
    """
    gate = gate or _load_gate_config()
    path = dataset_path or _replay_file(setup_name)

    if not path.exists():
        return {
            "ok": False,
            "setup_name": setup_name,
            "pass": False,
            "error": f"Replay dataset not found: {path}",
        }

    data = load_json(path, {"signals": []})
    signals = data.get("signals", [])
    n = len(signals)

    if n < gate["min_sample_size"]:
        return {
            "ok": True,
            "setup_name": setup_name,
            "pass": False,
            "trades": n,
            "win_rate": 0.0,
            "avg_r": 0.0,
            "max_dd": 0.0,
            "reasons": [f"Sample size {n} < minimum {gate['min_sample_size']}"],
            "suggested_action": "Add more historical signals to replay dataset.",
        }

    wins = sum(1 for s in signals if s.get("result") == "win")
    r_values = [float(s.get("r", 0)) for s in signals]
    win_rate = wins / n
    avg_r = sum(r_values) / n
    max_dd = _max_drawdown_rs(r_values)

    reasons: list[str] = []
    passed = True

    if win_rate < gate["min_win_rate"]:
        passed = False
        reasons.append(f"Win rate {win_rate:.2%} < {gate['min_win_rate']:.0%}")
    else:
        reasons.append(f"Win rate {win_rate:.2%} OK")

    if avg_r < gate["min_avg_r"]:
        passed = False
        reasons.append(f"Avg R {avg_r:.2f} < {gate['min_avg_r']}")
    else:
        reasons.append(f"Avg R {avg_r:.2f} OK")

    if max_dd > gate["max_drawdown"]:
        passed = False
        reasons.append(f"Max drawdown {max_dd:.2%} > {gate['max_drawdown']:.0%}")
    else:
        reasons.append(f"Max drawdown {max_dd:.2%} OK")

    result = {
        "ok": True,
        "setup_name": setup_name,
        "pass": passed,
        "trades": n,
        "wins": wins,
        "losses": n - wins,
        "win_rate": round(win_rate, 4),
        "avg_r": round(avg_r, 4),
        "max_dd": max_dd,
        "gate": gate,
        "reasons": reasons,
        "suggested_action": (
            "Promote setup to replay_passed then forward_test."
            if passed
            else "Do not promote — improve setup or gather more data."
        ),
    }

    # Persist latest replay result
    out_dir = REPO_ROOT / "strategy-rooms" / "signal-room" / "replay"
    out_dir.mkdir(parents=True, exist_ok=True)
    save_json(out_dir / "latest.json", result)
    save_json(out_dir / f"{setup_name}-latest.json", result)

    return result


def get_setup_status(setup_name: str) -> str:
    setups = load_json(data_path("setups.json"), {"setups": {}})
    return setups.get("setups", {}).get(setup_name, {}).get("status", "draft")


def promote_setup(setup_name: str, new_status: str) -> dict[str, Any]:
    allowed = ("draft", "replay_passed", "forward_test", "live")
    if new_status not in allowed:
        return {"ok": False, "error": f"Invalid status. Use one of: {allowed}"}

    store = load_json(data_path("setups.json"), {"setups": {}})
    store.setdefault("setups", {})
    entry = store["setups"].setdefault(setup_name, {})
    entry["status"] = new_status
    save_json(data_path("setups.json"), store)
    return {"ok": True, "setup_name": setup_name, "status": new_status}
