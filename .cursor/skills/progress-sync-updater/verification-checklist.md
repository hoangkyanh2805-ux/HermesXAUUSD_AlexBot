# Progress Sync — Verification Checklist

Use during Step 2 of `progress-sync-updater`. Record evidence for each row.

Legend: ✅ DONE | ⚠️ PARTIAL | ❌ MISSING | ❓ UNVERIFIED (claimed only)

---

## 1. Supabase direct sync

| Check | How to verify | Evidence to cite |
|-------|---------------|------------------|
| Batch sync module | Read `src/supabase_sync.py` — `sync_all`, `build_sync_payloads`, `_postgrest_upsert` | Function names |
| CLI dry-run | `python scripts/sync_to_supabase.py --dry-run` | Exit 0, counts |
| MCP tool | `mcp/xauusd-trading/server.py` — `sync_supabase` | Tool name |
| Per-step writes on `create_signal` | Grep `create_signal` → direct insert or `sync_signal` hook | File:line |
| Per-step writes on `check_signal` | Grep `_cmd_check_signal` | |
| Per-step writes on `calc_lot` | Grep `_cmd_calc_lot` | |
| Per-step writes on `seed_signal` | Grep `_cmd_seed_signal` | |
| Per-step writes on `publish_signal` | Grep `_cmd_publish_signal` | |
| Per-step writes on `close_signal` | Grep `_cmd_close_signal` | |
| `maybe_sync_after_pipeline` | Only on `export_state()`? | `src/dashboard.py` |
| Live sync tested | `supabase/.env` + sync exit ok | Operator log or ❓ |
| Production-ready label | All pipeline steps + `sig-test-001` rows in DB | |

**Verdict rule:** MCP + batch sync = ⚠️ PARTIAL until per-step or E2E `sig-test-001` verified.

---

## 2. Signals table structure

Compare `supabase/schema.sql` `signals` vs brief fields:

| Field | In schema? | In sync payload? | In local JSON? |
|-------|------------|------------------|----------------|
| signal_id, pair, direction, entry_*, stop_loss, take_profits | | | |
| session, market_bias, news_risk | | | |
| dxy_direction, us10y_direction | | | |
| dxy_context, us10y_context | | | |
| correlation_risk_tag | | | |
| spread_seed (or spread_audit only) | | | |
| status, reason, suggested_action, decision | | | |

Read `src/supabase_sync.py::_signal_row` for sync mapping.

---

## 3. Activity logs

| Check | How to verify |
|-------|---------------|
| Schema event types | `supabase/schema.sql` activity_logs CHECK |
| Brief event types (SIGNAL_CREATED, LOT_CALCULATED, …) | Grep codebase |
| Emitted on create | Grep `SIGNAL_CREATED` or emitter module |
| Emitted on check | Gate → audit path |
| Emitted on lot calc | |
| Emitted on seed | |
| Emitted on publish | |
| Emitted on close / journal | |
| `payload` column | Schema + writer |
| Sync to Supabase | `_activity_rows` or direct insert |

---

## 4. DXY / US10Y market context

| Check | How to verify |
|-------|---------------|
| `src/market_context.py` exists | |
| `source` field (mock vs live) | Grep `source` |
| Live API / Yahoo / feed | Grep fetch/http |
| Defaults only (neutral, spread 28) | Read `get_market_context` |
| Written to `market_context.json` | `write_market_context` usage |
| Passed into `check_signal` | `telegram_router._cmd_check_signal` |

---

## 5. Correlation filter (`check_signal`)

| Check | How to verify |
|-------|---------------|
| `APPROVE` / `WAIT` / `REJECT` / `REDUCE_RISK` | `src/signal_gate.py` |
| BUY + DXY bullish → high risk | Test or `_correlation_severity` |
| SELL + DXY bearish → high risk | |
| Does not auto-reject all conflicts | Read gate logic |
| Tests | `tests/test_signal_gate.py`, `tests/test_phase_d.py` |

---

## 6. Spread guard

| Check | How to verify |
|-------|---------------|
| `src/spread_guard.py` | File exists? |
| Record seed / entry / close spread | `src/spread_audit.py` |
| Threshold from config | `desk_config` / `spread_threshold_pts` |
| High spread → WAIT / CANCEL_PENDING | `safety_locks.py` |
| `SPREAD_WARNING` activity | Grep |
| `spread_audit` Supabase rows | sync or direct write |
| Slippage detection | Grep slippage |

---

## 7. Risk-first lot calculator

| Check | How to verify |
|-------|---------------|
| Formula `(Equity × Risk%) / (SL × value/pt)` | `calculate_lot` |
| Blocks martingale / recovery | `is_recovery_request`, blocks |
| Blocks missing SL | |
| Floating risk cap | config + calculator/router |
| Tests | `tests/test_lot_calculator.py` |

---

## 8. Multi-entry (unchanged total risk)

| Check | How to verify |
|-------|---------------|
| `split_entries` sum validation | `src/multi_entry.py` |
| MCP `/split_entries` | `server.py` |
| `calc_lot` outputs entry_parts | |
| Persisted to journal / trades.lot_parts | |
| Tests | `test_multi_entry_sum_matches` |

---

## 9. Volume dashboard reporting

| Check | How to verify |
|-------|---------------|
| `volume_tracker.py` daily/weekly/monthly | |
| KPI 200 progress | `volume_monthly` view / tracker |
| `reporting_audit.py` warnings | |
| Dashboard HTML sections | `dashboard/ib-signals/index.html` |
| Metabase cards SQL | `metabase/cards.sql` |
| G10 guardrail doc | `docs/guardrails.md` |
| No trade logic tied to KPI | Grep volume → publish/lot triggers |

---

## 10. 200 lots/month KPI (reporting only)

| Check | How to verify |
|-------|---------------|
| Documented as display-only | G10, SOP, progress report |
| No code path: low KPI → increase lot | Grep `required_daily_pace` misuse |
| Metabase / dashboard labels | |

---

## 11. End-to-end `sig-test-001`

| Check | How to verify |
|-------|---------------|
| Fixture `sig-test-001` in tests or script | Grep |
| Sequence create → check → lot → seed → publish | Test or workbook |
| Supabase rows after flow | SQL or dry_run payloads |
| `publish_signal(dry_run=True)` if required | Grep dry_run on publish |
| `python tests/run_tests.py` pass | Run if safe |

---

## Evidence log template

```markdown
| Claim | Evidence | Verdict |
|-------|----------|---------|
| Supabase production-ready | only sync_supabase MCP | ❓ UNVERIFIED |
| check_signal correlation | signal_gate.py + test_phase_d | ✅ DONE |
```
