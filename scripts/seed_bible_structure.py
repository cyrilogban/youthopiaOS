"""Seed Bible structure data from bible-api.com into Supabase.

Fetches translations, books, and chapters (with verse counts) from
the public bible-api.com API and upserts everything into the
``bible_translations``, ``bible_books``, and ``bible_chapters`` tables.

Usage (from project root):
    python -m scripts.seed_bible_structure
    python scripts/seed_bible_structure.py
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv
from supabase import create_client, Client


# ---------------------------------------------------------------------------
# Environment setup
# ---------------------------------------------------------------------------

# Resolve the project root so the script works when invoked directly
# (python scripts/seed_bible_structure.py) *and* as a module
# (python -m scripts.seed_bible_structure).
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_ENV_PATH = _PROJECT_ROOT / ".env"

load_dotenv(_ENV_PATH)

SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
BASE_API_URL: str = "https://bible-api.com/data"


# ---------------------------------------------------------------------------
# Rate limiter — 15 requests per 30-second window
# ---------------------------------------------------------------------------

class RateLimiter:
    """Simple sliding-window rate limiter.

    Tracks timestamps of recent requests and sleeps when the
    configured ceiling is reached.
    """

    def __init__(self, max_requests: int = 15, window_seconds: int = 30) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._timestamps: list[float] = []

    def wait(self) -> None:
        """Block until a request slot is available."""
        now = time.time()
        # Purge timestamps outside the current window
        self._timestamps = [
            t for t in self._timestamps
            if now - t < self.window_seconds
        ]
        if len(self._timestamps) >= self.max_requests:
            oldest = self._timestamps[0]
            sleep_for = self.window_seconds - (now - oldest) + 0.1
            if sleep_for > 0:
                print(f"  ⏳ Rate limit reached — sleeping {sleep_for:.1f}s")
                time.sleep(sleep_for)
            # Purge again after sleeping
            now = time.time()
            self._timestamps = [
                t for t in self._timestamps
                if now - t < self.window_seconds
            ]
        self._timestamps.append(time.time())


_limiter = RateLimiter()


# ---------------------------------------------------------------------------
# HTTP helper with retry + backoff
# ---------------------------------------------------------------------------

def fetch_json(url: str, max_retries: int = 3) -> dict | None:
    """GET *url* and return parsed JSON, or ``None`` on persistent failure.

    Retries up to *max_retries* times with exponential backoff.
    """
    for attempt in range(1, max_retries + 1):
        _limiter.wait()
        try:
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as exc:
            wait = 2 ** attempt
            print(f"  ⚠️  HTTP error on {url} (attempt {attempt}/{max_retries}): {exc}")
            if attempt < max_retries:
                print(f"      Retrying in {wait}s …")
                time.sleep(wait)
    print(f"  ❌ Skipping {url} after {max_retries} failed attempts.")
    return None


# ---------------------------------------------------------------------------
# Seed steps
# ---------------------------------------------------------------------------

def seed_translations(client: Client) -> list[dict]:
    """Fetch all translations and upsert into ``bible_translations``.

    Returns the list of translation dicts from the API so downstream
    steps can iterate over them.
    """
    print("\n{'='*60}")
    print("STEP 1 — Fetching translations")
    print("=" * 60)

    data = fetch_json(BASE_API_URL)
    if not data:
        print("  ❌ Could not fetch translations. Aborting.")
        sys.exit(1)

    translations = data.get("translations", [])
    print(f"  Found {len(translations)} translation(s).")

    rows = [
        {
            "id": t["identifier"],
            "name": t["name"],
            "language": t["language"],
            "language_code": t["language_code"],
            "license": t.get("license", "Public Domain"),
        }
        for t in translations
    ]

    if rows:
        client.table("bible_translations").upsert(rows, on_conflict="id").execute()
        print(f"  ✅ Upserted {len(rows)} translation(s).")

    return translations


def seed_books(client: Client, translations: list[dict]) -> list[dict]:
    """For each translation, fetch its books and upsert into ``bible_books``.

    Returns a flat list of ``(translation_id, book_id)`` tuples for
    downstream chapter seeding.
    """
    print("\n" + "=" * 60)
    print("STEP 2 — Fetching books for each translation")
    print("=" * 60)

    all_book_refs: list[dict] = []

    for t_idx, translation in enumerate(translations, 1):
        t_id = translation["identifier"]
        t_name = translation["name"]
        print(f"\n  [{t_idx}/{len(translations)}] {t_name} ({t_id})")

        data = fetch_json(f"{BASE_API_URL}/{t_id}")
        if not data:
            print(f"    ⚠️  Skipped — could not fetch books for {t_id}.")
            continue

        books = data.get("books", [])
        print(f"    Found {len(books)} book(s).")

        rows = []
        for order, book in enumerate(books, 1):
            book_id = book["id"]
            rows.append({
                "translation_id": t_id,
                "book_id": book_id,
                "book_name": book["name"],
                "book_order": order,
            })
            all_book_refs.append({"translation_id": t_id, "book_id": book_id})

        if rows:
            client.table("bible_books").upsert(
                rows, on_conflict="translation_id,book_id"
            ).execute()
            print(f"    ✅ Upserted {len(rows)} book(s).")

    return all_book_refs


def seed_chapters(
    client: Client,
    book_refs: list[dict],
    translations: list[dict],
) -> None:
    """For each book, fetch its chapters; for each chapter, count verses.

    Upserts results into ``bible_chapters``.
    """
    print("\n" + "=" * 60)
    print("STEP 3 — Fetching chapters & verse counts")
    print("=" * 60)

    total_books = len(book_refs)

    # Build a quick translation-name lookup for nicer logging
    t_names: dict[str, str] = {
        t["identifier"]: t["name"] for t in translations
    }

    for b_idx, ref in enumerate(book_refs, 1):
        t_id = ref["translation_id"]
        book_id = ref["book_id"]
        pct = (b_idx / total_books) * 100
        print(
            f"\n  [{b_idx}/{total_books}] ({pct:5.1f}%) "
            f"{t_names.get(t_id, t_id)} / {book_id}"
        )

        # --- Fetch chapter list for this book ---
        chap_data = fetch_json(f"{BASE_API_URL}/{t_id}/{book_id}")
        if not chap_data:
            print(f"    ⚠️  Skipped — could not fetch chapters.")
            continue

        chapters = chap_data.get("chapters", [])
        print(f"    {len(chapters)} chapter(s) found.")

        rows: list[dict] = []
        for ch in chapters:
            ch_num = ch["chapter"]

            # --- Fetch verses for this chapter to get total_verses ---
            verse_data = fetch_json(f"{BASE_API_URL}/{t_id}/{book_id}/{ch_num}")
            if not verse_data:
                print(f"    ⚠️  Could not fetch verses for chapter {ch_num} — skipping.")
                continue

            verses = verse_data.get("verses", [])
            total_verses = len(verses)

            rows.append({
                "translation_id": t_id,
                "book_id": book_id,
                "chapter_number": ch_num,
                "total_verses": total_verses,
            })

        if rows:
            client.table("bible_chapters").upsert(
                rows, on_conflict="translation_id,book_id,chapter_number"
            ).execute()
            print(f"    ✅ Upserted {len(rows)} chapter(s).")


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Run the full Bible-structure seed pipeline."""
    print("🔧 Bible Structure Seed Script")
    print(f"   Supabase URL : {SUPABASE_URL[:40]}…" if len(SUPABASE_URL) > 40 else f"   Supabase URL : {SUPABASE_URL}")

    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ SUPABASE_URL and SUPABASE_KEY must be set in .env")
        sys.exit(1)

    client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("   ✅ Supabase client connected.\n")

    start = time.time()

    # Step 1
    translations = seed_translations(client)

    # Step 2
    book_refs = seed_books(client, translations)

    # Step 3
    seed_chapters(client, book_refs, translations)

    elapsed = time.time() - start
    minutes, seconds = divmod(int(elapsed), 60)
    print("\n" + "=" * 60)
    print(f"🎉 Seed complete!  ({minutes}m {seconds}s elapsed)")
    print("=" * 60)


if __name__ == "__main__":
    main()
