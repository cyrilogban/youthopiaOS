from dataclasses import dataclass


@dataclass(frozen=True)
class Track:
    title: str
    file_path: str
    duration: int
    source_url: str | None = None
    thumbnail_url: str | None = None


@dataclass(frozen=True)
class MusicResult:
    message: str
    track: Track | None = None
