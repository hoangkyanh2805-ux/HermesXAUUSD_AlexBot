-- Hermes XAUUSD IB Desk — Metabase SQL cards (Phase 5)
-- Database: Supabase PostgreSQL (Hermes XAUUSD Supabase)
-- G10: volume KPI is display-only — not a trading trigger

-- =============================================================================
-- CARD 01 — Monthly Volume Progress Gauge
-- Viz: Gauge or Progress bar (0–100)
-- =============================================================================
select
  progress_percent,
  current_lots,
  target_lots
from volume_monthly
order by month desc
limit 1;

-- =============================================================================
-- CARD 02 — Daily Lots Bar Chart
-- Viz: Bar chart — X: date, Y: total_lots
-- =============================================================================
select
  date,
  total_lots,
  total_trades,
  win_count,
  loss_count,
  breakeven_count
from volume_daily
order by date desc
limit 30;

-- =============================================================================
-- CARD 03 — Weekly Lots Trend
-- Viz: Line chart — X: week_start, Y: total_lots
-- =============================================================================
select
  week_start,
  total_lots,
  total_trades,
  average_lot
from volume_weekly
order by week_start desc
limit 12;

-- =============================================================================
-- CARD 04 — Monthly vs 200 Target
-- Viz: Bar chart (grouped) — current_lots vs target_lots
-- =============================================================================
select
  month,
  current_lots,
  target_lots,
  progress_percent
from volume_monthly
order by month desc
limit 6;

-- =============================================================================
-- CARD 05 — Remaining Lots
-- Viz: Number / Scalar
-- =============================================================================
select remaining_lots
from volume_monthly
order by month desc
limit 1;

-- =============================================================================
-- CARD 06 — Required Daily Pace
-- Viz: Number / Scalar
-- =============================================================================
select required_daily_pace
from volume_monthly
order by month desc
limit 1;

-- =============================================================================
-- CARD 07 — Projected Month-End Lots
-- Viz: Number / Scalar
-- =============================================================================
select projected_month_end_lots
from volume_monthly
order by month desc
limit 1;

-- =============================================================================
-- CARD 08 — Volume by Session
-- Viz: Bar chart
-- =============================================================================
select
  coalesce(session, 'unknown') as session,
  sum(lot_total) as total_lots,
  count(*) as trade_count
from trades
where closed_at is not null
group by 1
order by total_lots desc;

-- =============================================================================
-- CARD 09 — Volume by Client Group
-- Viz: Pie or bar
-- =============================================================================
select
  coalesce(client_group, 'unknown') as client_group,
  sum(lot_total) as total_lots,
  count(*) as trade_count
from trades
where closed_at is not null
group by 1
order by total_lots desc;

-- =============================================================================
-- CARD 10 — Volume by Risk Tier
-- Viz: Pie or bar
-- =============================================================================
select
  coalesce(risk_tier, 'unknown') as risk_tier,
  sum(lot_total) as total_lots,
  count(*) as trade_count
from trades
where closed_at is not null
group by 1
order by total_lots desc;

-- =============================================================================
-- CARD 11 — Risk vs Volume (latest snapshot)
-- Viz: Table
-- =============================================================================
select
  r.created_at,
  r.equity,
  r.floating_risk_percent,
  r.daily_drawdown_percent,
  r.risk_status,
  r.action_taken,
  coalesce(
    (select sum(lot_total) from trades where closed_at::date = r.created_at::date),
    0
  ) as lots_closed_today
from risk_audit r
order by r.created_at desc
limit 10;

-- =============================================================================
-- CARD 12 — Drawdown over time
-- Viz: Line chart — X: created_at, Y: daily_drawdown_percent
-- =============================================================================
select
  created_at,
  daily_drawdown_percent,
  floating_risk_percent,
  risk_status
from risk_audit
order by created_at desc
limit 90;

-- =============================================================================
-- CARD 13 — Spread warning count
-- Viz: Number / Scalar
-- =============================================================================
select count(*) as warning_count
from spread_audit
where spread_status in ('WARNING', 'HIGH_SPREAD_RISK');

-- =============================================================================
-- CARD 14 — Avg spread by session
-- Viz: Bar chart
-- =============================================================================
select
  coalesce(s.session, 'unknown') as session,
  round(avg(sa.spread_seed), 2) as avg_spread_seed,
  round(avg(sa.spread_entry), 2) as avg_spread_entry,
  round(avg(sa.spread_close), 2) as avg_spread_close,
  count(*) as signal_count
from spread_audit sa
left join signals s on s.signal_id = sa.signal_id
group by 1
order by avg_spread_entry desc nulls last;

-- =============================================================================
-- CARD 15 — Signal decisions (Approved / Waiting / Rejected)
-- Viz: Pie chart
-- =============================================================================
select
  event_type,
  count(*) as event_count
from activity_logs
where event_type in (
  'SIGNAL_APPROVED', 'SIGNAL_WAITING', 'SIGNAL_REJECTED'
)
group by 1
order by event_count desc;

-- =============================================================================
-- CARD 16 — Win / Loss / Breakeven
-- Viz: Pie chart
-- =============================================================================
select
  result,
  count(*) as trade_count,
  round(sum(pnl), 2) as total_pnl
from trades
where result is not null
group by 1
order by trade_count desc;

-- =============================================================================
-- CARD 17 — Event type breakdown (TP/SL / lifecycle)
-- Viz: Bar chart
-- =============================================================================
select
  event_type,
  count(*) as event_count
from activity_logs
group by 1
order by event_count desc;

-- =============================================================================
-- CARD 18 — Correlation risk outcomes
-- Viz: Bar chart
-- =============================================================================
select
  coalesce(correlation_risk_tag, 'none') as correlation_risk_tag,
  decision,
  count(*) as signal_count
from signals
where correlation_risk_tag is not null or decision is not null
group by 1, 2
order by signal_count desc;

-- =============================================================================
-- CARD 19 — Blocked trades by reason
-- Viz: Bar chart
-- =============================================================================
select
  coalesce(action_taken, 'none') as action_taken,
  risk_status,
  count(*) as audit_count
from risk_audit
where action_taken is not null
  and action_taken != 'snapshot'
group by 1, 2
order by audit_count desc;

-- =============================================================================
-- CARD 20 — IB Commission estimate (DISPLAY ONLY — edit rate below)
-- Viz: Number / Scalar
-- Default: $8 per lot — adjust to your IB rebate
-- =============================================================================
select
  round(coalesce(sum(lot_total), 0) * 8, 2) as estimated_commission_usd,
  coalesce(sum(lot_total), 0) as total_lots
from trades
where closed_at >= date_trunc('month', now());

-- =============================================================================
-- CARD 21 — Correlation risk alerts (24h) — RED ALERT TABLE
-- Viz: Table — recent CORRELATION_RISK events
-- =============================================================================
select
  signal_id,
  event_note,
  status_after as gate_decision,
  created_at
from activity_logs
where event_type = 'CORRELATION_RISK'
  and created_at >= now() - interval '24 hours'
order by created_at desc
limit 20;

-- =============================================================================
-- CARD 22 — Correlation risk count (24h) — RED ALERT SCALAR
-- Viz: Number / Scalar — pin top of dashboard
-- =============================================================================
select count(*) as correlation_risk_alerts_24h
from activity_logs
where event_type = 'CORRELATION_RISK'
  and created_at >= now() - interval '24 hours';
