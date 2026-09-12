-- Migration: Add index on telegram_accounts(last_seen_at)
-- Accelerates Monthly Active Users (MAU) and Daily Active Users (DAU) analytics queries.

CREATE INDEX IF NOT EXISTS idx_telegram_accounts_last_seen_at 
ON telegram_accounts (last_seen_at DESC);
