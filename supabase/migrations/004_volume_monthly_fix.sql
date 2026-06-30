-- Fix volume_monthly.required_daily_pace null on last day of month

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
  case
    when greatest(0, c.days_in_month - c.trading_days_passed) = 0 then 0
    else round(
      (p.target_lots - c.current_lots)
        / greatest(1, c.days_in_month - c.trading_days_passed),
      2
    )
  end as required_daily_pace,
  round(c.current_lots / nullif(c.trading_days_passed, 0), 2) as actual_daily_pace,
  round(
    (c.current_lots / nullif(c.trading_days_passed, 0)) * c.days_in_month,
    2
  ) as projected_month_end_lots
from calendar c
cross join params p
order by c.month desc;
