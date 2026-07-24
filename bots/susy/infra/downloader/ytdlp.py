import asyncio
from pathlib import Path
from uuid import uuid4

import yt_dlp
from yt_dlp.utils import DownloadError

from bots.susy.core.music.errors import DownloadFailedError
from bots.susy.core.music.models import Track


class YtDlpDownloader:
    """Downloads audio from a search query or URL using yt-dlp."""

    def __init__(
        self,
        download_dir: str,
        retries: int = 3,
        socket_timeout: int = 30,
        extractor_retries: int = 2,
        js_runtimes: str | None = None,
        cookiefile: str | None = None,
    ) -> None:
        self._download_dir = Path(download_dir)
        self._download_dir.mkdir(parents=True, exist_ok=True)
        self._retries = retries
        self._socket_timeout = socket_timeout
        self._extractor_retries = extractor_retries
        self._js_runtimes = js_runtimes
        
        self._cookiefile = None
        if cookiefile:
            c_path = Path(cookiefile)
            if c_path.exists():
                writable_path = self._download_dir / "youtube_cookies_writable.txt"
                try:
                    import shutil
                    shutil.copy2(c_path, writable_path)
                    self._cookiefile = str(writable_path)
                except Exception as e:
                    print(f"FAILED TO COPY COOKIEFILE TO WRITABLE PATH: {e}")
                    self._cookiefile = cookiefile
            else:
                self._cookiefile = cookiefile

    async def download(self, query: str) -> Track:
        return await asyncio.to_thread(self._download_sync, query)

    def _download_sync(self, query: str) -> Track:
        request = query if _looks_like_url(query) else f"ytsearch1:{query}"
        output_stem = self._download_dir / f"{uuid4()}"

        options = {
            "format": "bestaudio/best",
            "outtmpl": f"{output_stem}.%(ext)s",
            "quiet": True,
            "noplaylist": True,
            "default_search": "ytsearch",
            "retries": self._retries,
            "socket_timeout": self._socket_timeout,
            "extractor_retries": self._extractor_retries,
            "extractor_args": {"youtube": ["player_client=ios,android"]},
        }
        if self._cookiefile:
            options["cookiefile"] = self._cookiefile

        try:
            with yt_dlp.YoutubeDL(options) as downloader:
                info = downloader.extract_info(request, download=True)
        except DownloadError as error:
            print(f"YTDLP DOWNLOAD ERROR: {str(error)}")
            raise DownloadFailedError(reason=str(error)) from error
        except Exception as error:
            print(f"YTDLP UNKNOWN ERROR: {str(error)}")
            raise DownloadFailedError(reason=str(error)) from error

        if "entries" in info:
            info = info["entries"][0]

        file_path = Path(downloader.prepare_filename(info))
        return Track(
            title=info.get("title") or query,
            file_path=str(file_path),
            duration=int(info.get("duration") or 0),
            source_url=info.get("webpage_url"),
            thumbnail_url=info.get("thumbnail"),
        )


def _looks_like_url(query: str) -> bool:
    return query.startswith(("http://", "https://"))


def _map_download_error(message: str) -> str:
    normalized = message.lower()
    if "timed out" in normalized or "timeout" in normalized:
        return "timeout"
    if "unavailable" in normalized or "private" in normalized or "forbidden" in normalized:
        return "source_unavailable"
    return "unknown"
