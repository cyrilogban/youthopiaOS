-- Migration for Lusy's Universal Game Engine

-- 1. Create the questions table
create table if not exists lusy_questions (
    id uuid primary key default gen_random_uuid(),
    game_type text not null check (game_type in ('multiple_choice', 'verse_completion', 'emoji_puzzle', 'true_false', 'fill_in_the_blank')),
    category text not null,
    difficulty text not null check (difficulty in ('easy', 'medium', 'hard', 'expert')),
    content jsonb not null default '{}'::jsonb,
    correct_answer text not null,
    explanation text,
    base_xp integer not null default 10,
    created_at timestamptz not null default now(),
    is_active boolean not null default true
);

-- 2. Create the game history table to track results and prevent repeats
create table if not exists lusy_game_history (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references users(id) on delete cascade,
    question_id uuid not null references lusy_questions(id) on delete cascade,
    is_correct boolean not null,
    xp_earned integer not null default 0,
    answered_at timestamptz not null default now()
);

-- 3. Add Indexes for fast querying
create index if not exists idx_lusy_questions_type_diff on lusy_questions(game_type, difficulty);
create index if not exists idx_lusy_questions_category on lusy_questions(category);
create index if not exists idx_lusy_game_history_user on lusy_game_history(user_id);
create index if not exists idx_lusy_game_history_question on lusy_game_history(question_id);

-- 4. Enable Row Level Security (RLS)
alter table lusy_questions enable row level security;
alter table lusy_game_history enable row level security;

-- Only authenticated services (our bots) can access these tables natively right now.
-- In Supabase, if the Python SDK connects with a service_role key, it bypasses RLS automatically.
