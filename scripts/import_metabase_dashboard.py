#!/usr/bin/env python3
"""Import Metabase dashboard from metabase/cards.sql via REST API."""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARDS_SQL = ROOT / "metabase" / "cards.sql"
ENV_PATH = ROOT / "metabase" / ".env"

CARD_META: dict[int, dict[str, str]] = {
    1: {"name": "Monthly Volume Progress", "display": "gauge"},
    2: {"name": "Daily Lots", "display": "bar"},
    3: {"name": "Weekly Lots Trend", "display": "line"},
    4: {"name": "Monthly vs 200 Target", "display": "bar"},
    5: {"name": "Remaining Lots", "display": "scalar"},
    6: {"name": "Required Daily Pace", "display": "scalar"},
    7: {"name": "Projected Month-End Lots", "display": "scalar"},
    8: {"name": "Volume by Session", "display": "bar"},
    9: {"name": "Volume by Client Group", "display": "pie"},
    10: {"name": "Volume by Risk Tier", "display": "pie"},
    11: {"name": "Risk vs Volume (latest)", "display": "table"},
    12: {"name": "Drawdown over time", "display": "line"},
    13: {"name": "Spread warning count", "display": "scalar"},
    14: {"name": "Avg spread by session", "display": "bar"},
    15: {"name": "Signal decisions", "display": "pie"},
    16: {"name": "Win / Loss / Breakeven", "display": "pie"},
    17: {"name": "Event type breakdown", "display": "bar"},
    18: {"name": "Correlation risk outcomes", "display": "bar"},
    19: {"name": "Blocked trades by reason", "display": "bar"},
    20: {"name": "IB Commission estimate", "display": "scalar"},
}


def load_env() -> dict[str, str]:
    env: dict[str, str] = {}
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    defaults = {
        "METABASE_URL": "http://localhost:3000",
        "METABASE_DATABASE_NAME": "Hermes Supabase",
        "COLLECTION_NAME": "Hermes XAUUSD IB Desk",
        "DASHBOARD_NAME": "Hermes XAUUSD IB Desk",
    }
    for key in (
        "METABASE_URL",
        "METABASE_EMAIL",
        "METABASE_PASSWORD",
        "METABASE_DATABASE_NAME",
        "COLLECTION_NAME",
        "DASHBOARD_NAME",
    ):
        env[key] = os.environ.get(key) or env.get(key) or defaults.get(key, "")
    return env


class MetabaseClient:
    def __init__(self, base_url: str, session_id: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.session_id = session_id

    @classmethod
    def login(cls, base_url: str, email: str, password: str) -> MetabaseClient:
        data = json.dumps({"username": email, "password": password}).encode("utf-8")
        req = urllib.request.Request(
            f"{base_url.rstrip('/')}/api/session",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        return cls(base_url, payload["id"])

    def _request(self, method: str, path: str, body: dict | None = None) -> Any:
        url = f"{self.base_url}{path}"
        data = None
        headers = {
            "Content-Type": "application/json",
            "X-Metabase-Session": self.session_id,
        }
        if body is not None:
            data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")
            raise RuntimeError(f"{method} {path} HTTP {e.code}: {detail[:500]}") from e

    def get_database_id(self, name: str) -> int:
        dbs = self._request("GET", "/api/database")
        data = dbs.get("data", dbs if isinstance(dbs, list) else [])
        target = name.lower().replace(" ", "")
        for db in data:
            if db.get("name", "").lower().replace(" ", "") == target:
                return int(db["id"])
        for db in data:
            n = db.get("name", "").lower()
            if "hermes" in n and "supabase" in n:
                return int(db["id"])
        names = [d.get("name") for d in data]
        raise RuntimeError(f"Database '{name}' not found. Available: {names}")

    def get_or_create_collection(self, name: str) -> int:
        tree = self._request("GET", "/api/collection/tree")
        for node in _walk_collections(tree):
            if node.get("name") == name and node.get("id"):
                return int(node["id"])
        created = self._request("POST", "/api/collection", {"name": name, "color": "#509EE3"})
        return int(created["id"])

    def get_or_create_card(
        self,
        *,
        name: str,
        sql: str,
        display: str,
        database_id: int,
        collection_id: int,
    ) -> int:
        items = self._request("GET", f"/api/collection/{collection_id}/items")
        for item in items.get("data", []):
            if item.get("model") == "card" and item.get("name") == name:
                return int(item["id"])
        body = {
            "name": name,
            "display": display,
            "collection_id": collection_id,
            "dataset_query": {
                "database": database_id,
                "type": "native",
                "native": {"query": sql.strip()},
            },
            "visualization_settings": {},
        }
        created = self._request("POST", "/api/card", body)
        return int(created["id"])

    def get_or_create_dashboard(self, name: str, collection_id: int) -> int:
        dashboards = self._request("GET", "/api/dashboard")
        for dash in dashboards:
            if dash.get("name") == name:
                return int(dash["id"])
        created = self._request(
            "POST",
            "/api/dashboard",
            {
                "name": name,
                "collection_id": collection_id,
                "description": "G10: Volume KPI reporting only — not a trading trigger.",
            },
        )
        return int(created["id"])

    def set_dashboard_cards(self, dashboard_id: int, card_ids: list[int]) -> None:
        cards = []
        col = 0
        row = 0
        for i, cid in enumerate(card_ids):
            if i > 0 and i % 4 == 0:
                row += 4
                col = 0
            cards.append(
                {
                    "id": -1 - i,
                    "card_id": cid,
                    "row": row,
                    "col": col,
                    "size_x": 6,
                    "size_y": 4,
                }
            )
            col += 6
            if col >= 12:
                col = 0
                row += 4
        self._request("PUT", f"/api/dashboard/{dashboard_id}/cards", {"cards": cards})


def _walk_collections(nodes: list) -> list[dict]:
    out: list[dict] = []
    for node in nodes:
        out.append(node)
        out.extend(_walk_collections(node.get("children", [])))
    return out


def parse_cards_sql(path: Path) -> dict[int, str]:
    text = path.read_text(encoding="utf-8")
    blocks = re.findall(
        r"-- CARD (\d+).*?\n(.*?)(?=\n-- =+\n-- CARD |\Z)",
        text,
        re.DOTALL,
    )
    cards: dict[int, str] = {}
    for num_s, block in blocks:
        lines = [
            ln
            for ln in block.splitlines()
            if not ln.strip().startswith("--") and ln.strip()
        ]
        sql = "\n".join(lines).strip()
        if sql:
            cards[int(num_s)] = sql
    return cards


def main() -> int:
    env = load_env()
    email = env.get("METABASE_EMAIL", "")
    password = env.get("METABASE_PASSWORD", "")
    if not email or not password:
        print(
            "Missing METABASE_EMAIL or METABASE_PASSWORD.\n"
            f"Copy metabase/env.example -> metabase/.env and fill credentials."
        )
        return 1

    cards_sql = parse_cards_sql(CARDS_SQL)
    if len(cards_sql) < 20:
        print(f"Warning: parsed {len(cards_sql)} cards from cards.sql")

    client = MetabaseClient.login(env["METABASE_URL"], email, password)
    db_id = client.get_database_id(env["METABASE_DATABASE_NAME"])
    collection_id = client.get_or_create_collection(env["COLLECTION_NAME"])

    card_ids: list[int] = []
    for num in sorted(cards_sql):
        meta = CARD_META.get(num, {"name": f"Card {num:02d}", "display": "table"})
        cid = client.get_or_create_card(
            name=meta["name"],
            sql=cards_sql[num],
            display=meta["display"],
            database_id=db_id,
            collection_id=collection_id,
        )
        card_ids.append(cid)
        print(f"OK card {num:02d}: {meta['name']} (id={cid})")

    dash_id = client.get_or_create_dashboard(env["DASHBOARD_NAME"], collection_id)
    client.set_dashboard_cards(dash_id, card_ids)

    url = f"{env['METABASE_URL']}/dashboard/{dash_id}"
    print(json.dumps({"ok": True, "dashboard_id": dash_id, "url": url, "cards": len(card_ids)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
