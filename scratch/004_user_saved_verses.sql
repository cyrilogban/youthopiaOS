create table public.user_saved_verses (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.users(id) on delete cascade,
  bot_name text not null,
  reference text not null,
  category text not null,
  saved_at timestamp with time zone not null default now(),
  unique (user_id, bot_name, reference)
);

-- Enable RLS
alter table public.user_saved_verses enable row level security;

-- Create policy
create policy "Users can read their own saved verses"
  on public.user_saved_verses
  for select
  using (true);

create policy "Service role has full access to user_saved_verses"
  on public.user_saved_verses
  for all
  using (true);
