-- Table for scheduling the daily Verse of the Day (VOTD)
-- Note: We only store the reference (e.g., "John 3:16"). 
-- The bot dynamically fetches the text from a Bible API in the user's preferred translation.

create table if not exists verse_of_the_day (
    id serial primary key,
    scheduled_date date not null unique,
    reference text not null,
    created_at timestamptz not null default now()
);

-- Index for fast lookup by date
create index if not exists idx_votd_date on verse_of_the_day(scheduled_date);
