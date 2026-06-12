-- Bible structure tables for storing translation, book, and chapter metadata.
-- No verse text is stored here — only structural reference data.

create table if not exists bible_translations (
    id text primary key,
    name text not null,
    language text not null,
    language_code text not null,
    license text not null default 'Public Domain',
    created_at timestamptz not null default now()
);

create table if not exists bible_books (
    id serial primary key,
    translation_id text not null references bible_translations(id) on delete cascade,
    book_id text not null,
    book_name text not null,
    book_order integer not null,
    created_at timestamptz not null default now(),
    unique (translation_id, book_id)
);

create table if not exists bible_chapters (
    id serial primary key,
    translation_id text not null references bible_translations(id) on delete cascade,
    book_id text not null,
    chapter_number integer not null,
    total_verses integer not null,
    created_at timestamptz not null default now(),
    unique (translation_id, book_id, chapter_number),
    foreign key (translation_id, book_id) references bible_books(translation_id, book_id) on delete cascade
);

create index if not exists idx_bible_books_translation on bible_books(translation_id);
create index if not exists idx_bible_chapters_translation_book on bible_chapters(translation_id, book_id);
