-- Metabase smoke SQL — run in Supabase SQL Editor or Metabase SQL question
-- Phase 5 operator verify

select 'signals' as tbl, count(*)::int as rows from signals
union all
select 'activity_logs', count(*)::int from activity_logs
union all
select 'spread_audit', count(*)::int from spread_audit
union all
select 'risk_audit', count(*)::int from risk_audit;

-- sig-test-001 rows (after run_sig_test_001 --live)
select signal_id, status, decision, correlation_risk_tag, correlation_data
from signals where signal_id = 'sig-test-001';

select event_type, event_note, created_at
from activity_logs
where signal_id = 'sig-test-001'
order by created_at;

-- Volume KPI (G10 display-only)
select progress_percent, current_lots, target_lots, required_daily_pace
from volume_monthly
order by month desc
limit 1;
