-- YouThopiaOS unified Supabase schema.
-- Supabase is authoritative for identity, XP, roles, moderation, events, and cross-bot state.
-- MongoDB is intentionally excluded from this schema and is reserved for telemetry only.

create extension if not exists pgcrypto;

create table if not exists users (
    id uuid primary key default gen_random_uuid(),
    display_name text,
    engagement_level text not null default 'new',
    trust_score integer not null default 100 check (trust_score >= 0 and trust_score <= 100),
    total_xp integer not null default 0 check (total_xp >= 0),
    level integer not null default 1 check (level >= 1),
    is_active boolean not null default true,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists telegram_accounts (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references users(id) on delete cascade,
    telegram_id bigint not null unique,
    username text,
    first_name text,
    last_name text,
    is_bot boolean not null default false,
    first_seen_at timestamptz not null default now(),
    last_seen_at timestamptz not null default now()
);

create table if not exists telegram_chats (
    id uuid primary key default gen_random_uuid(),
    telegram_chat_id bigint not null unique,
    chat_type text not null,
    title text,
    username text,
    is_active boolean not null default true,
    is_official boolean not null default false,
    first_seen_at timestamptz not null default now(),
    last_seen_at timestamptz not null default now(),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists bot_chat_memberships (
    id uuid primary key default gen_random_uuid(),
    chat_id uuid not null references telegram_chats(id) on delete cascade,
    bot_name text not null check (bot_name in ('theo', 'lusy', 'pete', 'eddy', 'susy')),
    status text not null default 'active' check (status in ('active', 'left', 'kicked', 'disabled')),
    enabled boolean not null default true,
    joined_at timestamptz not null default now(),
    left_at timestamptz,
    last_seen_at timestamptz not null default now(),
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique (chat_id, bot_name)
);

create table if not exists chat_bot_settings (
    id uuid primary key default gen_random_uuid(),
    chat_id uuid not null references telegram_chats(id) on delete cascade,
    bot_name text not null check (bot_name in ('theo', 'lusy', 'pete', 'eddy', 'susy')),
    settings jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique (chat_id, bot_name)
);

create table if not exists chat_subscriptions (
    id uuid primary key default gen_random_uuid(),
    chat_id uuid not null references telegram_chats(id) on delete cascade,
    bot_name text not null check (bot_name in ('theo', 'lusy', 'pete', 'eddy', 'susy')),
    subscription_type text not null,
    enabled boolean not null default true,
    schedule text,
    timezone text not null default 'UTC',
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique (chat_id, bot_name, subscription_type)
);

create table if not exists user_subscriptions (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references users(id) on delete cascade,
    bot_name text not null check (bot_name in ('theo', 'lusy', 'pete', 'eddy', 'susy')),
    subscription_type text not null,
    enabled boolean not null default true,
    schedule text,
    timezone text not null default 'UTC',
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique (user_id, bot_name, subscription_type)
);

create table if not exists roles (
    id uuid primary key default gen_random_uuid(),
    name text not null unique,
    description text,
    scope text not null default 'global' check (scope in ('global', 'chat')),
    created_at timestamptz not null default now()
);

create table if not exists permissions (
    id uuid primary key default gen_random_uuid(),
    code text not null unique,
    description text,
    created_at timestamptz not null default now()
);

create table if not exists role_permissions (
    role_id uuid not null references roles(id) on delete cascade,
    permission_id uuid not null references permissions(id) on delete cascade,
    primary key (role_id, permission_id)
);

create table if not exists chat_memberships (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references users(id) on delete cascade,
    chat_id uuid not null references telegram_chats(id) on delete cascade,
    role_id uuid references roles(id) on delete set null,
    status text not null default 'active',
    joined_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique (user_id, chat_id)
);

create table if not exists xp_transactions (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references users(id) on delete cascade,
    bot_name text not null,
    source text not null,
    amount integer not null,
    idempotency_key text unique,
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);

create table if not exists user_levels (
    user_id uuid primary key references users(id) on delete cascade,
    total_xp integer not null default 0 check (total_xp >= 0),
    level integer not null default 1 check (level >= 1),
    updated_at timestamptz not null default now()
);

create table if not exists moderation_actions (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references users(id) on delete cascade,
    chat_id uuid references telegram_chats(id) on delete set null,
    moderator_user_id uuid references users(id) on delete set null,
    action_type text not null,
    reason text,
    trust_delta integer not null default 0,
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);

create table if not exists events (
    id uuid primary key default gen_random_uuid(),
    title text not null,
    description text,
    starts_at timestamptz not null,
    ends_at timestamptz,
    location text,
    created_by_user_id uuid references users(id) on delete set null,
    status text not null default 'scheduled',
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists event_participants (
    id uuid primary key default gen_random_uuid(),
    event_id uuid not null references events(id) on delete cascade,
    user_id uuid not null references users(id) on delete cascade,
    status text not null default 'registered',
    attended_at timestamptz,
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique (event_id, user_id)
);

create table if not exists bot_user_state (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references users(id) on delete cascade,
    bot_name text not null,
    state jsonb not null default '{}'::jsonb,
    updated_at timestamptz not null default now(),
    unique (user_id, bot_name)
);

create table if not exists analytics_events (
    id uuid primary key default gen_random_uuid(),
    user_id uuid references users(id) on delete set null,
    bot_name text,
    event_name text not null,
    properties jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);

create index if not exists idx_telegram_accounts_user_id on telegram_accounts(user_id);
create index if not exists idx_telegram_chats_telegram_chat_id on telegram_chats(telegram_chat_id);
create index if not exists idx_bot_chat_memberships_bot_name on bot_chat_memberships(bot_name);
create index if not exists idx_chat_bot_settings_bot_name on chat_bot_settings(bot_name);
create index if not exists idx_chat_subscriptions_bot_type on chat_subscriptions(bot_name, subscription_type);
create index if not exists idx_user_subscriptions_bot_type on user_subscriptions(bot_name, subscription_type);
create index if not exists idx_chat_memberships_user_id on chat_memberships(user_id);
create index if not exists idx_xp_transactions_user_id on xp_transactions(user_id);
create index if not exists idx_moderation_actions_user_id on moderation_actions(user_id);
create index if not exists idx_event_participants_user_id on event_participants(user_id);
