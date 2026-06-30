-- Phase F migration — run in Supabase SQL Editor on existing projects
-- New installs: fields are already in schema.sql

alter table signals add column if not exists dxy_context jsonb;
alter table signals add column if not exists us10y_context jsonb;
alter table signals add column if not exists spread_log jsonb;

alter table activity_logs add column if not exists payload jsonb;

alter table activity_logs drop constraint if exists activity_logs_event_type_check;
alter table activity_logs add constraint activity_logs_event_type_check check (event_type in (
  'SIGNAL_CREATED', 'SIGNAL_CHECKED', 'SIGNAL_SEEDED', 'SIGNAL_PUBLISHED',
  'LOT_CALCULATED', 'SIGNAL_APPROVED', 'SIGNAL_WAITING', 'SIGNAL_REJECTED',
  'ENTRY_TRIGGERED', 'SPREAD_WARNING', 'PENDING_CANCELLED',
  'TP1_HIT', 'TP2_HIT', 'SL_HIT', 'TRADE_CLOSED', 'JOURNAL_UPDATED'
));
