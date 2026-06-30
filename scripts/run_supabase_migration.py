#!/usr/bin/env python3
"""Run a SQL migration file against Supabase PostgreSQL (Session pooler)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.supabase_sync import load_env_file

ENV_PATH = ROOT / "supabase" / ".env"
DEFAULT_HOST = "aws-1-ap-south-1.pooler.supabase.com"
DEFAULT_USER = "postgres.tikouskusgdygktslmzj"


def _db_config() -> dict[str, str]:
    env = load_env_file(ENV_PATH)
    url = os.environ.get("SUPABASE_URL") or env.get("SUPABASE_URL", "")
    ref = url.rstrip("/").split(".")[0].split("//")[-1] if url else "tikouskusgdygktslmzj"
    return {
        "host": os.environ.get("SUPABASE_DB_HOST") or env.get("SUPABASE_DB_HOST", DEFAULT_HOST),
        "port": int(os.environ.get("SUPABASE_DB_PORT") or env.get("SUPABASE_DB_PORT", "5432")),
        "dbname": os.environ.get("SUPABASE_DB_NAME") or env.get("SUPABASE_DB_NAME", "postgres"),
        "user": os.environ.get("SUPABASE_DB_USER") or env.get("SUPABASE_DB_USER", f"postgres.{ref}"),
        "password": os.environ.get("SUPABASE_DB_PASSWORD") or env.get("SUPABASE_DB_PASSWORD", ""),
    }


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python scripts/run_supabase_migration.py <migration.sql>")
        return 1

    sql_path = Path(sys.argv[1])
    if not sql_path.is_absolute():
        sql_path = ROOT / sql_path
    if not sql_path.exists():
        print(f"File not found: {sql_path}")
        return 1

    cfg = _db_config()
    if not cfg["password"]:
        print(
            "Missing SUPABASE_DB_PASSWORD in supabase/.env\n"
            "(Database password from Supabase Connect — not the API secret key.)"
        )
        return 1

    try:
        import psycopg2
    except ImportError:
        print("Install psycopg2-binary: pip install psycopg2-binary")
        return 1

    sql = sql_path.read_text(encoding="utf-8")
    conn = psycopg2.connect(
        host=cfg["host"],
        port=cfg["port"],
        dbname=cfg["dbname"],
        user=cfg["user"],
        password=cfg["password"],
        sslmode="require",
        connect_timeout=30,
    )
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
        print(f"Applied: {sql_path.relative_to(ROOT)}")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
