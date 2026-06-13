"""Bible scripture reference detection.

Provides regex-based detection of Bible references in arbitrary text.
Supports all 66 books with common aliases and abbreviations, verse
ranges, and case-insensitive matching.
"""

from __future__ import annotations

from dataclasses import dataclass
import re


BOOK_ALIASES: dict[str, tuple[str, ...]] = {
    "Genesis": ("genesis", "gen"),
    "Exodus": ("exodus", "exod", "exo"),
    "Leviticus": ("leviticus", "lev"),
    "Numbers": ("numbers", "num"),
    "Deuteronomy": ("deuteronomy", "deut", "deu"),
    "Joshua": ("joshua", "josh"),
    "Judges": ("judges", "judg", "jdg"),
    "Ruth": ("ruth", "rth"),
    "1 Samuel": ("1 samuel", "1 sam", "1sam", "i samuel", "i sam"),
    "2 Samuel": ("2 samuel", "2 sam", "2sam", "ii samuel", "ii sam"),
    "1 Kings": ("1 kings", "1 king", "1 kgs", "1kgs", "1 kin", "1kin", "i kings", "i king"),
    "2 Kings": ("2 kings", "2 king", "2 kgs", "2kgs", "2 kin", "2kin", "ii kings", "ii king"),
    "1 Chronicles": ("1 chronicles", "1 chron", "1chr", "1 chr", "i chronicles", "i chron"),
    "2 Chronicles": ("2 chronicles", "2 chron", "2chr", "2 chr", "ii chronicles", "ii chron"),
    "Ezra": ("ezra", "ezr"),
    "Nehemiah": ("nehemiah", "neh"),
    "Esther": ("esther", "esth", "est"),
    "Job": ("job",),
    "Psalm": ("psalm", "psalms", "ps"),
    "Proverbs": ("proverbs", "proverb", "prov", "prv"),
    "Ecclesiastes": ("ecclesiastes", "eccles", "eccl", "ecc"),
    "Song of Solomon": (
        "song of solomon",
        "song of songs",
        "song",
        "sos",
        "canticles",
    ),
    "Isaiah": ("isaiah", "isa"),
    "Jeremiah": ("jeremiah", "jer"),
    "Lamentations": ("lamentations", "lam"),
    "Ezekiel": ("ezekiel", "ezek", "ezk"),
    "Daniel": ("daniel", "dan"),
    "Hosea": ("hosea", "hos"),
    "Joel": ("joel",),
    "Amos": ("amos",),
    "Obadiah": ("obadiah", "obad"),
    "Jonah": ("jonah",),
    "Micah": ("micah", "mic"),
    "Nahum": ("nahum", "nah"),
    "Habakkuk": ("habakkuk", "hab"),
    "Zephaniah": ("zephaniah", "zeph"),
    "Haggai": ("haggai", "hag"),
    "Zechariah": ("zechariah", "zech"),
    "Malachi": ("malachi", "mal"),
    "Matthew": ("matthew", "matt", "mat"),
    "Mark": ("mark", "mrk", "mk"),
    "Luke": ("luke", "luk", "lk"),
    "John": ("john", "jhn", "jn"),
    "Acts": ("acts", "act"),
    "Romans": ("romans", "rom"),
    "1 Corinthians": (
        "1 corinthians",
        "1 cor",
        "1cor",
        "1 corin",
        "i corinthians",
        "i cor",
    ),
    "2 Corinthians": (
        "2 corinthians",
        "2 cor",
        "2cor",
        "2 corin",
        "ii corinthians",
        "ii cor",
    ),
    "Galatians": ("galatians", "gal"),
    "Ephesians": ("ephesians", "eph"),
    "Philippians": ("philippians", "phil", "php"),
    "Colossians": ("colossians", "col"),
    "1 Thessalonians": (
        "1 thessalonians",
        "1 thess",
        "1thess",
        "1 thes",
        "i thessalonians",
        "i thess",
    ),
    "2 Thessalonians": (
        "2 thessalonians",
        "2 thess",
        "2thess",
        "2 thes",
        "ii thessalonians",
        "ii thess",
    ),
    "1 Timothy": ("1 timothy", "1 tim", "1tim", "i timothy", "i tim"),
    "2 Timothy": ("2 timothy", "2 tim", "2tim", "ii timothy", "ii tim"),
    "Titus": ("titus", "tit"),
    "Philemon": ("philemon", "phlm", "phm"),
    "Hebrews": ("hebrews", "heb"),
    "James": ("james", "jas", "jam"),
    "1 Peter": ("1 peter", "1 pet", "1pet", "i peter", "i pet"),
    "2 Peter": ("2 peter", "2 pet", "2pet", "ii peter", "ii pet"),
    "1 John": ("1 john", "1 jn", "1jn", "i john", "i jn"),
    "2 John": ("2 john", "2 jn", "2jn", "ii john", "ii jn"),
    "3 John": ("3 john", "3 jn", "3jn", "iii john", "iii jn"),
    "Jude": ("jude", "jud"),
    "Revelation": ("revelation", "rev", "revelations"),
}


@dataclass(frozen=True)
class DetectedReference:
    """A single detected Bible reference with book, chapter, and verse info."""

    book: str
    chapter: int
    verse_start: int
    verse_end: int | None = None
    matched_text: str = ""

    @property
    def is_range(self) -> bool:
        return self.verse_end is not None

    @property
    def reference(self) -> str:
        if self.verse_end is None:
            return f"{self.book} {self.chapter}:{self.verse_start}"
        return f"{self.book} {self.chapter}:{self.verse_start}-{self.verse_end}"


# ---------------------------------------------------------------------------
# Alias lookup table
# ---------------------------------------------------------------------------

def _normalize_alias(alias: str) -> str:
    normalized = alias.casefold()
    normalized = normalized.replace(".", "")
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def _build_book_alias_lookup() -> dict[str, str]:
    lookup: dict[str, str] = {}

    for canonical_book, aliases in BOOK_ALIASES.items():
        raw_aliases = {canonical_book, *aliases}

        for raw_alias in raw_aliases:
            normalized_alias = _normalize_alias(raw_alias)
            if not normalized_alias:
                continue

            lookup.setdefault(normalized_alias, canonical_book)

            compact_alias = normalized_alias.replace(" ", "")
            lookup.setdefault(compact_alias, canonical_book)

    return lookup


BOOK_ALIAS_LOOKUP = _build_book_alias_lookup()

# ---------------------------------------------------------------------------
# Compiled regex — aliases sorted longest-first to prevent partial matches
# ---------------------------------------------------------------------------

BOOK_PATTERN = "|".join(
    re.escape(alias)
    for alias in sorted(BOOK_ALIAS_LOOKUP.keys(), key=lambda value: (-len(value), value))
)

SCRIPTURE_REFERENCE_PATTERN = re.compile(
    rf"""
    (?<![a-z0-9])
    (?P<book>{BOOK_PATTERN})
    \s*
    (?P<chapter>\d{{1,3}})
    \s*
    :
    \s*
    (?P<verse_start>\d{{1,3}})
    (?:
        \s*-\s*
        (?P<verse_end>\d{{1,3}})
    )?
    (?!\d)
    """,
    re.IGNORECASE | re.VERBOSE,
)


# ---------------------------------------------------------------------------
# Text normalization
# ---------------------------------------------------------------------------

def normalize_reference_text(text: str) -> str:
    """Normalize user input so the regex can match flexibly."""
    normalized = text.casefold()
    normalized = normalized.replace("\u2013", "-")
    normalized = normalized.replace("\u2014", "-")
    normalized = normalized.replace("\u2212", "-")
    normalized = normalized.replace("\ufffd", "'")
    normalized = normalized.replace("`", "'")
    normalized = normalized.replace(".", "")
    normalized = re.sub(r"[\(\)\[\]\{\},;!?]", " ", normalized)
    normalized = re.sub(r"(?<=\d)\s*(?:verses?|vs?|:)\s*(?=\d)", ":", normalized)
    normalized = re.sub(r"(?<=\d)\s*-\s*(?=\d)", "-", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def should_detect_scripture_references(text: str) -> bool:
    """Quick pre-check: is this text worth scanning?"""
    normalized_text = normalize_reference_text(text)
    return bool(normalized_text) and not normalized_text.startswith("/")


def find_scripture_references(text: str) -> tuple[DetectedReference, ...]:
    """Return all unique Bible references found in *text*."""
    normalized_text = normalize_reference_text(text)
    if not normalized_text or normalized_text.startswith("/"):
        return ()

    detected_references: list[DetectedReference] = []
    seen_references: set[str] = set()

    for match in SCRIPTURE_REFERENCE_PATTERN.finditer(normalized_text):
        book_alias = _normalize_alias(match.group("book"))
        canonical_book = BOOK_ALIAS_LOOKUP.get(book_alias)
        if canonical_book is None:
            continue

        chapter = int(match.group("chapter"))
        verse_start = int(match.group("verse_start"))
        verse_end_value = match.group("verse_end")
        verse_end = int(verse_end_value) if verse_end_value is not None else None

        if verse_end is not None and verse_end < verse_start:
            continue

        detected_reference = DetectedReference(
            book=canonical_book,
            chapter=chapter,
            verse_start=verse_start,
            verse_end=verse_end,
            matched_text=match.group(0),
        )

        if detected_reference.reference in seen_references:
            continue

        seen_references.add(detected_reference.reference)
        detected_references.append(detected_reference)

    return tuple(detected_references)


def find_reference_strings(text: str) -> tuple[str, ...]:
    """Convenience wrapper — returns just the formatted reference strings."""
    return tuple(reference.reference for reference in find_scripture_references(text))
