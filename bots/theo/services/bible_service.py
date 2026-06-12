"""Bible structure lookup service.

Queries the Supabase ``bible_translations``, ``bible_books``, and
``bible_chapters`` tables to provide translation listings, book and
chapter metadata, random verse references, and reference validation.

.. note::
   This service does **not** fetch verse text — that responsibility
   belongs to a separate service.
"""

from __future__ import annotations

import asyncio
import random
from dataclasses import dataclass
from typing import Any

from shared.db.supabase import SupabaseGateway


@dataclass(slots=True)
class BibleService:
    """High-level interface for Bible structure lookups.

    Wraps a :class:`SupabaseGateway` instance to query translation,
    book, and chapter tables without returning actual verse text.
    """

    db: SupabaseGateway

    # ------------------------------------------------------------------
    # Translations
    # ------------------------------------------------------------------

    async def get_translations(self) -> list[dict]:
        """Return every available Bible translation.

        Results are ordered by ``language`` then ``name`` so that
        translations for the same language are grouped together.
        """

        def run() -> list[dict]:
            response = (
                self.db._client()
                .table("bible_translations")
                .select("*")
                .order("language")
                .order("name")
                .execute()
            )
            return response.data or []

        return await asyncio.to_thread(run)

    # ------------------------------------------------------------------
    # Books
    # ------------------------------------------------------------------

    async def get_books(self, translation_id: str) -> list[dict]:
        """Return all books belonging to *translation_id*.

        Results are ordered by ``book_order`` (canonical ordering).
        """

        def run() -> list[dict]:
            response = (
                self.db._client()
                .table("bible_books")
                .select("*")
                .eq("translation_id", translation_id)
                .order("book_order")
                .execute()
            )
            return response.data or []

        return await asyncio.to_thread(run)

    # ------------------------------------------------------------------
    # Chapters
    # ------------------------------------------------------------------

    async def get_chapters(
        self, translation_id: str, book_id: str
    ) -> list[dict]:
        """Return all chapters for a given book within a translation.

        Results are ordered by ``chapter_number``.
        """

        def run() -> list[dict]:
            response = (
                self.db._client()
                .table("bible_chapters")
                .select("*")
                .eq("translation_id", translation_id)
                .eq("book_id", book_id)
                .order("chapter_number")
                .execute()
            )
            return response.data or []

        return await asyncio.to_thread(run)

    # ------------------------------------------------------------------
    # Random verse reference
    # ------------------------------------------------------------------

    async def get_random_verse_ref(
        self, translation_id: str = "kjv"
    ) -> dict:
        """Pick a random verse reference from the given translation.

        The method selects a random book, then a random chapter within
        that book, and finally a random verse number between 1 and
        the chapter's ``total_verses`` count.

        Returns a dict with keys ``translation_id``, ``book_id``,
        ``book_name``, ``chapter``, and ``verse``.
        """

        books = await self.get_books(translation_id)
        if not books:
            return {}

        book = random.choice(books)

        chapters = await self.get_chapters(translation_id, book["book_id"])
        if not chapters:
            return {}

        chapter = random.choice(chapters)
        verse = random.randint(1, chapter["total_verses"])

        return {
            "translation_id": translation_id,
            "book_id": book["book_id"],
            "book_name": book["name"],
            "chapter": chapter["chapter_number"],
            "verse": verse,
        }

    # ------------------------------------------------------------------
    # Reference validation
    # ------------------------------------------------------------------

    async def validate_reference(
        self,
        translation_id: str,
        book_id: str,
        chapter: int,
        verse: int,
    ) -> bool:
        """Check whether a Bible reference is valid.

        A reference is considered valid when:

        1. The *book_id* exists under the given *translation_id*.
        2. A chapter row exists for that book with the specified
           *chapter* number.
        3. The *verse* number is between 1 and the chapter's
           ``total_verses`` (inclusive).
        """

        book = await self.db.find_one_multi(
            "bible_books",
            {"translation_id": translation_id, "book_id": book_id},
        )
        if not book:
            return False

        chapter_row = await self.db.find_one_multi(
            "bible_chapters",
            {
                "translation_id": translation_id,
                "book_id": book_id,
                "chapter_number": chapter,
            },
        )
        if not chapter_row:
            return False

        return 1 <= verse <= chapter_row["total_verses"]
