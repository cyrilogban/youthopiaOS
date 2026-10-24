-- Migration: 008_theo_bible_feed.sql
-- Description: Creates featured_verses, saved_verses, and likes tables for Theo Bible Feed feature

CREATE TABLE IF NOT EXISTS public.featured_verses (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  verse_reference TEXT NOT NULL,
  verse_text TEXT NOT NULL,
  translation TEXT NOT NULL DEFAULT 'KJV',
  scheduled_date DATE NOT NULL,
  is_active BOOLEAN DEFAULT true,
  style_override INTEGER DEFAULT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.saved_verses (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES public.telegram_accounts(telegram_id) ON DELETE CASCADE,
  verse_reference TEXT NOT NULL,
  verse_text TEXT NOT NULL,
  translation TEXT NOT NULL DEFAULT 'KJV',
  saved_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.likes (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES public.telegram_accounts(telegram_id) ON DELETE CASCADE,
  verse_reference TEXT NOT NULL,
  liked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(user_id, verse_reference)
);

-- Enable Row Level Security (RLS)
ALTER TABLE public.featured_verses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.saved_verses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.likes ENABLE ROW LEVEL SECURITY;

-- Permissive policy for read access if needed by client or service_role
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'featured_verses' AND policyname = 'Anyone can read active featured verses'
    ) THEN
        CREATE POLICY "Anyone can read active featured verses"
            ON public.featured_verses FOR SELECT USING (is_active = true);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'saved_verses' AND policyname = 'Users can access their own saved verses'
    ) THEN
        CREATE POLICY "Users can access their own saved verses"
            ON public.saved_verses FOR ALL USING (true);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'likes' AND policyname = 'Users can access likes'
    ) THEN
        CREATE POLICY "Users can access likes"
            ON public.likes FOR ALL USING (true);
    END IF;
END
$$;
