#!/usr/bin/env python3
"""Print Phase G migration SQL for Supabase SQL Editor."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sql = (ROOT / "supabase" / "migrations" / "002_phase_g.sql").read_text(encoding="utf-8")
print("Run in Supabase Dashboard -> SQL Editor -> New query:\n")
print(sql)
