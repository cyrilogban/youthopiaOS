-- Rank system (Decision 7): holistic rank_score + rank_definitions.
-- rank_score is the cross-bot engagement score (0..unbounded) that maps to a
-- YouTopian rank. Elite & Ambassador remain founder-appointed (manual_rank_id).

create table if not exists public.rank_definitions (
    id uuid primary key default gen_random_uuid(),
    rank_id text not null unique,
    rank_name text not null,
    tier text not null,
    min_score integer not null,
    max_score integer,
    color_code text not null,
    emoji text not null,
    description text,
    requires_manual_approval boolean not null default false,
    sort_order integer not null default 0,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

insert into public.rank_definitions (
    rank_id, rank_name, tier, min_score, max_score,
    color_code, emoji, description, requires_manual_approval, sort_order
)
values
    ('seeker',       'YouTopian Seeker',       'Entry Level',         0,    100,  '#D98A95', '🌸', 'A new soul exploring the community.',                              false, 1),
    ('gathered_one', 'YouTopian Gathered One', 'Entry Level',         101,  250,  '#D2B48C', '🌾', 'A verified member welcomed into the fold.',                        false, 2),
    ('spark',        'YouTopian Spark',        'Active Contributors', 251,  500,  '#88C9E8', '⚡', 'Active participant showing initial dedication.',                   false, 3),
    ('luminary',     'YouTopian Luminary',     'Active Contributors', 501,  800,  '#85D6A5', '💡', 'A shining light, active in Scripture quizzes & daily study.',      false, 4),
    ('witness',      'YouTopian Witness',      'Active Contributors', 801,  1200, '#B8CB80', '📜', 'A seasoned scripture master who exemplifies faith in action.',     false, 5),
    ('refiner',      'YouTopian Refiner',      'Mentors & Builders',  1201, 1700, '#B0A8E8', '🔨', 'Mentoring newer members and refining the community.',              false, 6),
    ('pillar',       'YouTopian Pillar',       'Mentors & Builders',  1701, 2300, '#D4628E', '🏛️', 'A foundational rock anchoring community discussions.',             false, 7),
    ('elite',        'YouTopian Elite',        'Core Leadership',     2301, 3000, '#8EA5D0', '👑', 'Core community leadership, moderators, and coordinators.',         true,  8),
    ('ambassador',   'YouTopian Ambassador',   'Core Leadership',     3001, null, '#B88B97', '🌍', 'Global visionary and community director.',                         true,  9)
on conflict (rank_id) do update set
    rank_name = excluded.rank_name,
    tier = excluded.tier,
    min_score = excluded.min_score,
    max_score = excluded.max_score,
    color_code = excluded.color_code,
    emoji = excluded.emoji,
    description = excluded.description,
    requires_manual_approval = excluded.requires_manual_approval,
    sort_order = excluded.sort_order,
    updated_at = now();

alter table public.rank_definitions enable row level security;

do $$
begin
    if not exists (
        select 1 from pg_policies
        where schemaname = 'public' and tablename = 'rank_definitions'
          and policyname = 'Anyone can read rank definitions'
    ) then
        create policy "Anyone can read rank definitions"
            on public.rank_definitions
            for select
            using (true);
    end if;

    if not exists (
        select 1 from pg_policies
        where schemaname = 'public' and tablename = 'rank_definitions'
          and policyname = 'Service role has full access to rank definitions'
    ) then
        create policy "Service role has full access to rank definitions"
            on public.rank_definitions
            for all
            using (true);
    end if;
end
$$;

-- Store the computed score + resolved rank on the user row.
-- manual_rank_id was previously created ad hoc; declare it here for reproducibility.
alter table public.users add column if not exists manual_rank_id text;
alter table public.users add column if not exists rank_score integer not null default 0;
alter table public.users add column if not exists rank_id text;
alter table public.users add column if not exists rank_title text;
alter table public.users add column if not exists rank_tier text;
alter table public.users add column if not exists rank_badge_color text;
alter table public.users add column if not exists rank_emoji text;
alter table public.users add column if not exists rank_updated_at timestamptz;
alter table public.users add column if not exists reading_streak integer not null default 0;

create index if not exists idx_users_rank_score on public.users (rank_score desc);
