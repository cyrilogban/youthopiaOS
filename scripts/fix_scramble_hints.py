"""Fix existing Verse Scramble questions in Supabase by stripping the
reference hint that was accidentally embedded in the question text.

e.g.  "world only begotten For loved God... (John 3:16)"
  ->  "world only begotten For loved God..."

Usage:
    python scripts/fix_scramble_hints.py
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_PROJECT_ROOT / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# Matches a trailing " (BookName 1:2)" or " (BookName 1:2-3)" hint
_HINT_RE = re.compile(r"\s*\([^)]+\d+:\d[^)]*\)\s*$")


def strip_hint(text: str) -> str:
    return _HINT_RE.sub("", text).strip()


def fix_questions():
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Error: SUPABASE_URL and SUPABASE_KEY must be set in your .env file.")
        return

    print("Initializing Supabase client...")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Fetch all verse_completion questions
    print("Fetching verse_completion questions...")
    response = supabase.table("lusy_questions").select("id, content").eq("game_type", "verse_completion").execute()
    rows = response.data or []
    print(f"Found {len(rows)} verse_completion questions.")

    fixed = 0
    skipped = 0

    for row in rows:
        q_id = row["id"]
        content = row.get("content", {})
        original_text = content.get("text", "")
        cleaned_text = strip_hint(original_text)

        if cleaned_text == original_text:
            skipped += 1
            continue

        # Patch only the text field inside content JSONB
        new_content = {**content, "text": cleaned_text}
        try:
            supabase.table("lusy_questions").update({"content": new_content}).eq("id", q_id).execute()
            print(f"  Fixed [{q_id[:8]}...]: '{original_text[:60]}...' -> '{cleaned_text[:60]}'")
            fixed += 1
        except Exception as e:
            print(f"  ERROR updating {q_id}: {e}")

    print(f"\nDone. Fixed: {fixed} | Already clean: {skipped}")


if __name__ == "__main__":
    fix_questions()
