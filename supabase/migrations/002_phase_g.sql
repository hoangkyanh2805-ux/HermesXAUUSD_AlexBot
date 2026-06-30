-- Phase G migration — correlation_data + CORRELATION_RISK event

alter table signals add column if not exists correlation_data jsonb;

alter table activity_logs drop constraint if exists activity_logs_event_type_check;
alter table activity_logs add constraint activity_logs_event_type_check check (event_type in (
  'SIGNAL_CREATED', 'SIGNAL_CHECKED', 'CORRELATION_RISK', 'SIGNAL_SEEDED', 'SIGNAL_PUBLISHED',
  'LOT_CALCULATED', 'SIGNAL_APPROVED', 'SIGNAL_WAITING', 'SIGNAL_REJECTED',
  'ENTRY_TRIGGERED', 'SPREAD_WARNING', 'PENDING_CANCELLED',
  'TP1_HIT', 'TP2_HIT', 'SL_HIT', 'TRADE_CLOSED', 'JOURNAL_UPDATED'
));
