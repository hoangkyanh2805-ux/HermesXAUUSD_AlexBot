-- Hermes XAUUSD IB Desk — Reporting & Audit schema (Supabase)
-- Phase 2+: sync from local JSON pipeline or direct inserts
-- Metabase Phase 4–5: connect to these tables/views

-- =============================================================================
-- CORE TABLES
-- =============================================================================

create table if not exists signals (
  id uuid primary key default gen_random_uuid(),
  signal_id text unique not null,
  created_at timestamptz not null default now(),
  pair text not null default 'XAUUSD',
  direction text not null check (direction in ('buy', 'sell')),
  entry_low numeric not null,
  entry_high numeric not null,
  stop_loss numeric not null,
  take_profits jsonb not null default '[]',
  session text,
  market_bias text,
  news_risk text,
  dxy_direction text,
  us10y_direction text,
  correlation_risk_tag text,
  setup_name text,
  status text not null default 'draft',
  decision text,
  reason text,
  suggested_action text
);

create table if not exists trades (
  id uuid primary key default gen_random_uuid(),
  signal_id text not null references signals(signal_id),
  opened_at timestamptz,
  closed_at timestamptz,
  pair text not null default 'XAUUSD',
  direction text not null,
  entry_price numeric,
  close_price numeric,
  stop_loss numeric,
  take_profit_hit text,
  result text check (result in ('win', 'loss', 'breakeven')),
  lot_total numeric not null default 0,
  lot_parts jsonb,
  client_group text,
  risk_tier text,
  risk_percent numeric,
  pnl numeric default 0,
  rr numeric,
  session text,
  setup_type text
);

create table if not exists activity_logs (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  signal_id text,
  trade_id uuid references trades(id),
  event_type text not null check (event_type in (
    'SIGNAL_SEEDED', 'SIGNAL_APPROVED', 'SIGNAL_WAITING', 'SIGNAL_REJECTED',
    'ENTRY_TRIGGERED', 'SPREAD_WARNING', 'PENDING_CANCELLED',
    'TP1_HIT', 'TP2_HIT', 'SL_HIT', 'TRADE_CLOSED', 'JOURNAL_UPDATED'
  )),
  event_note text,
  spread_value numeric,
  price numeric,
  status_before text,
  status_after text
);

create table if not exists risk_audit (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  signal_id text,
  trade_id uuid references trades(id),
  equity numeric,
  risk_percent numeric,
  floating_risk_percent numeric,
  daily_drawdown_percent numeric,
  max_allowed_risk_percent numeric,
  risk_status text check (risk_status in (
    'OK', 'REDUCE_RISK', 'BLOCK_NEW_TRADE', 'DAILY_LOSS_LOCK', 'FLOATING_RISK_LOCK'
  )),
  action_taken text
);

create table if not exists spread_audit (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  signal_id text not null,
  trade_id uuid references trades(id),
  spread_seed numeric,
  spread_entry numeric,
  spread_close numeric,
  max_spread numeric,
  spread_threshold numeric,
  spread_status text check (spread_status in (
    'NORMAL', 'WARNING', 'HIGH_SPREAD_RISK', 'PENDING_CANCELLED'
  )),
  action_taken text
);

-- =============================================================================
-- VIEWS — VOLUME AGGREGATES
-- =============================================================================

create or replace view volume_daily as
select
  date_trunc('day', closed_at)::date as date,
  coalesce(sum(lot_total), 0) as total_lots,
  count(*) as total_trades,
  coalesce(avg(lot_total), 0) as average_lot,
  count(*) filter (where result = 'win') as win_count,
  count(*) filter (where result = 'loss') as loss_count,
  count(*) filter (where result = 'breakeven') as breakeven_count
from trades
where closed_at is not null
group by 1
order by 1 desc;

create or replace view volume_weekly as
select
  date_trunc('week', closed_at)::date as week_start,
  coalesce(sum(lot_total), 0) as total_lots,
  count(*) as total_trades,
  coalesce(avg(lot_total), 0) as average_lot
from trades
where closed_at is not null
group by 1
order by 1 desc;

create or replace view volume_monthly as
with params as (
  select 200::numeric as target_lots
),
month_stats as (
  select
    date_trunc('month', closed_at) as month,
    coalesce(sum(lot_total), 0) as current_lots,
    count(*) as total_trades
  from trades
  where closed_at is not null
  group by 1
),
calendar as (
  select
    m.month,
    m.current_lots,
    m.total_trades,
    extract(day from (m.month + interval '1 month - 1 day'))::int as days_in_month,
    greatest(1, extract(day from least(now(), m.month + interval '1 month - 1 day') - m.month) + 1)::int as trading_days_passed
  from month_stats m
)
select
  c.month,
  p.target_lots,
  c.current_lots,
  round(c.current_lots / p.target_lots * 100, 2) as progress_percent,
  round(p.target_lots - c.current_lots, 2) as remaining_lots,
  c.trading_days_passed,
  greatest(0, c.days_in_month - c.trading_days_passed) as trading_days_remaining,
  round(
    (p.target_lots - c.current_lots) / nullif(c.days_in_month - c.trading_days_passed, 0),
    2
  ) as required_daily_pace,
  round(c.current_lots / nullif(c.trading_days_passed, 0), 2) as actual_daily_pace,
  round(
    (c.current_lots / nullif(c.trading_days_passed, 0)) * c.days_in_month,
    2
  ) as projected_month_end_lots
from calendar c
cross join params p
order by c.month desc;

-- =============================================================================
-- INDEXES
-- =============================================================================

create index if not exists idx_trades_closed_at on trades(closed_at);
create index if not exists idx_trades_signal_id on trades(signal_id);
create unique index if not exists idx_trades_signal_unique on trades(signal_id);
create index if not exists idx_activity_logs_signal on activity_logs(signal_id);
create index if not exists idx_spread_audit_signal on spread_audit(signal_id);
create unique index if not exists idx_spread_audit_signal_unique on spread_audit(signal_id);
